"""Modifications suivies : toute modification du texte passe par ici.

L'utilisateur doit voir l'original juste à côté et pouvoir rejeter chaque
changement un par un dans Word. Un module d'écriture qui contournerait ce
fichier casserait la garantie principale de la skill.
"""

import copy
from datetime import datetime

import xml.etree.ElementTree as ET

from . import ooxml
from .ooxml import q, XML_ESPACE


class Reviseur(object):
    def __init__(self, document, auteur="dyspositif", date=None):
        self.document = document
        self.auteur = auteur
        self.date = date or datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self._compteur = document.prochain_id_revision()
        self.journal = []

    # -- primitives -------------------------------------------------------

    def _id(self):
        valeur = self._compteur
        self._compteur += 1
        return valeur

    def _attributs(self, element):
        element.set(q("w:id"), str(self._id()))
        element.set(q("w:author"), self.auteur)
        element.set(q("w:date"), self.date)
        return element

    def insertion(self, runs):
        element = self._attributs(ET.Element(q("w:ins")))
        for run in runs:
            element.append(run)
        return element

    def suppression(self, runs):
        element = self._attributs(ET.Element(q("w:del")))
        for run in runs:
            for t in run.iter(q("w:t")):
                t.tag = q("w:delText")
            element.append(run)
        return element

    def marque_paragraphe_insere(self, paragraphe):
        """Marque de paragraphe insérée : sans elle, le paragraphe neuf n'est pas suivi."""
        proprietes = ooxml.ppr(paragraphe, creer_si_absent=True)
        rpr = proprietes.find(q("w:rPr"))
        if rpr is None:
            rpr = ET.Element(q("w:rPr"))
            proprietes.append(rpr)
        marque = ET.Element(q("w:ins"))
        self._attributs(marque)
        rpr.insert(0, marque)  # w:ins doit précéder les autres enfants de rPr
        return paragraphe

    def noter(self, genre, detail, avant=None, apres=None, index=None):
        self.journal.append(
            {
                "genre": genre,
                "detail": detail,
                "avant": avant,
                "apres": apres,
                "paragraphe": index,
            }
        )


# -- repérage du texte dans les runs --------------------------------------


def segments(paragraphe):
    """[(run, parent, texte, debut, fin)] pour les runs simples porteurs de texte.

    On ignore les runs déjà pris dans une révision et ceux qui mêlent texte et
    autre chose : les découper serait risqué pour un gain nul.
    """
    parents = {}
    for parent in paragraphe.iter():
        for enfant in parent:
            parents[id(enfant)] = parent

    interdits = set()
    for revision in list(paragraphe.iter(q("w:del"))) + list(paragraphe.iter(q("w:ins"))):
        for run in revision.iter(q("w:r")):
            interdits.add(id(run))

    sortie = []
    position = 0
    for run in paragraphe.iter(q("w:r")):
        enfants = [e for e in run if e.tag != q("w:rPr")]
        texte = ""
        if len(enfants) == 1 and enfants[0].tag == q("w:t"):
            texte = enfants[0].text or ""
        else:
            for enfant in enfants:
                if enfant.tag == q("w:t"):
                    texte += enfant.text or ""
                elif enfant.tag == q("w:tab"):
                    texte += "\t"
        if not texte:
            continue
        if id(run) in interdits or len(enfants) != 1 or enfants[0].tag != q("w:t"):
            position += len(texte)
            continue
        sortie.append(
            {
                "run": run,
                "parent": parents.get(id(run), paragraphe),
                "texte": texte,
                "debut": position,
                "fin": position + len(texte),
            }
        )
        position += len(texte)
    return sortie


def _nouveau_run(modele, contenu):
    run = ET.Element(q("w:r"))
    proprietes = modele.find(q("w:rPr"))
    if proprietes is not None:
        run.append(copy.deepcopy(proprietes))
    t = ET.SubElement(run, q("w:t"))
    t.text = contenu
    t.set(XML_ESPACE, "preserve")
    return run


