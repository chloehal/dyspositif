"""Un seul fil de lecture : jamais deux éléments à suivre en parallèle.

Au-delà de trois colonnes, un tableau demande de tenir une ligne et une
colonne en même temps. Deux réponses possibles, selon le profil : le signaler
en commentaire, ou le découper en tableaux de trois colonnes maximum.
"""

import copy
import re
import xml.etree.ElementTree as ET

from . import ooxml, paquet, suivi
from .ooxml import XML_ESPACE, q


def inventaire(document):
    tableaux = []
    for index, tableau in enumerate(document.tableaux()):
        grille = tableau.find(q("w:tblGrid"))
        colonnes = len(grille.findall(q("w:gridCol"))) if grille is not None else 0
        lignes = tableau.findall(q("w:tr"))
        fusions = any(
            cellule.find("./%s/%s" % (q("w:tcPr"), q("w:gridSpan"))) is not None
            or cellule.find("./%s/%s" % (q("w:tcPr"), q("w:vMerge"))) is not None
            for cellule in tableau.iter(q("w:tc"))
        )
        uniforme = all(
            len(ligne.findall(q("w:tc"))) == colonnes for ligne in lignes
        ) and colonnes > 0
        tableaux.append(
            {
                "index": index,
                "element": tableau,
                "colonnes": colonnes,
                "lignes": len(lignes),
                "fusions": fusions,
                "decoupable": uniforme and not fusions,
            }
        )
    return tableaux


def traiter(document, dossier, reviseur, profil):
    """Applique l'action choisie aux tableaux trop larges."""
    maxi = int(profil.get("tableaux", {}).get("max_colonnes", 3))
    action = profil.get("tableaux", {}).get("action", "signaler")
    resultats = []
    for infos in inventaire(document):
        if infos["colonnes"] <= maxi:
            continue
        if action == "decouper" and infos["decoupable"]:
            morceaux = decouper(document, reviseur, infos, maxi)
            resultats.append(
                {"index": infos["index"], "action": "découpé", "morceaux": morceaux}
            )
        else:
            raison = (
                "cellules fusionnées : un découpage automatique déformerait le tableau"
                if infos["fusions"]
                else "signalé sans découpage"
            )
            signaler(document, dossier, infos, raison)
            resultats.append(
                {"index": infos["index"], "action": "signalé", "raison": raison}
            )
        reviseur.noter(
            "tableau",
            "tableau de %s colonnes : %s"
            % (infos["colonnes"], resultats[-1]["action"]),
            index=infos["index"],
        )
    return resultats


# -- signaler --------------------------------------------------------------


def signaler(document, dossier, infos, raison):
    """Un commentaire Word sur la première cellule — aucun texte touché."""
    texte = (
        "Tableau de %s colonnes. Lire une ligne à la fois : repérer d'abord la "
        "colonne de gauche, puis avancer vers la droite. %s."
        % (infos["colonnes"], raison)
    )
    try:
        sortie = paquet.commenter(dossier, texte)
    except paquet.ErreurPaquet:
        return False
    identifiants = re.findall(r'w:id="(\d+)"', sortie)
    if not identifiants:
        return False
    identifiant = identifiants[0]

    premiere = infos["element"].find("./%s/%s" % (q("w:tr"), q("w:tc")))
    if premiere is None:
        return False
    paragraphe = premiere.find(q("w:p"))
    if paragraphe is None:
        return False

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
    return True


# -- découper --------------------------------------------------------------


