"""Analyser le document sans le faire entrer en contexte.

Sert deux choses : annoncer le volume et le coût avant de lancer quoi que ce
soit, et repérer les endroits qui méritent une intervention.
"""

import re
import zipfile
import zlib

from . import ooxml
from .ooxml import q

FIN_DE_PHRASE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÀÂÉÈÊËÎÏÔÙÛÜÇ«\"])")
MOT = re.compile(r"[^\W\d_]+", re.UNICODE)
NOMBRE = re.compile(r"\d[\d   .,]*\d|\d")

CONNECTEURS = [
    "mais", "donc", "or", "car", "cependant", "toutefois", "néanmoins",
    "tandis que", "alors que", "parce que", "puisque", "afin de", "afin que",
    "si bien que", "de sorte que", "c'est-à-dire", "en revanche", "ainsi",
    "par ailleurs", "dès lors", "en effet", "notamment", "lorsque", "bien que",
]

MARQUEURS_ENUMERATION = [
    r"d'une part.+d'autre part",
    r"\bpremièrement\b.+\bdeuxièmement\b",
    r"\bd'abord\b.+\bensuite\b",
    r"\btout d'abord\b.+\benfin\b",
    r"\bsoit\b.+\bsoit\b.+\bsoit\b",
]

MARQUEURS_CHRONOLOGIE = [
    r"\b1[0-9]{3}\b", r"\b20[0-9]{2}\b", r"\bavant\b", r"\baprès\b",
    r"\bensuite\b", r"\bpuis\b", r"\benfin\b", r"\bà partir de\b",
]


def analyser_docx(chemin):
    with zipfile.ZipFile(chemin) as archive:
        noms = archive.namelist()
        donnees = archive.read("word/document.xml")
        medias = [n for n in noms if n.startswith("word/media/")]
    racine = ooxml.ET.fromstring(donnees)

    paragraphes = []
    for index, paragraphe in enumerate(racine.iter(q("w:p"))):
        texte = ooxml.texte_paragraphe(paragraphe)
        style = paragraphe.find("./%s/%s" % (q("w:pPr"), q("w:pStyle")))
        niveau_titre = None
        if style is not None:
            valeur = (style.get(q("w:val")) or "").lower()
            correspondance = re.search(r"(heading|titre)(\d)", valeur.replace(" ", ""))
            if correspondance:
                niveau_titre = int(correspondance.group(2))
        liste = paragraphe.find("./%s/%s" % (q("w:pPr"), q("w:numPr"))) is not None
        paragraphes.append(
            {
                "index": index,
                "texte": texte,
                "mots": len(MOT.findall(texte)),
                "caracteres": len(texte),
                "titre": niveau_titre,
                "liste": liste,
            }
        )

    corps = [p for p in paragraphes if p["texte"].strip()]
    caracteres = sum(p["caracteres"] for p in corps)
    mots = sum(p["mots"] for p in corps)

    tableaux = []
    for index, tableau in enumerate(racine.iter(q("w:tbl"))):
        grille = tableau.find(q("w:tblGrid"))
        colonnes = len(grille.findall(q("w:gridCol"))) if grille is not None else 0
        lignes = len(tableau.findall(q("w:tr")))
        fusions = any(
            cellule.find("./%s/%s" % (q("w:tcPr"), q("w:gridSpan"))) is not None
            or cellule.find("./%s/%s" % (q("w:tcPr"), q("w:vMerge"))) is not None
            for cellule in tableau.iter(q("w:tc"))
        )
        tableaux.append(
            {"index": index, "colonnes": colonnes, "lignes": lignes, "fusions": fusions}
        )

    images = len(list(racine.iter(q("w:drawing")))) + len(
        list(racine.iter("{urn:schemas-microsoft-com:vml}imagedata"))
    )

    denses = []
    phrases_longues = 0
    for p in corps:
        if p["titre"] or p["mots"] < 12:
            continue
        phrases = decouper_phrases(p["texte"])
        longueurs = [len(MOT.findall(phrase)) for phrase in phrases] or [0]
        maxi = max(longueurs)
        moyenne = sum(longueurs) / float(len(longueurs))
        phrases_longues += sum(1 for longueur in longueurs if longueur > 28)
        indice = indice_densite(p["texte"], moyenne)
        if maxi > 28 or (p["mots"] > 110 and moyenne > 20):
            denses.append(
                {
                    "index": p["index"],
                    "mots": p["mots"],
                    "phrase_la_plus_longue": maxi,
                    "indice": round(indice, 1),
                    "extrait": p["texte"][:120],
                }
            )

    candidates = []
    for p in corps:
        trouvee = detecter_liste_enfouie(p["texte"])
        if trouvee:
            trouvee["index"] = p["index"]
            candidates.append(trouvee)

    chronologies = [
        p["index"]
        for p in corps
        if sum(1 for motif in MARQUEURS_CHRONOLOGIE if re.search(motif, p["texte"], re.I)) >= 3
    ]

    nombres_longs = 0
    for p in corps:
        for brut in NOMBRE.findall(p["texte"]):
            if len(re.sub(r"\D", "", brut)) >= 5:
                nombres_longs += 1

    direct = {"polices": set(), "tailles": set(), "runs": 0}
    for run in racine.iter(q("w:r")):
        proprietes = run.find(q("w:rPr"))
        if proprietes is None:
            continue
        police = proprietes.find(q("w:rFonts"))
        taille = proprietes.find(q("w:sz"))
        if police is not None or taille is not None:
            direct["runs"] += 1
        if police is not None:
            direct["polices"].add(police.get(q("w:ascii")) or "?")
        if taille is not None:
            valeur = taille.get(q("w:val"))
            if valeur and valeur.isdigit():
                direct["tailles"].add(int(valeur) / 2.0)

    justifies = sum(
        1
        for jc in racine.iter(q("w:jc"))
        if jc.get(q("w:val")) == "both"
    )

    pages = max(1, int(round((caracteres / 1800.0) + images * 0.3)))
    rapport = {
        "fichier": str(chemin),
        "pages_estimees": pages,
        "blocs": len(corps),
        "mots": mots,
        "caracteres": caracteres,
        "titres": sum(1 for p in corps if p["titre"]),
        "images": images,
        "medias": len(medias),
        "tableaux": tableaux,
        "tableaux_larges": [t for t in tableaux if t["colonnes"] > 3],
        "paragraphes_denses": denses,
        "phrases_longues": phrases_longues,
        "listes_candidates": candidates,
        "chronologies": chronologies,
        "nombres_longs": nombres_longs,
        "formatage_direct": {
            "runs": direct["runs"],
            "polices": sorted(direct["polices"]),
            "tailles": sorted(direct["tailles"]),
        },
        "paragraphes_justifies": justifies,
    }
    rapport["part_dense"] = (
        round(100.0 * len(denses) / len(corps)) if corps else 0
    )
    rapport["resume"] = resume(rapport)
    return rapport


