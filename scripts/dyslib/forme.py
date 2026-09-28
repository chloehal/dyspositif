"""Mise en forme : le degré le plus utile et le moins risqué.

Rien ici ne touche à un mot du cours. Ces changements n'ont donc pas à passer
par les modifications suivies — ils ne modifient aucun texte.
Justification de chaque paramètre : references/reglages.md
"""

import copy
import re
import xml.etree.ElementTree as ET

from . import analyse, ooxml
from .ooxml import ORDRE_PPR, ORDRE_RPR, XML_ESPACE, poser_enfant, q

FONDS = {
    "blanc": ("FFFFFF", "1A1A1A"),
    "creme": ("FBF6EC", "24211C"),
    "sombre": ("22262B", "E7E3DC"),
}

PALETTE_FILETS = ["1D4ED8", "047857", "C2410C", "6D28D9", "B91C1C", "A16207"]

PALETTE_LIBRE = ["C2410C", "6D28D9", "0B6E4F", "A16207", "BE185D", "1D4ED8"]

POLICES_SYMBOLES = {"symbol", "wingdings", "wingdings 2", "wingdings 3", "webdings"}

LETTRES_MIROIR = "bdpq"
CHIFFRES_CONFONDUS = "38 17"


def contraste(texte, fond):
    def luminance(couleur):
        rgb = [int(couleur[i:i+2], 16) / 255 for i in (0, 2, 4)]
        rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
        return sum(v * poids for v, poids in zip(rgb, (.2126, .7152, .0722)))
    bas, haut = sorted((luminance(texte), luminance(fond)))
    return (haut + .05) / (bas + .05)


def couleur_texte(profil):
    choisie = profil.get("couleur_texte", "auto")
    return FONDS[profil["fond"]][1] if choisie == "auto" else choisie


def couleur_libre(profil, souhaitee):
    """Couleur ajoutée : contraste >= 4.5 et aucun code personnel réutilisé."""
    prises = {v.upper() for v in (profil.get("couleurs_utilisateur") or {}).values()}
    fond = profil.get("fond_effectif", FONDS[profil["fond"]][0])
    for candidate in [souhaitee] + PALETTE_LIBRE + ["FDBA74", "C4B5FD", "6EE7B7", "FDE68A", "F9A8D4", "93C5FD", "FFFFFF", "000000"]:
        if candidate and candidate.upper() not in prises and contraste(candidate, fond) >= 4.5:
            return candidate.upper()
    raise ValueError("Aucune teinte disponible : conserver le texte sans repère coloré.")


def _actif(profil, cle):
    return profil.get("decisions", {}).get(cle, {}).get("etat") in ("valide", "refuse", "essai")


def appliquer(document, dossier, profil, rapport=None):
    """Ne modifier que les propriétés choisies ou explicitement essayées."""
    profil = copy.deepcopy(profil)
    fond = document.racine.find(q("w:background"))
    profil["fond_effectif"] = (FONDS[profil["fond"]][0] if _actif(profil, "fond") else
                              fond.get(q("w:color"), "FFFFFF") if fond is not None else "FFFFFF")
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", profil["fond_effectif"]):
        raise ValueError("Fond de page non résolu : vérifier la couleur effective avant adaptation.")
    ancienne_taille = _taille_par_defaut(dossier)
    ratio = float(profil["taille_pt"]) / ancienne_taille if ancienne_taille and _actif(profil, "taille_pt") else 1.0
    faits = {"styles": _styles(dossier, profil, ratio),
             "formatage_direct": _neutraliser_formatage_direct(document, profil, ratio)}
    if _actif(profil, "longueur_ligne") or _actif(profil, "marge_annotation"):
        # Calcul de marge sur la taille réelle si aucun nouveau corps choisi.
        geometrie = dict(profil)
        if not _actif(profil, "taille_pt"):
            geometrie["taille_pt"] = ancienne_taille
        faits["marges"] = _longueur_de_ligne(document, geometrie)
    if _actif(profil, "fond"):
        faits["fond"] = _fond(document, dossier, profil)
    if _actif(profil, "air_proportionnel"):
        faits["air"] = _air_proportionnel(document, profil)
    if profil.get("filet_section") and _actif(profil, "filet_section"):
        faits["filets"] = _filets_de_section(document, profil)
    if profil.get("lettres_miroir", {}).get("actif") and _actif(profil, "lettres_miroir.actif"):
        faits["lettres_miroir"] = _teinter(document, LETTRES_MIROIR, couleur_libre(profil, profil["lettres_miroir"]["teinte"]))
    if profil.get("chiffres", {}).get("paires") and _actif(profil, "chiffres.paires"):
        faits["paires_chiffres"] = _teinter(document, CHIFFRES_CONFONDUS.replace(" ", ""), couleur_libre(profil, profil["chiffres"]["teinte"]), chiffres=True)
    return faits


