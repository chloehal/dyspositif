"""Contrats utilisateur : les inférences ne remplacent jamais ses choix."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from dyslib import profil


class Profils(unittest.TestCase):
    def test_refus_chiffres_prioritaire(self):
        p = profil.depuis_reponses({'q1_gene': ['chiffres'], 'c1_groupes': 'colle'})
        self.assertFalse(p['chiffres']['grouper'])
        self.assertFalse(p['chiffres']['paires'])

    def test_difficulte_ne_vaut_pas_autorisation(self):
        p = profil.depuis_reponses({'d3_segmenter_ou_reecrire': 'segmentee', 'd4_mot_complique': 'bloque'})
        self.assertFalse(p['reformulation']['actif'])

    def test_diagnostic_sans_inference(self):
        p = profil.depuis_reponses({'q1_troubles': ['dyscalculie', 'trouble_inconnu']})
        self.assertEqual(p['difficultes'], [])
        self.assertFalse(p['chiffres']['grouper'])

    def test_non_desactive_et_reponses_partielles_preservent(self):
        p = profil.depuis_reponses({'q1_gene': ['ligne'], 'q1_troubles': ['dyslexie']})
        p = profil.appliquer_definitions(p, ['lettres_miroir.actif=true'])
        p = profil.depuis_reponses({'d2_lettres_miroir': 'non'}, base=p)
        self.assertFalse(p['lettres_miroir']['actif'])
        self.assertEqual(p['difficultes'], ['ligne'])
        self.assertEqual(p['troubles_declares'], ['dyslexie'])

    def test_proposition_ne_s_applique_pas_sans_essai(self):
        p = profil.depuis_reponses({'d1_relire': 'souvent'})
        self.assertEqual(p['interligne'], profil.DEFAUTS['interligne'])
        self.assertIn('interligne', p['propositions'])
        p = profil.valider_propositions(p, ['interligne'])
        self.assertEqual(p['interligne'], 1.8)
        self.assertEqual(p['decisions']['interligne']['etat'], 'valide')

    def test_refus_ne_peut_pas_etre_reactive_par_inference(self):
        p = profil.appliquer_definitions(profil.normaliser({}), ['interligne=1.2'])
        p = profil.depuis_reponses({'d1_relire': 'souvent', 'interrompu': True}, base=p)
        self.assertEqual(p['interligne'], 1.2)
        self.assertNotIn('interligne', p['propositions'])

    def test_fusion_profonde_sans_mutation(self):
        base = {'chiffres': {'grouper': False}}
        old = copy.deepcopy(base)
        p = profil.depuis_reponses({'c2_tableau': 'doigt'}, base=base)
        self.assertIn('teinte', p['chiffres'])
        self.assertEqual(base, old)

    def test_inconnus_et_conflit_sans_couleurs(self):
        p = profil.depuis_reponses({'q1_gene': ['sensibilite_inconnue'], 'besoin_libre': 'Je lis au clavier'})
        p = profil.appliquer_definitions(p, ['lettres_miroir.actif=true', 'sans_couleurs=true'])
        effectif = profil.pour_application(p)
        self.assertFalse(effectif['lettres_miroir']['actif'])
        self.assertTrue(effectif['conflits'])
        self.assertEqual(p['besoin_libre'], 'Je lis au clavier')

    def test_valeurs_invalides_rejetees(self):
        for definition in ['taille_pt=-4', 'interligne=nan', 'fond=violet', 'chiffres.grouper=peut-etre', 'inexistant=true']:
            with self.subTest(definition=definition), self.assertRaises(ValueError):
                profil.appliquer_definitions(profil.normaliser({}), [definition])

    def test_garder_original_annule_les_adaptations(self):
        p = profil.depuis_reponses({'c1_groupes': 'espace', 'c3_teintes': 'oui', 'q_tableaux': 'decouper'})
        p = profil.depuis_reponses({'c1_groupes': 'original', 'c3_teintes': 'original', 'q_tableaux': 'original'}, p)
        self.assertFalse(p['chiffres']['grouper'])
        self.assertFalse(p['chiffres']['paires'])
        self.assertEqual(p['tableaux']['action'], 'conserver')

    def test_migration_etat_non_valide(self):
        p = profil.normaliser({'version': 1, 'interligne': 1.8, 'chiffres': {'grouper': True}})
        self.assertFalse(p['chiffres']['grouper'])
        self.assertEqual(p['propositions']['interligne']['origine'], 'migration_v1')
        self.assertFalse(p['decisions'])

    def test_profil_malforme_explique_l_erreur(self):
        for base in [{'lettres_miroir': None}, {'decisions': {'interligne': 'oui'}},
                     {'propositions': {'interligne': {'valeur': -1, 'origine': 'test', 'etat': 'propose'}}}]:
            with self.subTest(base=base), self.assertRaises(ValueError):
                profil.normaliser(base)

    def test_contextes_et_temporaire(self):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, DYSPOSITIF_PROFIL=str(Path(d) / 'profil.json'))
            cmd = [sys.executable, str(ROOT / 'scripts/dys.py'), 'profil']
            a = subprocess.run(cmd + ['--contexte', 'ecran', '--definir', 'fond=sombre'], env=env, capture_output=True, text=True)
            self.assertEqual(a.returncode, 0, a.stderr)
            b = subprocess.run(cmd + ['--contexte', 'ecran', '--definir', 'fond=blanc', '--temporaire', '--json'], env=env, capture_output=True, text=True)
            self.assertEqual(b.returncode, 0, b.stderr)
            self.assertEqual(json.loads(b.stdout)['fond'], 'blanc')
            self.assertEqual(json.loads(b.stdout)['decisions']['fond']['etat'], 'essai')
            c = subprocess.run(cmd + ['--contexte', 'ecran', '--json'], env=env, capture_output=True, text=True)
            self.assertEqual(json.loads(c.stdout)['fond'], 'sombre')


class Questions(unittest.TestCase):
    def call(self, *options):
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/dys.py'), 'questions'] + list(options), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_combinaison_independante_ordre(self):
        a = self.call('--difficultes', 'attention,fatigue')
        b = self.call('--difficultes', 'fatigue,attention')
        self.assertEqual(a, b)
        self.assertTrue(all(len(g) == 1 for g in a['groupes']))

    def test_diagnostic_ne_selectionne_pas_une_branche(self):
        r = self.call('--troubles', 'dyscalculie')
        self.assertEqual(r['branches_ouvertes'], [])
        self.assertIn('q1_gene', [q['id'] for g in r['groupes'] for q in g])

    def test_besoin_non_repertorie_et_acces_non_visuel(self):
        r = self.call('--difficultes', 'inconnu,navigation', '--acces', 'lecteur_ecran')
        self.assertTrue(r['presentation']['champ_libre_facultatif'])
        self.assertEqual(r['presentation']['progression'], 'texte')
        self.assertIn('autre', r['branches_ouvertes'])


if __name__ == '__main__':
    unittest.main()