def decouper(document, reviseur, infos, maxi):
    """Découpe en tableaux de `maxi` colonnes, première colonne répétée.

    L'original est marqué supprimé et les morceaux insérés : rejeter la
    modification dans Word restitue le tableau d'origine intact.
    """
    tableau = infos["element"]
    parents = document.parents()
    parent = parents.get(id(tableau))
    if parent is None:
        return 0

    grille = tableau.find(q("w:tblGrid"))
    colonnes = grille.findall(q("w:gridCol"))
    lignes = tableau.findall(q("w:tr"))
    restantes = list(range(1, len(colonnes)))
    paquets = [
        restantes[i: i + (maxi - 1)] for i in range(0, len(restantes), maxi - 1)
    ]

    entetes = _textes_de_ligne(lignes[0]) if lignes else []
    position = list(parent).index(tableau)
    inseres = []

    for rang, indices in enumerate(paquets):
        titres = [entetes[i] if i < len(entetes) else "" for i in indices]
        legende = "Partie %s sur %s — %s" % (
            rang + 1,
            len(paquets),
            ", ".join(t for t in titres if t) or "suite du tableau",
        )
        inseres.append(
            suivi.paragraphe_insere(None, [(legende, None)], reviseur)
        )
        inseres.append(_sous_tableau(tableau, [0] + indices, reviseur))

    # Word fusionne deux tableaux qui se touchent : un paragraphe les sépare.
    inseres.append(suivi.paragraphe_insere(None, [("", None)], reviseur))

    for decalage, element in enumerate(inseres):
        parent.insert(position + 1 + decalage, element)

    _marquer_tableau_supprime(tableau, reviseur)
    return len(paquets)


def _textes_de_ligne(ligne):
    return [
        " ".join(
            ooxml.texte_paragraphe(p).strip()
            for p in cellule.findall(q("w:p"))
        ).strip()
        for cellule in ligne.findall(q("w:tc"))
    ]


def _sous_tableau(tableau, indices, reviseur):
    nouveau = ET.Element(q("w:tbl"))
    proprietes = tableau.find(q("w:tblPr"))
    if proprietes is not None:
        nouveau.append(copy.deepcopy(proprietes))

    grille_source = tableau.find(q("w:tblGrid"))
    grille = ET.SubElement(nouveau, q("w:tblGrid"))
    colonnes = grille_source.findall(q("w:gridCol")) if grille_source is not None else []
    for index in indices:
        if index < len(colonnes):
            grille.append(copy.deepcopy(colonnes[index]))

    for ligne in tableau.findall(q("w:tr")):
        cellules = ligne.findall(q("w:tc"))
        nouvelle = ET.Element(q("w:tr"))
        proprietes_ligne = ligne.find(q("w:trPr"))
        proprietes_ligne = (
            copy.deepcopy(proprietes_ligne)
            if proprietes_ligne is not None
            else ET.Element(q("w:trPr"))
        )
        marque = ET.SubElement(proprietes_ligne, q("w:ins"))
        reviseur._attributs(marque)
        nouvelle.append(proprietes_ligne)
        for index in indices:
            if index < len(cellules):
                cellule = copy.deepcopy(cellules[index])
                _marquer_runs(cellule, reviseur, insertion=True)
                nouvelle.append(cellule)
        nouveau.append(nouvelle)
    return nouveau


def _marquer_tableau_supprime(tableau, reviseur):
    for ligne in tableau.findall(q("w:tr")):
        proprietes = ligne.find(q("w:trPr"))
        if proprietes is None:
            proprietes = ET.Element(q("w:trPr"))
            ligne.insert(0, proprietes)
        marque = ET.SubElement(proprietes, q("w:del"))
        reviseur._attributs(marque)
    _marquer_runs(tableau, reviseur, insertion=False)


def _marquer_runs(racine, reviseur, insertion):
    parents = {}
    for parent in racine.iter():
        for enfant in parent:
            parents[id(enfant)] = parent
    for run in list(racine.iter(q("w:r"))):
        parent = parents.get(id(run))
        if parent is None or parent.tag in (q("w:ins"), q("w:del")):
            continue
        position = list(parent).index(run)
        parent.remove(run)
        if insertion:
            parent.insert(position, reviseur.insertion([run]))
        else:
            parent.insert(position, reviseur.suppression([run]))
