#!/usr/bin/env python3
"""dyspositif — outillage de la skill.

    python scripts/dys.py profil
    python scripts/dys.py questions --difficultes ligne,chiffres
    python scripts/dys.py analyser cours.docx
    python scripts/dys.py appliquer cours.docx sortie.docx --pages 1
    python scripts/dys.py apercu sortie.docx
    python scripts/dys.py verifier sortie.docx --original cours.docx

Chaque commande fait une chose et s'arrête : le parcours en six étapes de
SKILL.md décide de l'enchaînement, pas ce fichier.
"""

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))

from dyslib import (  # noqa: E402
    analyse,
    annotations,
    controle,
    forme,
    listes,
    ooxml,
    paquet,
    profil as module_profil,
    suivi,
    tableaux,
    texte as module_texte,
)

SKILL = RACINE.parent
AUTEUR = "dyspositif"
CARACTERES_PAR_PAGE = 1800


# -- profil ----------------------------------------------------------------


def commande_profil(args):
    if args.oublier:
        print("Profil supprimé." if module_profil.oublier() else "Aucun profil à supprimer.")
        return 0

    profil = module_profil.charger()

    if args.reponses:
        with open(args.reponses, encoding="utf-8") as f:
            reponses = json.load(f)
        profil = module_profil.depuis_reponses(reponses, base=profil)
    if args.definir:
        profil = module_profil.appliquer_definitions(profil or dict(module_profil.DEFAUTS), args.definir)

    if args.reponses or args.definir:
        chemin = module_profil.enregistrer(profil)
        print("Profil enregistré : %s" % chemin)

    if profil is None:
        print("Aucun profil enregistré. (%s)" % module_profil.emplacement())
        return 1 if args.json else 0

    if args.json:
        print(json.dumps(profil, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(module_profil.resume(profil))
        print("Fichier : %s" % module_profil.emplacement())
    return 0


# -- questionnaire ---------------------------------------------------------


def commande_questions(args):
    chemin = SKILL / "references" / "questionnaire.json"
    with open(chemin, encoding="utf-8") as f:
        questionnaire = json.load(f)

    difficultes = [d for d in (args.difficultes or "").split(",") if d]
    for trouble in [t for t in (args.troubles or "").split(",") if t]:
        for difficulte in module_profil.TROUBLE_VERS_DIFFICULTES.get(trouble, []):
            if difficulte not in difficultes:
                difficultes.append(difficulte)

    questions = list(questionnaire["socle"]) if not difficultes else []
    if difficultes:
        for branche in module_profil.branches_a_poser(difficultes):
            questions += questionnaire["branches"].get(branche, [])
        questions += questionnaire["final"]
    else:
        questions += questionnaire["final"]

    presentation = dict(questionnaire["presentation"]["defaut"])
    for difficulte in difficultes:
        presentation.update(
            questionnaire["presentation"]["selon_difficulte"].get(difficulte, {})
        )

    groupes = [questions[i: i + 3] for i in range(0, len(questions), 3)]
    sortie = {
        "total": len(questions),
        "annonce": questionnaire["annonce"],
        "presentation": presentation,
        "groupes": groupes,
        "branches_ouvertes": module_profil.branches_a_poser(difficultes),
    }
    if presentation.get("progression") == "points":
        sortie["progression"] = [
            "●" * (i + 1) + "○" * (len(groupes) - i - 1) for i in range(len(groupes))
        ]
    print(json.dumps(sortie, ensure_ascii=False, indent=2))
    return 0


# -- analyse ---------------------------------------------------------------


def commande_analyser(args):
    chemin = Path(args.fichier)
    if chemin.suffix.lower() == ".pdf":
        rapport = analyse.analyser_pdf(chemin)
        if args.json:
            print(json.dumps(rapport, ensure_ascii=False, indent=2))
        else:
            print(rapport["resume"])
            if not rapport["texte_extractible"]:
                print(
                    "Conversion inutile en l'état : il n'y a pas de texte à adapter, "
                    "seulement des images de pages."
                )
            else:
                print("Convertir en .docx avant d'adapter.")
        return 0 if rapport.get("texte_extractible") else 4

    rapport = analyse.analyser_docx(chemin)
    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
    else:
        print(rapport["resume"])
    return 0


def commande_listes(args):
    with paquet.DossierTemporaire() as dossier:
        paquet.ouvrir(args.fichier, dossier)
        try:
            paquet.fusionner_runs(dossier)
        except paquet.ErreurPaquet:
            pass
        document = ooxml.Document(dossier / "word" / "document.xml")
        trouves = listes.candidats(document, portee=args.blocs)
    print(json.dumps(trouves, ensure_ascii=False, indent=2))
    return 0


# -- application -----------------------------------------------------------


def _portee_en_blocs(source, pages):
    if not pages:
        return None
    return analyse.blocs_pour_pages(source, pages, CARACTERES_PAR_PAGE)


def commande_appliquer(args):
    source = Path(args.source)
    sortie = Path(args.sortie)

    profil = module_profil.charger()
    if args.profil:
        with open(args.profil, encoding="utf-8") as f:
            charge = json.load(f)
        profil = module_profil.depuis_reponses(charge) if "q1_gene" in charge else charge
    if profil is None:
        print(
            "Aucun profil enregistré : les réglages courants sont utilisés. "
            "(`dys.py profil --reponses ...` pour en enregistrer un)",
            file=sys.stderr,
        )
        profil = dict(module_profil.DEFAUTS)
        profil.update(module_profil.COURANTS)

    etapes = [e.strip() for e in args.etapes.split(",") if e.strip()]
    rapport = analyse.analyser_docx(source)
    portee = _portee_en_blocs(source, args.pages)

    specifications = []
    if args.listes_spec:
        with open(args.listes_spec, encoding="utf-8") as f:
            specifications = json.load(f)

    faits = {}
    with paquet.DossierTemporaire() as dossier:
        paquet.ouvrir(source, dossier)
        try:
            faits["runs_fusionnes"] = paquet.fusionner_runs(dossier)
        except paquet.ErreurPaquet as erreur:
            print("Avertissement : %s" % erreur, file=sys.stderr)

        document = ooxml.Document(dossier / "word" / "document.xml")
        reviseur = suivi.Reviseur(document, auteur=args.auteur)

        # Ordre : le texte d'abord, sur des runs encore entiers ; la mise en
        # forme ensuite, qui découpe les runs pour teinter des caractères.
        if "segmentation" in etapes and profil.get("segmentation", {}).get("actif", True):
            faits["segmentation"] = module_texte.segmenter(document, reviseur, profil, portee)
        if "chiffres" in etapes and profil.get("chiffres", {}).get("grouper"):
            faits["chiffres"] = module_texte.grouper_chiffres(document, reviseur, portee)
        if "listes" in etapes and specifications:
            faits["listes"] = listes.appliquer(document, reviseur, specifications, profil)
        if "tableaux" in etapes:
            faits["tableaux"] = tableaux.traiter(document, dossier, reviseur, profil)
        if "forme" in etapes:
            faits["forme"] = forme.appliquer(document, dossier, profil, rapport)

        document.enregistrer()
        paquet.refermer(dossier, sortie)

    validation = None
    if not args.sans_validation:
        validation = paquet.valider(sortie, original=source, auteur=args.auteur)

    chemin_controle = Path(args.controle) if args.controle else sortie.with_suffix(".controle.md")
    controle.ecrire(chemin_controle, source, sortie, profil, faits, reviseur, validation)

    resume = {
        "sortie": str(sortie),
        "controle": str(chemin_controle),
        "portee_blocs": portee or "document entier",
        "faits": {k: v for k, v in faits.items() if k != "runs_fusionnes"},
        "validation": None if validation is None else validation[0],
    }
    print(json.dumps(resume, ensure_ascii=False, indent=2))
    if validation is not None and validation[0] is False:
        print(validation[1], file=sys.stderr)
        return 3
    return 0


def commande_commenter(args):
    """Un mnémotechnique, un avertissement : en commentaire, jamais dans le texte."""
    with paquet.DossierTemporaire() as dossier:
        paquet.ouvrir(args.source, dossier)
        document = ooxml.Document(dossier / "word" / "document.xml")
        paragraphe = annotations.paragraphe_par_index(document, args.paragraphe)
        if paragraphe is None:
            print("Paragraphe %s introuvable." % args.paragraphe, file=sys.stderr)
            return 1
        identifiant = annotations.poser_sur_paragraphe(dossier, paragraphe, args.texte, args.auteur)
        document.enregistrer()
        paquet.refermer(dossier, args.sortie)
    print(json.dumps({"commentaire": identifiant, "sortie": args.sortie}, ensure_ascii=False))
    return 0


# -- vérification ----------------------------------------------------------


def commande_apercu(args):
    dossier = Path(args.dossier or (Path(args.fichier).parent / "apercu"))
    try:
        images = paquet.rendre_images(args.fichier, dossier, page_max=args.pages)
    except paquet.ErreurPaquet as erreur:
        print(str(erreur), file=sys.stderr)
        return 5
    print(json.dumps([str(i) for i in images], ensure_ascii=False, indent=2))
    print(
        "Regarder ces images avant de les montrer : une police substituée ou un "
        "contraste illisible ne se voit jamais dans le XML.",
        file=sys.stderr,
    )
    return 0


def commande_verifier(args):
    resultats = {}
    passe = True
    incomplet = False

    validation = paquet.valider(args.sortie, original=args.original, auteur=args.auteur)
    resultats["validate.py"] = {"passe": validation[0], "sortie": validation[1][:4000]}
    if validation[0] is False:
        passe = False
    elif validation[0] is None:
        # Une vérification qui n'a pas pu tourner n'est pas une vérification
        # réussie : on le dit au lieu de laisser croire que tout va bien.
        incomplet = True

    avant = analyse.analyser_docx(args.original)
    apres = analyse.analyser_docx(args.sortie)
    resultats["images"] = {"avant": avant["images"], "apres": apres["images"]}
    resultats["medias"] = {"avant": avant["medias"], "apres": apres["medias"]}
    resultats["tableaux"] = {
        "avant": len(avant["tableaux"]),
        "apres": len(apres["tableaux"]),
    }
    if apres["images"] < avant["images"] or apres["medias"] < avant["medias"]:
        passe = False
        resultats["images"]["alerte"] = "des images ont disparu"
    if len(apres["tableaux"]) < len(avant["tableaux"]):
        passe = False
        resultats["tableaux"]["alerte"] = "des tableaux ont disparu"

    valeurs = _controle_des_nombres(args.original, args.sortie)
    resultats["valeurs_numeriques"] = valeurs
    if not valeurs["identiques"]:
        passe = False

    if not passe:
        resultats["verdict"] = "échec"
    elif incomplet:
        resultats["verdict"] = "incomplet"
        resultats["a_faire"] = (
            "Les contrôles internes passent, mais validate.py n'a pas pu tourner : "
            "le document n'a pas été vérifié contre les schémas XSD."
        )
    else:
        resultats["verdict"] = "passe"
    print(json.dumps(resultats, ensure_ascii=False, indent=2))
    if not passe:
        return 3
    return 4 if incomplet else 0


def _controle_des_nombres(original, sortie):
    """Aucune valeur numérique du cours ne doit avoir bougé.

    Règle appliquée : toutes les valeurs de l'original se retrouvent dans le
    document accepté. L'outil a le droit d'ajouter des nombres à lui — numéros
    de liste, numéros de partie — mais jamais de modifier, d'arrondir ni de
    faire disparaître un nombre du cours.
    """
    import re
    import zipfile

    espaces = "[\\s\u202f\u00a0]"

    def nombres(chemin):
        with zipfile.ZipFile(chemin) as archive:
            racine = ooxml.lire(archive.read("word/document.xml"))
        # w:t seulement : c'est la vue « toutes modifications acceptées ».
        texte = " ".join(
            noeud.text or ""
            for noeud in racine.iter()
            if noeud.tag == ooxml.q("w:t")
        )
        bruts = re.findall(r"\d(?:%s|\d)*\d|\d" % espaces, texte)
        return [re.sub(espaces, "", n) for n in bruts]

    avant = nombres(original)
    apres = nombres(sortie)

    restants = list(apres)
    manquants = []
    for valeur in avant:
        if valeur in restants:
            restants.remove(valeur)
        else:
            manquants.append(valeur)

    return {
        "identiques": not manquants,
        "regle": "toutes les valeurs de l'original se retrouvent à l'identique",
        "nombre_avant": len(avant),
        "nombre_apres": len(apres),
        "manquants_ou_modifies": manquants[:10],
        "ajoutes_par_loutil": len(restants),
    }


# -- CLI -------------------------------------------------------------------


def principal(argv=None):
    parseur = argparse.ArgumentParser(prog="dys.py", description=__doc__)
    sous = parseur.add_subparsers(dest="commande")

    p = sous.add_parser("profil", help="charger, définir ou oublier le profil")
    p.add_argument("--reponses", help="fichier JSON de réponses au questionnaire")
    p.add_argument("--definir", nargs="*", help="police=Arial taille_pt=16 chiffres.grouper=true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--oublier", action="store_true")
    p.set_defaults(fonction=commande_profil)

    p = sous.add_parser("questions", help="les questions à poser, et elles seules")
    p.add_argument("--difficultes", help="ligne,lettres,attention,chiffres,reperage,fatigue")
    p.add_argument("--troubles", help="dyslexie,tdah,dyscalculie,dyspraxie,dysorthographie")
    p.set_defaults(fonction=commande_questions)

    p = sous.add_parser("analyser", help="volume, densité, tableaux, listes enfouies")
    p.add_argument("fichier")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fonction=commande_analyser)

    p = sous.add_parser("listes", help="énumérations enfouies, à confirmer avant d'agir")
    p.add_argument("fichier")
    p.add_argument("--blocs", type=int)
    p.set_defaults(fonction=commande_listes)

    p = sous.add_parser("appliquer", help="adapter le document")
    p.add_argument("source")
    p.add_argument("sortie")
    p.add_argument("--profil", help="fichier de profil ou de réponses (sinon : profil enregistré)")
    p.add_argument("--etapes", default="forme,segmentation,chiffres,tableaux")
    p.add_argument("--pages", type=int, help="limite les étapes coûteuses aux N premières pages")
    p.add_argument("--listes-spec", help="candidats confirmés, au format de `dys.py listes`")
    p.add_argument("--controle", help="chemin du fichier de contrôle")
    p.add_argument("--auteur", default=AUTEUR)
    p.add_argument("--sans-validation", action="store_true")
    p.set_defaults(fonction=commande_appliquer)

    p = sous.add_parser("commenter", help="ajouter un commentaire Word")
    p.add_argument("source")
    p.add_argument("sortie")
    p.add_argument("--paragraphe", type=int, required=True)
    p.add_argument("--texte", required=True)
    p.add_argument("--auteur", default=AUTEUR)
    p.set_defaults(fonction=commande_commenter)

    p = sous.add_parser("apercu", help="rendre les premières pages en images")
    p.add_argument("fichier")
    p.add_argument("--pages", type=int, default=1)
    p.add_argument("--dossier")
    p.set_defaults(fonction=commande_apercu)

    p = sous.add_parser("verifier", help="validate.py + images, tableaux, valeurs numériques")
    p.add_argument("sortie")
    p.add_argument("--original", required=True)
    p.add_argument("--auteur", default=AUTEUR)
    p.set_defaults(fonction=commande_verifier)

    arguments = parseur.parse_args(argv)
    if not getattr(arguments, "fonction", None):
        parseur.print_help()
        return 1
    if not ooxml.XML_DURCI:
        print(
            "Avertissement : defusedxml n'est pas installé. Les documents traités "
            "viennent de tiers ; sans lui, une bombe d'entités XML n'est pas "
            "arrêtée. Installer : python3 -m pip install defusedxml",
            file=sys.stderr,
        )
    try:
        return arguments.fonction(arguments)
    except paquet.ErreurPaquet as erreur:
        print("Erreur : %s" % erreur, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(principal())