# -- styles ----------------------------------------------------------------


def _chemin_styles(dossier):
    return dossier / "word" / "styles.xml"


def _taille_par_defaut(dossier):
    chemin = _chemin_styles(dossier)
    if not chemin.is_file():
        return 11.0
    racine = ooxml.lire_fichier(chemin).getroot()
    defauts = racine.find("./%s/%s/%s" % (q("w:docDefaults"), q("w:rPrDefault"), q("w:rPr")))
    if defauts is not None:
        taille = defauts.find(q("w:sz"))
        if taille is not None and (taille.get(q("w:val")) or "").isdigit():
            return int(taille.get(q("w:val"))) / 2.0
    return 11.0


def _regler_rpr(rpr, profil, ratio, defaut=False):
    if _actif(profil, "police"):
        police = rpr.find(q("w:rFonts"))
        if (police is not None and not _est_symbole(police)) or (police is None and defaut):
            police = poser_enfant(rpr, "w:rFonts", ORDRE_RPR, ascii=profil["police"], hAnsi=profil["police"], cs=profil["police"])
            for attr in ("asciiTheme", "hAnsiTheme", "cstheme"):
                police.attrib.pop(q("w:" + attr), None)
    if _actif(profil, "taille_pt"):
        for nom in ("w:sz", "w:szCs"):
            taille = rpr.find(q(nom))
            if taille is not None and (taille.get(q("w:val")) or "").isdigit():
                taille.set(q("w:val"), str(_arrondir_taille(taille, ratio)))
            elif defaut:
                poser_enfant(rpr, nom, ORDRE_RPR, val=int(round(profil["taille_pt"]*2)))
    if _actif(profil, "espacement_lettres_pt"):
        poser_enfant(rpr, "w:spacing", ORDRE_RPR, val=int(round(profil["espacement_lettres_pt"] * 20)))
    if defaut and (_actif(profil, "fond") or _actif(profil, "couleur_texte")):
        poser_enfant(rpr, "w:color", ORDRE_RPR, val=couleur_texte(profil))


def _regler_ppr(ppr, profil):
    if _actif(profil, "interligne"):
        poser_enfant(ppr, "w:spacing", ORDRE_PPR, line=int(round(profil["interligne"]*240)), lineRule="auto")
    if _actif(profil, "alignement") and profil["alignement"] == "gauche":
        poser_enfant(ppr, "w:jc", ORDRE_PPR, val="left")


def _styles(dossier, profil, ratio):
    chemin = _chemin_styles(dossier)
    if not chemin.is_file():
        return 0
    fichier = ooxml.Document(chemin)
    racine = fichier.racine
    defauts = racine.find(q("w:docDefaults"))
    if defauts is None:
        defauts = ET.Element(q("w:docDefaults"))
        racine.insert(0, defauts)
    for parent_nom, nom, regler in [("w:rPrDefault", "w:rPr", lambda p: _regler_rpr(p, profil, ratio, True)),
                                    ("w:pPrDefault", "w:pPr", lambda p: _regler_ppr(p, profil))]:
        parent = defauts.find(q(parent_nom))
        if parent is None:
            parent = ET.Element(q(parent_nom))
            defauts.insert(0 if parent_nom == "w:rPrDefault" else len(defauts), parent)
        prop = parent.find(q(nom))
        if prop is None:
            prop = ET.SubElement(parent, q(nom))
        regler(prop)
    for style in racine.findall(q("w:style")):
        rp, pp = style.find(q("w:rPr")), style.find(q("w:pPr"))
        if rp is not None:
            _regler_rpr(rp, profil, ratio)
        if pp is not None:
            _regler_ppr(pp, profil)
    fichier.enregistrer()
    return len(racine.findall(q("w:style")))


def _arrondir_taille(element, ratio):
    valeur = int(element.get(q("w:val")))
    return max(16, int(round(valeur * ratio / 2.0)) * 2)


