"""Numérotation Word sémantique pour les nouvelles listes confirmées."""
import xml.etree.ElementTree as ET
from . import ooxml
from .ooxml import q


def ajouter(dossier, numeroter=False, compteur=False):
    chemin = dossier / 'word/numbering.xml'
    if chemin.is_file():
        document = ooxml.Document(chemin)
        racine = document.racine
    else:
        document = None
        racine = ET.Element(q('w:numbering'))
    def suivant(nom, attribut):
        return max([int(e.get(q(attribut))) for e in racine.findall(q(nom))] + [0]) + 1
    abstract_id = suivant('w:abstractNum', 'w:abstractNumId')
    num_id = suivant('w:num', 'w:numId')
    abstrait = ET.Element(q('w:abstractNum'), {q('w:abstractNumId'): str(abstract_id)})
    ET.SubElement(abstrait, q('w:multiLevelType'), {q('w:val'): 'singleLevel'})
    niveau = ET.SubElement(abstrait, q('w:lvl'), {q('w:ilvl'): '0'})
    for nom, valeur in [('w:start','1'), ('w:numFmt', 'none' if compteur else 'decimal' if numeroter else 'bullet'),
                        ('w:lvlText', '' if compteur else '%1.' if numeroter else '•'), ('w:lvlJc','left')]:
        ET.SubElement(niveau, q(nom), {q('w:val'): valeur})
    indice = next((i for i, e in enumerate(racine) if e.tag in (q('w:num'), q('w:numIdMacAtCleanup'))), len(racine))
    racine.insert(indice, abstrait)
    num = ET.Element(q('w:num'), {q('w:numId'): str(num_id)})
    ET.SubElement(num, q('w:abstractNumId'), {q('w:val'): str(abstract_id)})
    indice = next((i for i, e in enumerate(racine) if e.tag == q('w:numIdMacAtCleanup')), len(racine))
    racine.insert(indice, num)
    if document:
        document.enregistrer()
    else:
        ET.ElementTree(racine).write(chemin, encoding='UTF-8', xml_declaration=True)
    rels = ooxml.Document(dossier / 'word/_rels/document.xml.rels')
    relation_type = ooxml.NS['r'] + '/numbering'
    if not any(e.get('Type') == relation_type for e in rels.racine):
        ids = {e.get('Id') for e in rels.racine}
        i = 1
        while 'rId%s' % i in ids:
            i += 1
        ET.SubElement(rels.racine, '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',
                      Id='rId%s' % i, Type=relation_type, Target='numbering.xml')
        rels.enregistrer()
    types = ooxml.Document(dossier / '[Content_Types].xml')
    if not any(e.get('PartName') == '/word/numbering.xml' for e in types.racine):
        ET.SubElement(types.racine, '{http://schemas.openxmlformats.org/package/2006/content-types}Override',
                      PartName='/word/numbering.xml', ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml')
        types.enregistrer()
    return num_id
