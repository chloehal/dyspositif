"""Vérifie les effets réels sur les fichiers, pas les textes des consignes."""
import copy
import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import fabriquer_fixture
from dyslib import forme, ooxml, paquet, profil, tableaux, suivi
from dyslib.ooxml import q


def contrast(a, b):
    def luminance(h):
        rgb = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
        rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        return sum(v*w for v, w in zip(rgb, (.2126, .7152, .0722)))
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi+.05)/(lo+.05)


class Documents(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.d = Path(self.temp.name)
        self.source = fabriquer_fixture.tout(self.d / 'fixtures')['docx']
        self.env = dict(os.environ, DYSPOSITIF_PROFIL=str(self.d / 'profil.json'))

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/dys.py')] + list(args), env=self.env, capture_output=True, text=True)

    def test_contraste_teintes_sur_chaque_fond(self):
        for fond, bg in [('blanc', 'FFFFFF'), ('creme', 'FBF6EC'), ('sombre', '22262B')]:
            p = profil.depuis_reponses({'q3_fond': fond})
            for c in ['C2410C', '0B6E4F', '1D4ED8']:
                couleur = forme.couleur_libre(p, c)
                self.assertGreaterEqual(contrast(couleur, bg), 4.5)

    def test_teinte_preserve_un_code_couleur_existant(self):
        with paquet.DossierTemporaire() as d:
            paquet.ouvrir(self.source, d)
            doc = ooxml.Document(d / 'word/document.xml')
            r = next(r for r in doc.racine.iter(q('w:r')) if r.find(q('w:t')) is not None)
            r.find(q('w:t')).text = 'baba'
            ooxml.poser_enfant(ooxml.rpr(r, True), 'w:color', ooxml.ORDRE_RPR, val='1D4ED8')
            before = ET.tostring(r)
            forme._teinter(doc, 'bdpq', 'C2410C')
            self.assertEqual(ET.tostring(r), before)
            self.assertTrue(any(x is r for x in doc.racine.iter(q('w:r'))))

    def test_teinte_preserve_style_de_paragraphe(self):
        with paquet.DossierTemporaire() as d:
            paquet.ouvrir(self.source, d)
            doc = ooxml.Document(d / 'word/document.xml')
            p = next(doc.paragraphes())
            ooxml.poser_enfant(ooxml.ppr(p, True), 'w:pStyle', ooxml.ORDRE_PPR, val='DefinitionBlue')
            r = ET.SubElement(p, q('w:r'))
            ET.SubElement(r, q('w:t')).text = 'baba'
            before = ET.tostring(r)
            forme._teinter(doc, 'bdpq', 'C2410C')
            self.assertTrue(any(x is r for x in doc.racine.iter(q('w:r'))))
            self.assertEqual(ET.tostring(r), before)

    def test_un_seul_choix_preserve_police_fond_et_marges(self):
        with paquet.DossierTemporaire() as d:
            paquet.ouvrir(self.source, d)
            doc = ooxml.Document(d / 'word/document.xml')
            initial = ET.tostring(doc.racine)
            styles_before = ooxml.lire_fichier(d / 'word/styles.xml').getroot()
            fonts = [ET.tostring(e) for e in styles_before.iter(q('w:rFonts'))]
            marges = [ET.tostring(e) for e in doc.racine.iter(q('w:pgMar'))]
            p = profil.appliquer_definitions({}, ['interligne=1.8'])
            forme.appliquer(doc, d, p)
            self.assertIsNone(doc.racine.find(q('w:background')))
            self.assertEqual(marges, [ET.tostring(e) for e in doc.racine.iter(q('w:pgMar'))])
            styles_after = ooxml.lire_fichier(d / 'word/styles.xml').getroot()
            self.assertEqual(fonts, [ET.tostring(e) for e in styles_after.iter(q('w:rFonts'))])
            self.assertNotEqual(ET.tostring(doc.racine), initial)

    def test_integrite_preserve_structure_mathematique(self):
        from dyslib import integrite
        with zipfile.ZipFile(self.source) as z:
            data = {n: z.read(n) for n in z.namelist()}
        root = ooxml.lire(data['word/document.xml'])
        p = next(root.iter(q('w:p')))
        math = ET.SubElement(p, q('m:oMath'))
        frac = ET.SubElement(math, q('m:f'))
        for tag, text in [('m:num', '1'), ('m:den', '2')]:
            r = ET.SubElement(ET.SubElement(frac, q(tag)), q('m:r'))
            ET.SubElement(r, q('m:t')).text = text
        paths = []
        for i in range(2):
            if i:
                math.clear()
                ET.SubElement(ET.SubElement(math, q('m:r')), q('m:t')).text = '12'
            data['word/document.xml'] = ET.tostring(root)
            path = self.d / ('math%s.docx' % i)
            with zipfile.ZipFile(path, 'w') as z:
                for n, content in data.items():
                    z.writestr(n, content)
            paths.append(path)
        self.assertFalse(integrite.comparer(*paths)['passe'])

    def test_liste_semantique_et_spec_perimee(self):
        from dyslib import listes
        with paquet.DossierTemporaire() as d:
            paquet.ouvrir(self.source, d)
            doc = ooxml.Document(d / 'word/document.xml')
            candidats = listes.candidats(doc)
            rev = suivi.Reviseur(doc)
            p = profil.appliquer_definitions({}, ['listes.numeroter=false'])
            compte = listes.appliquer(doc, rev, candidats, p, dossier=d)
            self.assertEqual(compte, 1)
            self.assertTrue(any(True for _ in doc.racine.iter(q('w:numPr'))))
            self.assertTrue((d / 'word/numbering.xml').is_file())
            for name in ['word/numbering.xml', 'word/_rels/document.xml.rels', '[Content_Types].xml']:
                self.assertIsNotNone(ooxml.lire_fichier(d / name).getroot())
            with self.assertRaises(ValueError):
                listes.appliquer(doc, rev, candidats, p, dossier=d)

    def test_police_heritee_symbole_non_ecrasee(self):
        with paquet.DossierTemporaire() as d:
            paquet.ouvrir(self.source, d)
            doc = ooxml.Document(d / 'word/document.xml')
            p = next(doc.paragraphes())
            r = ET.SubElement(p, q('w:r'))
            rp = ET.SubElement(r, q('w:rPr'))
            ET.SubElement(rp, q('w:rStyle'), {q('w:val'): 'Symboles'})
            ET.SubElement(rp, q('w:b'))
            ET.SubElement(r, q('w:t')).text = 'a'
            styles = ooxml.lire_fichier(d / 'word/styles.xml')
            style = ET.SubElement(styles.getroot(), q('w:style'), {q('w:type'): 'character', q('w:styleId'): 'Symboles'})
            props = ET.SubElement(style, q('w:rPr'))
            ET.SubElement(props, q('w:rFonts'), {q('w:ascii'): 'Symbol', q('w:hAnsi'): 'Symbol'})
            styles.write(d / 'word/styles.xml', encoding='UTF-8', xml_declaration=True)
            forme.appliquer(doc, d, profil.appliquer_definitions({}, ['police=Arial']))
            self.assertIsNone(rp.find(q('w:rFonts')))

    def test_conserver_tableaux_ne_pose_pas_de_commentaires(self):
        with paquet.DossierTemporaire() as d:
            paquet.ouvrir(self.source, d)
            doc = ooxml.Document(d / 'word/document.xml')
            rev = suivi.Reviseur(doc)
            self.assertEqual(tableaux.traiter(doc, d, rev, profil.normaliser({})), [])

    def test_cours_refuse_et_source_intacte(self):
        before = self.source.read_bytes()
        out = self.d / 'sortie.docx'
        r = self.cli('appliquer', str(self.source), str(out), '--nature', 'cours')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('synthèse existante', r.stderr)
        self.assertFalse(out.exists())
        self.assertEqual(self.source.read_bytes(), before)
        r = self.cli('appliquer', str(self.source), str(self.source), '--nature', 'synthese')
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.source.read_bytes(), before)

    def test_extrait_repere_un_tableau_hors_premiere_page(self):
        r = self.cli('extrait', str(self.source), '--inventaire')
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        indice = next(b['index'] for b in data['blocs'] if b['type'] == 'tableau')
        out = self.d / 'extrait.docx'
        r = self.cli('extrait', str(self.source), str(out), '--debut', str(indice), '--fin', str(indice))
        self.assertEqual(r.returncode, 0, r.stderr)
        with zipfile.ZipFile(out) as z:
            body = ooxml.lire(z.read('word/document.xml')).find(q('w:body'))
            self.assertEqual(len(body.findall(q('w:tbl'))), 1)
            self.assertIsNotNone(body.find(q('w:sectPr')))
        self.assertNotEqual(out.read_bytes(), self.source.read_bytes())

    def test_audit_accessibilite_signale_images_et_structure(self):
        r = self.cli('accessibilite', str(self.source))
        self.assertEqual(r.returncode, 4, r.stderr)
        data = json.loads(r.stdout)
        self.assertFalse(data['certification'])
        self.assertIn('image_sans_alternative', [a['code'] for a in data['alertes']])

    def test_fidelite_detecte_media_modifie_meme_nombre(self):
        with zipfile.ZipFile(self.source) as z:
            data = {n: z.read(n) for n in z.namelist()}
        name = next(n for n in data if n.startswith('word/media/'))
        data[name] = b'corruption'
        out = self.d / 'corrompu.docx'
        with zipfile.ZipFile(out, 'w') as z:
            for n, content in data.items():
                z.writestr(n, content)
        r = self.cli('verifier', str(out), '--original', str(self.source))
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn(name, json.loads(r.stdout)['integrite']['modifies_ou_perdus'])

    def test_structure_confirmee_sans_recriture(self):
        with zipfile.ZipFile(self.source) as z:
            root = ooxml.lire(z.read('word/document.xml'))
            image_id = next(root.iter(q('wp:docPr'))).get('id')
            text_before = ''.join(t.text or '' for t in root.iter(q('w:t')))
        spec = self.d / 'structure.json'
        spec.write_text(json.dumps({'langue': 'fr-BE', 'titres': {'0': 1},
                                    'alternatives': {image_id: 'Schéma fourni dans la synthèse.'},
                                    'entetes_tableaux': {'0': 1}}))
        out = self.d / 'structure.docx'
        r = self.cli('structurer', str(self.source), str(out), '--spec', str(spec))
        self.assertEqual(r.returncode, 0, r.stderr)
        with zipfile.ZipFile(out) as z:
            root = ooxml.lire(z.read('word/document.xml'))
            self.assertEqual(''.join(t.text or '' for t in root.iter(q('w:t'))), text_before)
            self.assertEqual(next(root.iter(q('wp:docPr'))).get('descr'), 'Schéma fourni dans la synthèse.')
            self.assertIsNotNone(root.find('.//' + q('w:tblHeader')))
            self.assertIsNotNone(root.find('.//' + q('w:outlineLvl')))
        data = json.loads(self.cli('accessibilite', str(out)).stdout)
        self.assertNotIn('image_sans_alternative', [a['code'] for a in data['alertes']])
        self.assertNotIn('langue_absente', [a['code'] for a in data['alertes']])

    def test_fidelite_detecte_negation_supprimee_sans_suivi(self):
        with zipfile.ZipFile(self.source) as z:
            data = {n: z.read(n) for n in z.namelist()}
        root = ooxml.lire(data['word/document.xml'])
        t = next(root.iter(q('w:t')))
        t.text = 'Texte remplacé sans révision'
        data['word/document.xml'] = ET.tostring(root)
        out = self.d / 'texte-corrompu.docx'
        with zipfile.ZipFile(out, 'w') as z:
            for n, content in data.items():
                z.writestr(n, content)
        r = self.cli('verifier', str(out), '--original', str(self.source))
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertFalse(json.loads(r.stdout)['integrite']['texte_restituable'])

    def test_choix_couleur_texte_applique(self):
        with paquet.DossierTemporaire() as d:
            paquet.ouvrir(self.source, d)
            doc = ooxml.Document(d / 'word/document.xml')
            p = profil.appliquer_definitions({}, ['couleur_texte=333333'])
            forme.appliquer(doc, d, p)
            styles = ooxml.lire_fichier(d / 'word/styles.xml').getroot()
            self.assertEqual(styles.find('.//' + q('w:docDefaults') + '//' + q('w:color')).get(q('w:val')), '333333')


if __name__ == '__main__':
    unittest.main()