def blocs_pour_pages(chemin, pages, caracteres_par_page=1800):
    """Combien de blocs représentent les N premières pages.

    Sert à limiter les étapes coûteuses : inutile de payer pour quarante pages
    que l'utilisateur va peut-être refuser.
    """
    with zipfile.ZipFile(chemin) as archive:
        racine = ooxml.ET.fromstring(archive.read("word/document.xml"))
    budget = pages * caracteres_par_page
    total = 0
    blocs = 0
    for paragraphe in racine.iter(q("w:p")):
        texte = ooxml.texte_paragraphe(paragraphe)
        if not texte.strip():
            continue
        blocs += 1
        total += len(texte)
        if total >= budget:
            break
    return max(1, blocs)


def resume(rapport):
    lignes = [
        "%s pages, %s blocs, %s images, %s tableaux."
        % (
            rapport["pages_estimees"],
            rapport["blocs"],
            rapport["images"],
            len(rapport["tableaux"]),
        ),
        "%s passages denses repérés, soit %s %%."
        % (len(rapport["paragraphes_denses"]), rapport["part_dense"]),
    ]
    if rapport["tableaux_larges"]:
        lignes.append(
            "%s tableau(x) de plus de trois colonnes."
            % len(rapport["tableaux_larges"])
        )
    if rapport["listes_candidates"]:
        lignes.append(
            "%s énumération(s) enfouie(s) dans une phrase."
            % len(rapport["listes_candidates"])
        )
    if rapport["formatage_direct"]["runs"]:
        lignes.append(
            "%s passages ont un formatage appliqué à la main, qui l'emporte sur les styles."
            % rapport["formatage_direct"]["runs"]
        )
    return " ".join(lignes)


def decouper_phrases(texte):
    phrases = [p.strip() for p in FIN_DE_PHRASE.split(texte) if p.strip()]
    return phrases or ([texte] if texte.strip() else [])


def indice_densite(texte, moyenne_mots):
    """Proxy de lisibilité : longueur de phrase et proportion de mots longs."""
    mots = MOT.findall(texte)
    if not mots:
        return 0.0
    longs = sum(1 for mot in mots if len(mot) > 9)
    return moyenne_mots + 15.0 * longs / len(mots)


