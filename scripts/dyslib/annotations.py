"""Commentaires Word — le seul endroit où la skill a le droit d'ajouter du sien.

Un commentaire est sans ambiguïté une annotation : impossible de le confondre
avec le cours du professeur, et l'utilisateur le supprime d'un clic. Les moyens
mnémotechniques et les avertissements passent par là, jamais par le corps du texte.
"""

import re
import xml.etree.ElementTree as ET

from . import paquet
from .ooxml import q


def poser_sur_paragraphe(dossier, paragraphe, texte, auteur="dyspositif"):
    """Crée le commentaire et pose ses marqueurs autour du paragraphe."""
    sortie = paquet.commenter(dossier, texte, auteur=auteur)
    identifiants = re.findall(r'w:id="(\d+)"', sortie)
    if not identifiants:
        return None
    identifiant = identifiants[0]

    debut = ET.Element(q("w:commentRangeStart"))
    debut.set(q("w:id"), identifiant)
    fin = ET.Element(q("w:commentRangeEnd"))
    fin.set(q("w:id"), identifiant)

    reference = ET.Element(q("w:r"))
    proprietes = ET.SubElement(reference, q("w:rPr"))
    style = ET.SubElement(proprietes, q("w:rStyle"))
    style.set(q("w:val"), "CommentReference")
    marque = ET.SubElement(reference, q("w:commentReference"))
    marque.set(q("w:id"), identifiant)

    position = 1 if len(paragraphe) and paragraphe[0].tag == q("w:pPr") else 0
    paragraphe.insert(position, debut)
    paragraphe.append(fin)
    paragraphe.append(reference)
    return identifiant


def paragraphe_par_index(document, index):
    for numero, paragraphe in enumerate(document.paragraphes()):
        if numero == index:
            return paragraphe
    return None