def _est_symbole(police):
    for attribut in ("ascii", "hAnsi"):
        valeur = (police.get(q("w:" + attribut)) or "").lower()
        if valeur in POLICES_SYMBOLES:
            return True
    return False


# -- formatage direct ------------------------------------------------------


def _neutraliser_formatage_direct(document, profil, ratio):
    touches = 0
    for run in document.racine.iter(q("w:r")):
        proprietes = run.find(q("w:rPr"))
        if proprietes is not None:
            avant = ET.tostring(proprietes)
            _regler_rpr(proprietes, profil, ratio)
            touches += avant != ET.tostring(proprietes)
    if _actif(profil, "interligne") or _actif(profil, "alignement"):
        for paragraphe in document.paragraphes():
            prop = ooxml.ppr(paragraphe, True)
            avant = ET.tostring(prop)
            _regler_ppr(prop, profil)
            touches += avant != ET.tostring(prop)
    return touches


# -- géométrie de la page --------------------------------------------------


def _longueur_de_ligne(document, profil):
    """Raccourcir la ligne est ce qui est le mieux établi contre la perte de ligne."""
    largeur_caractere = 0.52 * profil["taille_pt"] * 20  # twips, largeur moyenne
    largeur_texte = int(profil["longueur_ligne"] * largeur_caractere)
    touches = 0
    for sect in document.racine.iter(q("w:sectPr")):
        taille = sect.find(q("w:pgSz"))
        largeur_page = 11906
        if taille is not None and (taille.get(q("w:w")) or "").isdigit():
            largeur_page = int(taille.get(q("w:w")))
        marge = sect.find(q("w:pgMar"))
        if marge is None:
            marge = ET.SubElement(sect, q("w:pgMar"))
        restant = max(1440, largeur_page - largeur_texte)
        if profil.get("marge_annotation"):
            gauche = int(restant * 0.35)
            droite = restant - gauche  # colonne d'annotation à droite
        else:
            gauche = droite = restant // 2
        marge.set(q("w:left"), str(max(720, gauche)))
        marge.set(q("w:right"), str(max(720, droite)))
        for cote, valeur in (("w:top", "1134"), ("w:bottom", "1134")):
            if marge.get(q(cote)) is None:
                marge.set(q(cote), valeur)
        touches += 1
    return touches


def _fond(document, dossier, profil):
    """Le blanc pur fatigue ; le fond sombre n'a de sens que sur écran."""
    couleur, texte = FONDS.get(profil.get("fond", "creme"), FONDS["creme"])

    racine = document.racine
    fond = racine.find(q("w:background"))
    if fond is None:
        fond = ET.Element(q("w:background"))
        racine.insert(0, fond)  # w:background précède w:body
    fond.set(q("w:color"), couleur)

    chemin = dossier / "word" / "settings.xml"
    if chemin.is_file():
        arbre = ooxml.lire_fichier(chemin)
        reglages = arbre.getroot()
        # Sans ce réglage, Word ignore purement et simplement w:background.
        poser_enfant(reglages, "w:displayBackgroundShape", ooxml.ORDRE_SETTINGS)
        arbre.write(str(chemin), encoding="UTF-8", xml_declaration=True)
    return couleur


# -- respiration -----------------------------------------------------------


def _air_proportionnel(document, profil):
    """L'espacement suit la densité, bloc par bloc.

    Les passages difficiles respirent, les faciles restent compacts : la page
    ne double pas de longueur pour rien.
    """
    if not profil.get("air_proportionnel"):
        return 0
    interligne = float(profil["interligne"])
    touches = 0
    for paragraphe in document.paragraphes():
        texte = ooxml.texte_paragraphe(paragraphe)
        if not texte.strip():
            continue
        phrases = analyse.decouper_phrases(texte)
        longueurs = [len(analyse.MOT.findall(p)) for p in phrases] or [0]
        moyenne = sum(longueurs) / float(len(longueurs))
        indice = analyse.indice_densite(texte, moyenne)
        supplement = min(1.0, max(0.0, (indice - 18) / 22.0))
        ligne = int(round(interligne * 240 * (1 + 0.15 * supplement)))
        apres = int(round(160 + 200 * supplement))
        proprietes = ooxml.ppr(paragraphe, creer_si_absent=True)
        poser_enfant(proprietes, "w:spacing", ORDRE_PPR,
                     line=ligne, lineRule="auto", after=apres, before=int(apres * 0.4))
        touches += 1
    return touches