def detecter_liste_enfouie(texte):
    """Une énumération noyée dans une phrase — révélable, pas inventée.

    En cas de doute, on renvoie None : une fausse liste désoriente plus qu'un
    paragraphe dense.
    """
    for motif in MARQUEURS_ENUMERATION:
        if re.search(motif, texte, re.I):
            return {
                "motif": "marqueurs",
                "texte": texte[:200],
                "elements": None,
                "certitude": "à confirmer",
            }

    for phrase in decouper_phrases(texte):
        elements = _enumeration_de_phrase(phrase)
        if elements and len(elements) >= 3:
            annonce = nombre_annonce(phrase)
            return {
                "motif": "énumération coordonnée",
                "texte": phrase,
                "elements": elements,
                "nombre": len(elements),
                "nombre_annonce": annonce,
                "certitude": (
                    "annoncée par le texte"
                    if annonce == len(elements)
                    else "probable"
                ),
            }
    return None


INTRODUCTEURS = re.compile(
    r"\b(?:sont|est|comprend|comporte|distingue|regroupe|réunit|à savoir|"
    r"suivantes?|suivants?)\s*:?\s+",
    re.I,
)


def _enumeration_de_phrase(phrase):
    """« a, b, c et d » -> quatre éléments. Sinon rien."""
    corps = phrase
    decalage = 0
    deux_points = corps.find(" : ")
    if deux_points != -1:
        decalage = deux_points + 3
    else:
        premiere_virgule = corps.find(",")
        for introducteur in INTRODUCTEURS.finditer(corps):
            if premiere_virgule == -1 or introducteur.end() <= premiere_virgule:
                decalage = introducteur.end()
    if not decalage:
        # Aucune annonce d'énumération : deux virgules et un « et » ne suffisent
        # pas. Une fausse liste désoriente plus qu'un paragraphe dense.
        return None
    corps = corps[decalage:]

    coordinations = list(re.finditer(r",?\s+(?:et|ou|ainsi que)\s+", corps))
    if not coordinations:
        return None
    coordination = coordinations[-1]
    avant = corps[: coordination.start()]
    apres = corps[coordination.end():]
    if avant.count(",") < 1:
        return None

    morceaux = [m.strip() for m in avant.split(",") if m.strip()]
    dernier = re.split(r"[.;]", apres)[0].strip()
    if dernier:
        morceaux.append(dernier)
    if len(morceaux) < 3:
        return None
    longueurs = [len(MOT.findall(m)) for m in morceaux]
    if any(n > 10 or n == 0 for n in longueurs):
        return None  # ce sont des propositions, pas une énumération
    if sum(longueurs) / float(len(longueurs)) > 8:
        return None
    return morceaux


NOMBRES_ECRITS = {
    "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7,
    "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12,
}


def nombre_annonce(texte):
    """« les six causes » : le texte dit combien il y en a — de quoi vérifier."""
    for mot, valeur in NOMBRES_ECRITS.items():
        if re.search(r"\b%s\b" % mot, texte, re.I):
            return valeur
    return None


# -- PDF -------------------------------------------------------------------


def analyser_pdf(chemin):
    """Un PDF scanné n'a pas de texte extractible : le détecter, le dire.

    Produire un document vide à partir d'images serait pire que de s'arrêter.
    """
    with open(chemin, "rb") as f:
        donnees = f.read()

    pages = donnees.count(b"/Type /Page") + donnees.count(b"/Type/Page")
    pages = max(1, pages - donnees.count(b"/Type /Pages") - donnees.count(b"/Type/Pages"))
    images = donnees.count(b"/Subtype /Image") + donnees.count(b"/Subtype/Image")

    caracteres = 0
    operateurs = 0
    for flux in re.findall(rb"stream\r?\n(.*?)endstream", donnees, re.S):
        contenu = flux
        try:
            contenu = zlib.decompress(flux)
        except zlib.error:
            pass
        if b"Tj" not in contenu and b"TJ" not in contenu and b"'" not in contenu:
            continue
        operateurs += contenu.count(b"Tj") + contenu.count(b"TJ")
        for chaine in re.findall(rb"\((?:\\.|[^()\\])*\)", contenu):
            caracteres += max(0, len(chaine) - 2)

    a_du_texte = operateurs > 0 and caracteres > 40 * pages
    return {
        "fichier": str(chemin),
        "pages": pages,
        "images": images,
        "operateurs_texte": operateurs,
        "caracteres_estimes": caracteres,
        "texte_extractible": a_du_texte,
        "scanne_probable": not a_du_texte and images >= max(1, pages - 1),
        "resume": (
            "Texte extractible : %s caractères sur %s pages."
            % (caracteres, pages)
            if a_du_texte
            else "Aucun texte extractible : ce PDF contient des images de pages, "
            "pas du texte. Rien à adapter en l'état."
        ),
    }
