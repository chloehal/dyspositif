"""Contrôles structurels et contrastes partiels : jamais une certification."""
import re
from . import ooxml, paquet, forme
from .ooxml import q


def analyser(source):
    alertes = []
    def signaler(code, detail, **position):
        alertes.append(dict(code=code, detail=detail, **position))
    with paquet.DossierTemporaire() as d:
        paquet.ouvrir(source, d)
        doc = ooxml.Document(d / 'word/document.xml')
        root = doc.racine
        bg = root.find(q('w:background'))
        fond = bg.get(q('w:color'), 'FFFFFF') if bg is not None else 'FFFFFF'
        roots = [('word/document.xml', root)]
        for p in sorted((d / 'word').glob('*.xml')):
            if p.name != 'document.xml':
                roots.append(('word/' + p.name, ooxml.lire_fichier(p).getroot()))
        for partie, racine in roots:
            for i, image in enumerate(racine.iter(q('wp:docPr'))):
                if not (image.get('descr') or '').strip():
                    signaler('image_sans_alternative', 'Vérifier puis décrire le visuel, sans inventer son contenu.', partie=partie, image=i, id=image.get('id'))
            for i, image in enumerate(racine.iter(q('v:imagedata'))):
                signaler('image_ancienne', 'Alternative et ordre de lecture à vérifier pour ce visuel VML.', partie=partie, image=i)
            for couleur in racine.iter(q('w:color')):
                texte = couleur.get(q('w:val'), '')
                if re.fullmatch('[0-9A-Fa-f]{6}', texte) and re.fullmatch('[0-9A-Fa-f]{6}', fond):
                    ratio = forme.contraste(texte, fond)
                    if ratio < 4.5:
                        signaler('contraste_a_verifier', 'Contraste avec le fond de page ; vérifier surlignage et fond local avant correction.', partie=partie, couleur=texte, fond=fond, ratio=round(ratio, 2))
            if any(True for _ in racine.iter(q('w:shd'))) or any(True for _ in racine.iter(q('w:highlight'))):
                signaler('fonds_locaux', 'Des fonds ou surlignages nécessitent un contrôle du contraste dans le rendu.', partie=partie)
        styles_path = d / 'word/styles.xml'
        styles = ooxml.lire_fichier(styles_path).getroot() if styles_path.is_file() else None
        if not any(True for _, r in roots for _ in r.iter(q('w:lang'))):
            signaler('langue_absente', 'Renseigner la langue confirmée pour la prononciation.')
        niveaux = []
        for p in doc.paragraphes():
            st = p.find('./' + q('w:pPr') + '/' + q('w:pStyle'))
            outline = p.find('./' + q('w:pPr') + '/' + q('w:outlineLvl'))
            if outline is None and st is not None and styles is not None:
                style = next((s for s in styles.findall(q('w:style')) if s.get(q('w:styleId')) == st.get(q('w:val'))), None)
                outline = style.find('.//' + q('w:outlineLvl')) if style is not None else None
            if outline is not None and outline.get(q('w:val'), '').isdigit():
                niveaux.append(int(outline.get(q('w:val'))) + 1)
        if not niveaux:
            signaler('titres_non_verifies', 'Aucun niveau de plan détecté ; confirmer les titres utiles à la navigation.')
        if any(b > a + 1 for a, b in zip(niveaux, niveaux[1:])):
            signaler('saut_niveau', 'Vérifier la hiérarchie des titres.')
        for i, table in enumerate(doc.tableaux()):
            if table.find('.//' + q('w:tblHeader')) is None:
                signaler('entete_tableau_absente', 'Confirmer quelles lignes sont des en-têtes avant de les baliser.', tableau=i)
            if any(True for tag in ('w:vMerge', 'w:gridSpan') for _ in table.iter(q(tag))):
                signaler('tableau_complexe', 'Tester les relations entre cellules au lecteur d’écran.', tableau=i)
        if any(True for _ in root.iter(q('wp:anchor'))):
            signaler('objet_flottant', 'Vérifier l’ordre de lecture des objets flottants.')
    return {'certification': False, 'verdict': 'a_verifier', 'alertes': alertes,
            'verification_humaine': ['Rendu dans le logiciel cible et au grossissement habituel.',
                                    'Ordre de lecture, liens, listes et tableaux avec le moyen d’accès utilisé.',
                                    'Fidélité du sens et utilité des adaptations avec la personne.']}
