#!/usr/bin/env python3
"""Tests de la skill dyspositif.

    python3 tests/test_dys.py

Ce que ces tests garantissent, dans l'ordre d'importance :

1. le document produit s'ouvre (validate.py, XSD) ;
2. rejeter les modifications suivies restitue exactement le texte d'origine ;
3. les images et les tableaux d'origine sont toujours là ;
4. aucune valeur numérique du cours n'a bougé ;
5. le questionnaire ne pose que les branches déclarées.

Les points 1 et 4 dépendent de la skill docx et d'un Python avec lxml :
    export DYSPOSITIF_SKILL_DOCX=/chemin/vers/skills/docx
    export DYSPOSITIF_PYTHON=/chemin/vers/python-avec-lxml
Sans eux, ces tests-là sont sautés, pas silencieusement réussis.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
sys.path.insert(0, str(RACINE / "tests"))

import fabriquer_fixture  # noqa: E402
from dyslib import analyse, ooxml, paquet, profil as module_profil  # noqa: E402
from dyslib.ooxml import q  # noqa: E402

DYS = [sys.executable, str(RACINE / "scripts" / "dys.py")]

REPONSES = {
    "q1_gene": ["ligne", "lettres", "attention", "chiffres"],
    "q1_troubles": ["dyslexie", "tdah", "dyscalculie"],
    "q2_support": "ecran",
    "q3_fond": "sombre",
    "q4_police": "a",
    "q5_couleurs": "systeme",
    "q5_grille": {"definitions": "bleu", "a_retenir": "vert"},
    "d1_relire": "souvent",
    "d2_lettres_miroir": "oui",
    "d3_segmenter_ou_reecrire": "segmentee",
    "a2_listes": "groupes",
    "a3_reprise": "cherche",
    "c1_groupes": "espace",
    "c2_tableau": "abandonne",
    "z1_mnemo": "oui",
}


def lancer(*arguments, **kwargs):
    return subprocess.run(
        DYS + list(arguments), capture_output=True, text=True, env=ENV, **kwargs
    )


def texte_rejete(chemin):
    """Le texte tel qu'il revient si l'on rejette toutes les modifications suivies."""
    with zipfile.ZipFile(chemin) as archive:
        racine = ooxml.ET.fromstring(archive.read("word/document.xml"))
    return _texte(racine, garder_insertions=False)


def texte_accepte(chemin):
    with zipfile.ZipFile(chemin) as archive:
        racine = ooxml.ET.fromstring(archive.read("word/document.xml"))
    return _texte(racine, garder_insertions=True)


def _texte(racine, garder_insertions):
    insere = set()
    for insertion in racine.iter(q("w:ins")):
        for noeud in insertion.iter():
            insere.add(id(noeud))
    paragraphes = []
    for paragraphe in racine.iter(q("w:p")):
        morceaux = []
        for noeud in paragraphe.iter():
            if noeud.tag == q("w:t"):
                if id(noeud) in insere and not garder_insertions:
                    continue
                morceaux.append(noeud.text or "")
            elif noeud.tag == q("w:delText"):
                if garder_insertions:
                    continue
                morceaux.append(noeud.text or "")
        texte = "".join(morceaux)
        if texte:
            paragraphes.append(texte)
    return "\n".join(paragraphes)


class BaseDocument(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = Path(tempfile.mkdtemp(prefix="dyspositif-tests-"))
        cls.documents = fabriquer_fixture.tout(cls.dossier / "documents")
        cls.source = cls.documents["docx"]
        chemin_reponses = cls.dossier / "reponses.json"
        chemin_reponses.write_text(json.dumps(REPONSES), encoding="utf-8")
        resultat = lancer("profil", "--reponses", str(chemin_reponses))
        assert resultat.returncode == 0, resultat.stderr


class TestAnalyse(BaseDocument):
    def test_volume_et_reperes(self):
        rapport = analyse.analyser_docx(self.source)
        self.assertGreaterEqual(rapport["images"], 1)
        self.assertEqual(len(rapport["tableaux"]), 2)
        self.assertEqual(len(rapport["tableaux_larges"]), 1)
        self.assertGreaterEqual(rapport["paragraphes_denses"], [])
        self.assertGreater(rapport["formatage_direct"]["runs"], 0)
        self.assertIn("passages denses", rapport["resume"])

    def test_liste_enfouie_annoncee_par_le_texte(self):
        rapport = analyse.analyser_docx(self.source)
        candidates = rapport["listes_candidates"]
        self.assertEqual(len(candidates), 1, "une seule vraie énumération dans le cours")
        self.assertEqual(candidates[0]["nombre"], 6)
        self.assertEqual(candidates[0]["certitude"], "annoncée par le texte")

    def test_pas_de_fausse_liste(self):
        """Deux virgules et un « et » ne font pas une énumération."""
        texte = (
            "La population du royaume atteignait 1247893 habitants recensés en "
            "1789, pour une dette publique de 126000000 livres et un déficit "
            "annuel de 56000 livres par district."
        )
        self.assertIsNone(analyse.detecter_liste_enfouie(texte))

    def test_pdf_scanne_signale(self):
        rapport = analyse.analyser_pdf(self.documents["pdf_scanne"])
        self.assertFalse(rapport["texte_extractible"])
        self.assertTrue(rapport["scanne_probable"])
        self.assertIn("Aucun texte extractible", rapport["resume"])

    def test_pdf_numerique_reconnu(self):
        rapport = analyse.analyser_pdf(self.documents["pdf_texte"])
        self.assertTrue(rapport["texte_extractible"])


class TestProfil(BaseDocument):
    def test_reponses_traduites_en_reglages(self):
        profil = module_profil.charger()
        self.assertEqual(profil["fond"], "sombre")
        self.assertTrue(profil["lettres_miroir"]["actif"])
        self.assertTrue(profil["chiffres"]["grouper"])
        self.assertEqual(profil["listes"]["grouper_par"], 3)
        self.assertEqual(profil["tableaux"]["action"], "decouper")
        self.assertLessEqual(profil["longueur_ligne"], 60)

    def test_resume_tient_sur_une_ligne(self):
        resume = module_profil.resume(module_profil.charger())
        self.assertNotIn("\n", resume)
        self.assertIn("interligne", resume)

    def test_papier_annule_le_fond_sombre(self):
        profil = module_profil.depuis_reponses(
            {"q1_gene": ["ligne"], "q2_support": "papier", "q3_fond": "sombre"}
        )
        self.assertNotEqual(profil["fond"], "sombre")

    def test_branches_seulement_si_declarees(self):
        self.assertEqual(module_profil.branches_a_poser(["chiffres"]), ["chiffres"])
        self.assertEqual(
            module_profil.branches_a_poser(["ligne"]), ["dechiffrage"]
        )

    def test_arret_anticipe_complete_sans_ecraser(self):
        profil = module_profil.depuis_reponses(
            {"q1_gene": ["ligne"], "q3_fond": "sombre", "interrompu": True}
        )
        self.assertEqual(profil["fond"], "sombre", "la réponse donnée l'emporte")
        self.assertEqual(profil["police"], module_profil.COURANTS["police"])


class TestQuestionnaire(BaseDocument):
    def _questions(self, **arguments):
        options = []
        for cle, valeur in arguments.items():
            options += ["--" + cle, valeur]
        resultat = lancer("questions", *options)
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        return json.loads(resultat.stdout)

    def test_dyscalculie_progression_figuree(self):
        sortie = self._questions(troubles="dyscalculie")
        self.assertEqual(sortie["presentation"]["progression"], "points")
        self.assertIn("progression", sortie)
        self.assertIn("●", sortie["progression"][0])
        self.assertEqual(sortie["branches_ouvertes"], ["chiffres"])

    def test_dechiffrage_sans_branche_chiffres(self):
        sortie = self._questions(difficultes="ligne")
        self.assertEqual(sortie["branches_ouvertes"], ["dechiffrage"])
        identifiants = [q["id"] for groupe in sortie["groupes"] for q in groupe]
        self.assertFalse([i for i in identifiants if i.startswith("c")])

    def test_questions_par_groupes_de_trois(self):
        sortie = self._questions()
        self.assertTrue(all(len(groupe) <= 3 for groupe in sortie["groupes"]))
        self.assertIn("t'arrêter quand tu veux", sortie["annonce"])

    def test_aucune_question_a_champ_libre(self):
        chemin = RACINE / "references" / "questionnaire.json"
        questionnaire = json.loads(chemin.read_text(encoding="utf-8"))
        toutes = list(questionnaire["socle"]) + list(questionnaire["final"])
        for branche in questionnaire["branches"].values():
            toutes += branche
        for question in toutes:
            self.assertTrue(
                question.get("options") or question.get("grille"),
                "%s attend une réponse libre" % question["id"],
            )

    def test_les_questions_de_forme_montrent(self):
        chemin = RACINE / "references" / "questionnaire.json"
        questionnaire = json.loads(chemin.read_text(encoding="utf-8"))
        for identifiant in ("q3_fond", "q4_police"):
            question = [q for q in questionnaire["socle"] if q["id"] == identifiant][0]
            self.assertIn("montrer", question)
            self.assertIn("variantes", question["montrer"])


class TestApplication(BaseDocument):
    @classmethod
    def setUpClass(cls):
        super(TestApplication, cls).setUpClass()
        cls.sortie = cls.dossier / "sortie.docx"
        cls.listes = cls.dossier / "listes.json"
        candidats = lancer("listes", str(cls.source))
        cls.listes.write_text(candidats.stdout, encoding="utf-8")
        cls.resultat = lancer(
            "appliquer",
            str(cls.source),
            str(cls.sortie),
            "--etapes",
            "forme,segmentation,chiffres,tableaux,listes",
            "--listes-spec",
            str(cls.listes),
        )

    def test_le_document_est_produit(self):
        self.assertEqual(self.resultat.returncode, 0, self.resultat.stderr)
        self.assertTrue(self.sortie.exists())

    def test_rejeter_tout_restitue_loriginal(self):
        """La garantie centrale, vérifiée sans dépendre de validate.py."""
        self.assertEqual(texte_rejete(self.sortie), texte_rejete(self.source))

    def test_images_et_tableaux_conserves(self):
        avant = analyse.analyser_docx(self.source)
        apres = analyse.analyser_docx(self.sortie)
        self.assertEqual(avant["images"], apres["images"])
        self.assertEqual(avant["medias"], apres["medias"])
        self.assertGreaterEqual(len(apres["tableaux"]), len(avant["tableaux"]))

    def test_aucune_valeur_numerique_modifiee(self):
        import re

        def nombres(texte):
            return [
                re.sub(r"[\s  ]", "", n)
                for n in re.findall(r"\d(?:[\s  ]|\d)*\d|\d", texte)
            ]

        origine = nombres(texte_accepte(self.source))
        produit = nombres(texte_accepte(self.sortie))
        for valeur in origine:
            self.assertIn(valeur, produit, "valeur %s perdue ou modifiée" % valeur)

    def test_tout_changement_de_texte_est_suivi(self):
        with zipfile.ZipFile(self.sortie) as archive:
            xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("w:ins ", xml)
        self.assertIn('w:author="dyspositif"', xml)

    def test_les_chiffres_sont_groupes(self):
        self.assertIn("1 247 893", texte_accepte(self.sortie))

    def test_la_liste_enfouie_est_sortie_et_comptee(self):
        accepte = texte_accepte(self.sortie)
        self.assertIn("1 sur 6 — la crise financière", accepte)
        self.assertIn("6 sur 6 — le blocage des états généraux", accepte)

    def test_fichier_de_controle_ecrit(self):
        controle = self.sortie.with_suffix(".controle.md")
        self.assertTrue(controle.exists())
        contenu = controle.read_text(encoding="utf-8")
        self.assertIn("Valeurs numériques", contenu)
        self.assertIn("Revenir en arrière", contenu)

    def test_mise_en_forme_appliquee(self):
        with zipfile.ZipFile(self.sortie) as archive:
            styles = archive.read("word/styles.xml").decode("utf-8")
            document = archive.read("word/document.xml").decode("utf-8")
        self.assertIn('w:ascii="Verdana"', styles)
        self.assertNotIn('w:val="both"', document, "le texte justifié doit disparaître")
        self.assertIn("w:background", document)

    def test_portee_limitee_aux_premieres_pages(self):
        blocs = analyse.blocs_pour_pages(self.source, 1)
        self.assertGreaterEqual(blocs, 1)


@unittest.skipUnless(
    os.environ.get("DYSPOSITIF_SKILL_DOCX") or paquet.skill_docx(obligatoire=False),
    "skill docx introuvable",
)
class TestValidationMachine(BaseDocument):
    @classmethod
    def setUpClass(cls):
        super(TestValidationMachine, cls).setUpClass()
        cls.sortie = cls.dossier / "validee.docx"
        cls.resultat = lancer("appliquer", str(cls.source), str(cls.sortie))

    def test_validate_py_passe(self):
        if paquet.python_docx() is None:
            self.skipTest("aucun Python avec lxml pour validate.py")
        resultat = lancer(
            "verifier", str(self.sortie), "--original", str(self.source)
        )
        rapport = json.loads(resultat.stdout)
        self.assertTrue(rapport["validate.py"]["passe"], rapport["validate.py"]["sortie"])
        self.assertEqual(rapport["verdict"], "passe")


ENV = dict(os.environ)


def principal():
    global ENV
    dossier = tempfile.mkdtemp(prefix="dyspositif-env-")
    # Le profil de test ne doit jamais toucher celui de l'utilisateur : la
    # variable vaut pour ce processus comme pour les sous-processus.
    os.environ["DYSPOSITIF_PROFIL"] = str(Path(dossier) / "profil.json")
    ENV = dict(os.environ)
    return unittest.main(module=__name__, argv=[sys.argv[0]] + sys.argv[1:], exit=False)


if __name__ == "__main__":
    resultat = principal()
    sys.exit(0 if resultat.result.wasSuccessful() else 1)
