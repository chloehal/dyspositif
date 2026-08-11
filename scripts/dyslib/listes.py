"""Révéler une liste enfouie — pas en inventer une.

« les conditions sont l'urgence, la proportionnalité, la nécessité et la
subsidiarité » contient une liste de quatre. La sortir et la numéroter
n'invente rien, et savoir qu'il y en a quatre, c'est pouvoir vérifier qu'on
n'en oublie aucune.

En cas de doute sur le fait qu'une énumération en soit vraiment une, on
s'abstient : une fausse liste désoriente plus qu'un paragraphe dense.
"""

import copy
import xml.etree.ElementTree as ET

from . import analyse, ooxml, suivi
from .ooxml import ORDRE_PPR, q


def candidats(document, portee=None):
    """Énumérations repérées, avec leur position exacte — à confirmer avant d'agir."""
    trouves = []
    for index, paragraphe in enumerate(document.paragraphes()):
        texte = ooxml.texte_paragraphe(paragraphe)
        if not texte.strip():
            continue
        detection = analyse.detecter_liste_enfouie(texte)
        if not detection or not detection.get("elements"):
            continue
        elements = detection["elements"]
        debut = texte.find(elements[0])
        fin = texte.rfind(elements[-1])
        if debut < 0 or fin < 0:
            continue
        fin += len(elements[-1])
        trouves.append(
            {
                "paragraphe": index,
                "elements": elements,
                "nombre": len(elements),
                "debut": debut,
                "fin": fin,
                "texte": texte[max(0, debut - 60): fin + 20],
                "certitude": detection.get("certitude"),
            }
        )
    if portee:
        trouves = [t for t in trouves if t["paragraphe"] < portee]
    return trouves


def appliquer(document, reviseur, specifications, profil):
    """Sort les listes confirmées. `specifications` vient de `candidats`, filtrée."""
    groupe_de = int(profil.get("listes", {}).get("grouper_par", 0) or 0)
    compteur = bool(profil.get("listes", {}).get("compteur"))
    faits = 0

    paragraphes = list(document.paragraphes())
    parents = document.parents()

    for specification in sorted(
        specifications, key=lambda s: s["paragraphe"], reverse=True
    ):
        index = specification["paragraphe"]
        if index >= len(paragraphes):
            continue
        paragraphe = paragraphes[index]
        texte = ooxml.texte_paragraphe(paragraphe)
        elements = specification["elements"]
        debut, fin = specification["debut"], specification["fin"]
        if texte[debut:fin] != "".join(texte[debut:fin]):
            continue

        remplacement = " :"
        if fin < len(texte) and texte[fin] in ".;":
            fin += 1
        if debut > 0 and texte[debut - 1] == " ":
            debut -= 1

        if not suivi.remplacer_intervalle(
            paragraphe, debut, fin, remplacement, reviseur,
            "énumération sortie en liste (%s éléments)" % len(elements),
        ):
            continue

        parent = parents.get(id(paragraphe))
        if parent is None:
            continue
        position = list(parent).index(paragraphe)
        modele = _modele_de_liste(paragraphe)

        inseres = []
        for rang, element in enumerate(elements):
            if groupe_de and rang and rang % groupe_de == 0:
                inseres.append(suivi.paragraphe_insere(None, [("", None)], reviseur))
            if compteur:
                ligne = "%s sur %s — %s" % (rang + 1, len(elements), element)
            else:
                ligne = "%s. %s" % (rang + 1, element)
            inseres.append(
                suivi.paragraphe_insere(modele, [(ligne, None)], reviseur)
            )

        for decalage, element in enumerate(inseres):
            parent.insert(position + 1 + decalage, element)
        faits += 1
        reviseur.noter(
            "liste",
            "%s éléments sortis et numérotés%s"
            % (len(elements), ", groupés par %s" % groupe_de if groupe_de else ""),
            index=index,
        )
    return faits


def _modele_de_liste(paragraphe):
    """pPr d'un élément de liste : retrait, pas de numérotation Word héritée."""
    proprietes = paragraphe.find(q("w:pPr"))
    modele = copy.deepcopy(proprietes) if proprietes is not None else ET.Element(q("w:pPr"))
    for nom in ("w:numPr", "w:pStyle"):
        for enfant in modele.findall(q(nom)):
            modele.remove(enfant)
    retrait = modele.find(q("w:ind"))
    if retrait is None:
        index = ORDRE_PPR.index("w:ind")
        retrait = ET.Element(q("w:ind"))
        position = len(modele)
        for i, enfant in enumerate(modele):
            nom = ooxml._nom_court(enfant.tag)
            if nom in ORDRE_PPR and ORDRE_PPR.index(nom) > index:
                position = i
                break
        modele.insert(position, retrait)
    retrait.set(q("w:left"), "454")
    retrait.set(q("w:hanging"), "227")
    return modele
