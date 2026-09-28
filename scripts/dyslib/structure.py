"""Appliquer des annotations structurelles confirmées, sans créer de contenu."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from . import ooxml, paquet
from .ooxml import q, poser_enfant, ORDRE_PPR, ORDRE_RPR


def appliquer(source, sortie, spec):
    if Path(source).resolve() == Path(sortie).resolve():
        raise ValueError('Conserver la source sous un autre nom.')
    if not isinstance(spec, dict) or set(spec) - {'langue', 'titres', 'alternatives', 'entetes_tableaux'}:
        raise ValueError('Spécification attendue : langue, titres, alternatives, entetes_tableaux.')
    with paquet.DossierTemporaire() as d:
        paquet.ouvrir(source, d)
        doc = ooxml.Document(d / 'word/document.xml')
        paragraphes = list(doc.paragraphes())
        for brut, niveau in spec.get('titres', {}).items():
            index = int(brut)
            if not 0 <= index < len(paragraphes) or type(niveau) is not int or not 1 <= niveau <= 6:
                raise ValueError('Titre : index de paragraphe ou niveau invalide.')
            if not ooxml.texte_paragraphe(paragraphes[index]).strip():
                raise ValueError('Un titre doit déjà contenir du texte.')
            poser_enfant(ooxml.ppr(paragraphes[index], True), 'w:outlineLvl', ORDRE_PPR, val=niveau-1)
        images = list(doc.racine.iter(q('wp:docPr')))
        for identifiant, texte in spec.get('alternatives', {}).items():
            cibles = [e for e in images if e.get('id') == str(identifiant)]
            if len(cibles) != 1 or not isinstance(texte, str) or not texte.strip():
                raise ValueError('Alternative : identifiant unique et description confirmée non vide requis.')
            cibles[0].set('descr', texte)
        tables = list(doc.tableaux())
        for brut, nombre in spec.get('entetes_tableaux', {}).items():
            index = int(brut)
            if not 0 <= index < len(tables) or type(nombre) is not int:
                raise ValueError('Index de tableau ou nombre de lignes invalide.')
            lignes = tables[index].findall(q('w:tr'))
            if not 1 <= nombre <= len(lignes):
                raise ValueError('Nombre de lignes d’en-tête hors du tableau.')
            for ligne in lignes[:nombre]:
                prop = ligne.find(q('w:trPr'))
                if prop is None:
                    prop = ET.Element(q('w:trPr'))
                    ligne.insert(0, prop)
                poser_enfant(prop, 'w:tblHeader', ['w:cnfStyle', 'w:divId', 'w:gridBefore', 'w:gridAfter', 'w:wBefore', 'w:wAfter', 'w:cantSplit', 'w:trHeight', 'w:tblHeader', 'w:tblCellSpacing', 'w:jc', 'w:hidden', 'w:ins', 'w:del', 'w:trPrChange'])
        if 'langue' in spec:
            langue = spec['langue']
            if not isinstance(langue, str) or not re.fullmatch(r'[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', langue):
                raise ValueError('Langue attendue : par exemple fr-BE.')
            chemin = d / 'word/styles.xml'
            if not chemin.is_file():
                raise ValueError('styles.xml absent : renseigner la langue dans le traitement de texte.')
            styles = ooxml.Document(chemin)
            defauts = styles.racine.find(q('w:docDefaults'))
            if defauts is None:
                defauts = ET.Element(q('w:docDefaults'))
                styles.racine.insert(0, defauts)
            rdef = defauts.find(q('w:rPrDefault'))
            if rdef is None:
                rdef = ET.Element(q('w:rPrDefault'))
                defauts.insert(0, rdef)
            prop = rdef.find(q('w:rPr'))
            if prop is None:
                prop = ET.SubElement(rdef, q('w:rPr'))
            poser_enfant(prop, 'w:lang', ORDRE_RPR, val=langue)
            styles.enregistrer()
        doc.enregistrer()
        paquet.refermer(d, sortie)
    return {'sortie': str(sortie), 'applique': spec,
            'limite': 'Niveaux de plan et descriptions confirmés ; tester navigation, langue des passages et ordre de lecture.'}