def _filets_de_section(document, profil):
    """Un trait coloré en marge par grande partie : savoir où l'on est sans relire le titre."""
    touches = 0
    rang = -1
    for paragraphe in document.paragraphes():
        proprietes = ooxml.ppr(paragraphe, creer_si_absent=False)
        if proprietes is None:
            continue
        style = proprietes.find(q("w:pStyle"))
        if style is None:
            continue
        valeur = (style.get(q("w:val")) or "").lower().replace(" ", "")
        if not re.match(r"(heading|titre)[12]$", valeur):
            continue
        if valeur.endswith("1"):
            rang += 1
        couleur = couleur_libre(profil, PALETTE_FILETS[max(0, rang) % len(PALETTE_FILETS)])
        proprietes = ooxml.ppr(paragraphe, creer_si_absent=True)
        bordures = proprietes.find(q("w:pBdr"))
        if bordures is None:
            bordures = ET.Element(q("w:pBdr"))
            index = ORDRE_PPR.index("w:pBdr")
            position = len(proprietes)
            for i, enfant in enumerate(proprietes):
                nom = ooxml._nom_court(enfant.tag)
                if nom in ORDRE_PPR and ORDRE_PPR.index(nom) > index:
                    position = i
                    break
            proprietes.insert(position, bordures)
        gauche = bordures.find(q("w:left"))
        if gauche is None:
            gauche = ET.SubElement(bordures, q("w:left"))
        gauche.set(q("w:val"), "single")
        gauche.set(q("w:sz"), "18")
        gauche.set(q("w:space"), "8")
        gauche.set(q("w:color"), couleur)
        touches += 1
    return touches


# -- teintes ---------------------------------------------------------------


def _teinter(document, caracteres, couleur, chiffres=False):
    """Teinte des caractères isolés — b/d/p/q, ou 3/8 et 1/7.

    Une nuance légère plutôt qu'une police différente : le mot garde sa forme
    d'ensemble, seul le caractère qui trompe attire l'œil. Aucun texte modifié :
    on découpe des runs, on n'écrit rien.
    """
    cible = set(caracteres)
    parents = document.parents()
    touches = 0
    for run in list(document.racine.iter(q("w:r"))):
        enfants = [e for e in run if e.tag != q("w:rPr")]
        if len(enfants) != 1 or enfants[0].tag != q("w:t"):
            continue
        ancetre = parents.get(id(run))
        protege = False
        while ancetre is not None:
            if ancetre.tag == q("w:p") and ancetre.find("./" + q("w:pPr") + "/" + q("w:pStyle")) is not None:
                protege = True  # Conservateur : style hérité potentiellement sémantique.
                break
            ancetre = parents.get(id(ancetre))
        if protege:
            continue
        proprietes = run.find(q("w:rPr"))
        # Ne pas écraser un code couleur, un surlignage ou un style sémantique.
        if proprietes is not None and any(proprietes.find(q(n)) is not None for n in ("w:color", "w:highlight", "w:shd", "w:rStyle")):
            continue
        texte = enfants[0].text or ""
        if not texte or not any(c in cible for c in texte):
            continue
        parent = parents.get(id(run))
        if parent is None:
            continue

        morceaux = []
        courant = ""
        marque_courante = None
        for caractere in texte:
            marque = caractere in cible
            if marque != marque_courante and courant:
                morceaux.append((courant, marque_courante))
                courant = ""
            marque_courante = marque
            courant += caractere
        if courant:
            morceaux.append((courant, marque_courante))

        position = list(parent).index(run)
        parent.remove(run)
        modele = run.find(q("w:rPr"))
        for decalage, (contenu, marque) in enumerate(morceaux):
            nouveau = ET.Element(q("w:r"))
            proprietes = copy.deepcopy(modele) if modele is not None else ET.Element(q("w:rPr"))
            if marque:
                # Une nuance, rien d'autre : la graisse et le style du mot
                # restent ceux du cours.
                poser_enfant(proprietes, "w:color", ORDRE_RPR, val=couleur)
            if len(proprietes):
                nouveau.append(proprietes)
            t = ET.SubElement(nouveau, q("w:t"))
            t.text = contenu
            t.set(XML_ESPACE, "preserve")
            parent.insert(position + decalage, nouveau)
        touches += 1
    return touches
