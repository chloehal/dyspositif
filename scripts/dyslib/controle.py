"""Le fichier de contrôle : ce qui a été fait, et ce qui n'a pas été touché.

Il sert à deux choses. Répondre à « qu'est-ce que tu as changé exactement ? »
sans rouvrir le document, et rendre vérifiable la promesse la plus sensible :
aucune valeur numérique modifiée.
"""

from datetime import datetime

from . import profil as module_profil


def ecrire(chemin, source, sortie, profil, faits, reviseur, validation=None):
    lignes = []
    ajouter = lignes.append

    ajouter("# Fichier de contrôle — dyspositif")
    ajouter("")
    ajouter("- Document d'origine : `%s`" % source)
    ajouter("- Document produit : `%s`" % sortie)
    ajouter("- Date : %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    ajouter("- Profil appliqué : %s" % module_profil.resume(profil))
    ajouter("")

    ajouter("## Mise en forme (aucun mot touché)")
    ajouter("")
    if faits.get("forme"):
        for cle, valeur in sorted(faits["forme"].items()):
            ajouter("- %s : %s" % (cle.replace("_", " "), valeur))
    else:
        ajouter("- (non appliquée)")
    ajouter("")

    textuelles = [e for e in reviseur.journal if e["genre"] in ("texte", "liste")]
    segmentations = [e for e in reviseur.journal if e["genre"] == "segmentation"]
    tableaux = [e for e in reviseur.journal if e["genre"] == "tableau"]
    ajouts = [e for e in reviseur.journal if e["genre"] == "ajout"]

    ajouter("## Modifications suivies (texte)")
    ajouter("")
    ajouter(
        "Chacune est un `w:ins` / `w:del` signé « %s » : dans Word, onglet "
        "Révision, chaque changement s'accepte ou se rejette un par un."
        % reviseur.auteur
    )
    ajouter("")
    if textuelles:
        ajouter("| Paragraphe | Nature | Avant | Après |")
        ajouter("|---|---|---|---|")
        for entree in textuelles:
            ajouter(
                "| %s | %s | %s | %s |"
                % (
                    entree.get("paragraphe") if entree.get("paragraphe") is not None else entree.get("index", "—"),
                    entree["detail"],
                    _cellule(entree.get("avant")),
                    _cellule(entree.get("apres")),
                )
            )
    else:
        ajouter("Aucune.")
    ajouter("")
    ajouter("- Coupures de phrases longues (mêmes mots) : %s" % len(segmentations))
    ajouter("")

    ajouter("## Valeurs numériques")
    ajouter("")
    regroupements = [
        e for e in textuelles if "chiffres" in (e.get("detail") or "")
    ]
    if regroupements:
        ajouter(
            "%s nombre(s) regroupés par tranches de trois. Les chiffres eux-mêmes "
            "sont identiques — seuls des espaces fines insécables ont été insérés."
            % len(regroupements)
        )
        for entree in regroupements:
            ajouter(
                "- `%s` → `%s` (mêmes chiffres, même valeur)"
                % (entree.get("avant"), entree.get("apres"))
            )
    else:
        ajouter("Aucun nombre modifié.")
    ajouter("")

    if tableaux:
        ajouter("## Tableaux")
        ajouter("")
        for entree in tableaux:
            ajouter("- %s" % entree["detail"])
        ajouter("")

    ajouter("## Ajouts de l'outil")
    ajouter("")
    if ajouts:
        ajouter(
            "Ces éléments ne viennent pas du cours. Ils sont en commentaires Word, "
            "jamais dans le corps du texte, et se suppriment d'un clic."
        )
        for entree in ajouts:
            ajouter("- paragraphe %s : %s" % (entree.get("index"), entree["detail"]))
    else:
        ajouter("Aucun. Rien n'a été ajouté au contenu du cours.")
    ajouter("")

    if validation is not None:
        ajouter("## Vérification machine")
        ajouter("")
        ajouter(
            "`validate.py --original --author %s` : %s"
            % (reviseur.auteur, "passé" if validation[0] else "ÉCHEC")
        )
        if not validation[0] and validation[1]:
            ajouter("")
            ajouter("```")
            ajouter(validation[1][:2000])
            ajouter("```")
        ajouter("")

    ajouter("## Revenir en arrière")
    ajouter("")
    ajouter(
        "Dans Word : onglet **Révision** → **Rejeter** pour annuler un changement, "
        "ou *Rejeter toutes les modifications* pour retrouver le texte d'origine. "
        "La mise en forme, elle, se retire en repartant du fichier d'origine, qui "
        "n'a pas été modifié."
    )
    ajouter("")

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))
    return chemin


def _cellule(valeur):
    if valeur is None:
        return "—"
    valeur = valeur.replace("|", "\\|").replace("\n", " ")
    if len(valeur) > 80:
        valeur = valeur[:77] + "…"
    return "`%s`" % valeur