def remplacer_intervalle(paragraphe, debut, fin, nouveau_texte, reviseur, motif=""):
    """Remplace [debut, fin[ du texte du paragraphe par `nouveau_texte`, en suivi.

    L'ancien texte part dans un <w:del>, le nouveau arrive dans un <w:ins> :
    rejeter la modification restitue exactement l'original.
    """
    touches = [
        s for s in segments(paragraphe) if s["debut"] < fin and s["fin"] > debut
    ]
    if not touches:
        return False

    premier, dernier = touches[0], touches[-1]
    prefixe = premier["texte"][: max(0, debut - premier["debut"])]
    suffixe = dernier["texte"][max(0, fin - dernier["debut"]):]
    ancien = "".join(
        s["texte"][
            max(0, debut - s["debut"]): len(s["texte"]) - max(0, s["fin"] - fin)
        ]
        for s in touches
    )
    if not ancien:
        return False

    parent = premier["parent"]
    if any(s["parent"] is not parent for s in touches):
        return False
    position = list(parent).index(premier["run"])

    for s in touches:
        parent.remove(s["run"])

    nouveaux = []
    if prefixe:
        nouveaux.append(_nouveau_run(premier["run"], prefixe))
    nouveaux.append(reviseur.suppression([_nouveau_run(premier["run"], ancien)]))
    if nouveau_texte:
        nouveaux.append(
            reviseur.insertion([_nouveau_run(premier["run"], nouveau_texte)])
        )
    if suffixe:
        nouveaux.append(_nouveau_run(dernier["run"], suffixe))

    for decalage, element in enumerate(nouveaux):
        parent.insert(position + decalage, element)

    reviseur.noter("texte", motif, avant=ancien, apres=nouveau_texte)
    return True


def inserer_saut(paragraphe, offset, reviseur, motif="segmentation"):
    """Coupe la ligne à `offset` — mêmes mots, structure rendue visible."""
    cible = None
    for s in segments(paragraphe):
        if s["debut"] < offset <= s["fin"]:
            cible = s
            break
    if cible is None:
        return False

    parent = cible["parent"]
    position = list(parent).index(cible["run"])
    coupe = offset - cible["debut"]
    avant = cible["texte"][:coupe]
    apres = cible["texte"][coupe:]
    if not avant.strip() or not apres.strip():
        return False

    parent.remove(cible["run"])
    saut = ET.Element(q("w:r"))
    proprietes = cible["run"].find(q("w:rPr"))
    if proprietes is not None:
        saut.append(copy.deepcopy(proprietes))
    ET.SubElement(saut, q("w:br"))

    # Le texte doit rester identique au caractère près : on ne rogne rien,
    # on insère seulement un saut de ligne entre deux morceaux intacts.
    elements = [
        _nouveau_run(cible["run"], avant),
        reviseur.insertion([saut]),
        _nouveau_run(cible["run"], apres),
    ]

    for decalage, element in enumerate(elements):
        parent.insert(position + decalage, element)
    reviseur.noter("segmentation", motif, avant=None, apres=None)
    return True


def paragraphe_insere(modele_ppr, morceaux, reviseur):
    """Fabrique un paragraphe entièrement marqué comme inséré.

    `morceaux` : liste de (texte, rpr_modele_ou_None).
    """
    paragraphe = ET.Element(q("w:p"))
    if modele_ppr is not None:
        paragraphe.append(copy.deepcopy(modele_ppr))
    runs = []
    for texte, modele in morceaux:
        run = ET.Element(q("w:r"))
        if modele is not None:
            run.append(copy.deepcopy(modele))
        t = ET.SubElement(run, q("w:t"))
        t.text = texte
        t.set(XML_ESPACE, "preserve")
        runs.append(run)
    paragraphe.append(reviseur.insertion(runs))
    reviseur.marque_paragraphe_insere(paragraphe)
    return paragraphe


def supprimer_paragraphe(paragraphe, reviseur):
    """Suppression suivie : runs dans <w:del> et marque de paragraphe supprimée."""
    parents = {}
    for parent in paragraphe.iter():
        for enfant in parent:
            parents[id(enfant)] = parent

    for run in list(paragraphe.iter(q("w:r"))):
        parent = parents.get(id(run), paragraphe)
        if parent.tag in (q("w:del"), q("w:ins")):
            continue
        position = list(parent).index(run)
        parent.remove(run)
        parent.insert(position, reviseur.suppression([run]))

    proprietes = ooxml.ppr(paragraphe, creer_si_absent=True)
    rpr = proprietes.find(q("w:rPr"))
    if rpr is None:
        rpr = ET.Element(q("w:rPr"))
        proprietes.append(rpr)
    marque = ET.Element(q("w:del"))
    reviseur._attributs(marque)
    rpr.insert(0, marque)
    return paragraphe
