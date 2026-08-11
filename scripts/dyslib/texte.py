"""Segmentation et chiffres — les deux interventions qui touchent au texte
sans en changer un mot.

Couper une phrase longue à ses articulations rend sa structure visible en
gardant exactement les mêmes mots. C'est à essayer avant toute reformulation.
"""

import re

from . import analyse, ooxml, suivi
from .ooxml import q

ESPACE_FINE = "\u202f"  # espace fine insécable : ne casse pas le nombre en fin de ligne

CONNECTEURS = sorted(analyse.CONNECTEURS, key=len, reverse=True)
MOTIF_CONNECTEUR = re.compile(
    r"(?<=[\s,;])(?:%s)\b" % "|".join(re.escape(c) for c in CONNECTEURS), re.I
)
MOTIF_RELATIF = re.compile(r",\s(?=qui\b|que\b|dont\b|lequel\b|laquelle\b)")
MOTIF_NOMBRE = re.compile(r"(?<![\d.,])\d{5,}(?![\d.,])")


def paragraphes_du_corps(document, portee=None):
    """Les paragraphes à traiter, éventuellement limités aux premiers blocs."""
    sortie = []
    for index, paragraphe in enumerate(document.paragraphes()):
        texte = ooxml.texte_paragraphe(paragraphe)
        if not texte.strip():
            continue
        sortie.append((index, paragraphe, texte))
    if portee:
        sortie = sortie[:portee]
    return sortie


# -- segmentation ----------------------------------------------------------


def segmenter(document, reviseur, profil, portee=None):
    seuil = int(profil.get("segmentation", {}).get("seuil_mots", 28))
    coupes = 0
    for index, paragraphe, texte in paragraphes_du_corps(document, portee):
        if len(analyse.MOT.findall(texte)) < seuil:
            continue
        offsets = points_de_coupe(texte, seuil)
        for offset in reversed(offsets):
            if suivi.inserer_saut(paragraphe, offset, reviseur, "phrase longue"):
                coupes += 1
        if offsets:
            reviseur.noter(
                "segmentation",
                "phrase de %s mots coupée à %s articulation(s)"
                % (len(analyse.MOT.findall(texte)), len(offsets)),
                index=index,
            )
    return coupes


def points_de_coupe(texte, seuil):
    """Où couper : aux connecteurs logiques, jamais au milieu d'un membre court."""
    points = []
    for debut, fin in _bornes_de_phrases(texte):
        phrase = texte[debut:fin]
        if len(analyse.MOT.findall(phrase)) <= seuil:
            continue
        candidats = [m.start() + debut for m in MOTIF_CONNECTEUR.finditer(phrase)]
        candidats += [m.end() + debut for m in MOTIF_RELATIF.finditer(phrase)]
        candidats += [m.end() + debut for m in re.finditer(r"\s:\s", phrase)]
        candidats = sorted(set(candidats))

        precedent = debut
        for candidat in candidats:
            gauche = len(analyse.MOT.findall(texte[precedent:candidat]))
            droite = len(analyse.MOT.findall(texte[candidat:fin]))
            if gauche >= 6 and droite >= 6:
                points.append(candidat)
                precedent = candidat
    return points


def _bornes_de_phrases(texte):
    bornes = []
    debut = 0
    for separateur in analyse.FIN_DE_PHRASE.finditer(texte):
        bornes.append((debut, separateur.start()))
        debut = separateur.end()
    bornes.append((debut, len(texte)))
    return [(a, b) for a, b in bornes if b > a]


# -- chiffres --------------------------------------------------------------


def grouper_chiffres(document, reviseur, portee=None):
    """1247893 -> 1 247 893. La valeur ne change pas, la lecture change.

    Le regroupement passe par une modification suivie : c'est du texte.
    Aucun chiffre n'est réécrit, aucun ordre de grandeur n'est arrondi.
    """
    faits = 0
    for index, paragraphe, texte in paragraphes_du_corps(document, portee):
        trouves = list(MOTIF_NOMBRE.finditer(texte))
        for correspondance in reversed(trouves):
            brut = correspondance.group(0)
            groupe = _grouper(brut)
            if groupe == brut:
                continue
            if suivi.remplacer_intervalle(
                paragraphe,
                correspondance.start(),
                correspondance.end(),
                groupe,
                reviseur,
                "regroupement des chiffres (valeur inchangée)",
            ):
                faits += 1
                reviseur.journal[-1]["index"] = index
    return faits


def _grouper(nombre):
    morceaux = []
    reste = nombre
    while len(reste) > 3:
        morceaux.insert(0, reste[-3:])
        reste = reste[:-3]
    morceaux.insert(0, reste)
    return ESPACE_FINE.join(morceaux)


def controle_des_valeurs(avant, apres):
    """Vérifie qu'aucune valeur numérique n'a bougé entre deux textes.

    Le regroupement n'est acceptable que si cette fonction reste vraie.
    """
    normaliser = lambda t: re.sub(r"[\s\u202f\u00a0]", "", t)
    return [
        normaliser(n) for n in re.findall(r"[\d\u202f\u00a0 ]*\d", avant)
    ] == [normaliser(n) for n in re.findall(r"[\d\u202f\u00a0 ]*\d", apres)]
