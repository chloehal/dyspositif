"""Lecture et écriture d'un word/document.xml sans le refabriquer.

Règle qui gouverne ce module : on ouvre l'archive, on modifie les nœuds
concernés, on referme. Aucune reconstruction, aucun reformatage, aucune
indentation — Word interprète les espaces entre balises comme du contenu.
"""

import re
import xml.etree.ElementTree as ET

# Les documents traités viennent de tiers. defusedxml coupe les bombes
# d'entités et les entités externes ; sans lui, on parse quand même, mais
# `dys.py analyser` le signale.
try:
    from defusedxml.ElementTree import fromstring as _fromstring_sur
    from defusedxml.ElementTree import parse as _parse_sur

    XML_DURCI = True
except ImportError:  # pragma: no cover - dépend de l'environnement
    _fromstring_sur = ET.fromstring
    _parse_sur = ET.parse
    XML_DURCI = False


def lire(donnees):
    """Parse du XML venant d'un document non fiable."""
    return _fromstring_sur(donnees)


def lire_fichier(chemin):
    return _parse_sur(str(chemin))

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

for _prefixe, _uri in NS.items():
    if _prefixe != "xml":
        ET.register_namespace(_prefixe, _uri)

W = NS["w"]
XML_ESPACE = "{%s}space" % NS["xml"]

DECLARATION = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'


def q(nom):
    """« w:p » -> nom qualifié ElementTree."""
    prefixe, _, local = nom.partition(":")
    return "{%s}%s" % (NS[prefixe], local)


def attr(element, nom, defaut=None):
    return element.get(q(nom), defaut)


def poser(element, nom, valeur):
    element.set(q(nom), str(valeur))


def creer(nom, **attributs):
    element = ET.Element(q(nom))
    for cle, valeur in attributs.items():
        element.set(q(cle.replace("__", ":")), str(valeur))
    return element


class Document(object):
    """Un word/document.xml ouvert, modifiable, refermable à l'identique."""

    def __init__(self, chemin):
        self.chemin = chemin
        with open(chemin, "rb") as f:
            self.source = f.read()
        self.racine = lire(self.source)
        self._balise_origine = _balise_racine(self.source)

    # -- écriture ---------------------------------------------------------

    def enregistrer(self, chemin=None):
        sortie = ET.tostring(self.racine, encoding="utf-8")
        sortie = _reinjecter_namespaces(sortie, self._balise_origine)
        if not sortie.startswith(b"<?xml"):
            sortie = DECLARATION + sortie
        with open(chemin or self.chemin, "wb") as f:
            f.write(sortie)

    # -- navigation -------------------------------------------------------

    @property
    def corps(self):
        return self.racine.find(q("w:body"))

    def paragraphes(self):
        return self.racine.iter(q("w:p"))

    def tableaux(self):
        return self.racine.iter(q("w:tbl"))

    def parents(self):
        """ElementTree n'a pas de pointeur parent : on le fabrique à la demande."""
        table = {}
        for parent in self.racine.iter():
            for enfant in parent:
                table[id(enfant)] = parent
        return table

    def prochain_id_revision(self):
        maxi = 0
        for element in self.racine.iter():
            valeur = element.get(q("w:id"))
            if valeur and valeur.lstrip("-").isdigit():
                maxi = max(maxi, int(valeur))
        return maxi + 1


# -- texte -----------------------------------------------------------------


def texte_run(run):
    morceaux = []
    for noeud in run.iter():
        if noeud.tag in (q("w:t"), q("w:delText")):
            morceaux.append(noeud.text or "")
        elif noeud.tag == q("w:tab"):
            morceaux.append("\t")
        elif noeud.tag in (q("w:br"), q("w:cr")):
            morceaux.append("\n")
    return "".join(morceaux)


def texte_paragraphe(paragraphe, avec_supprime=False):
    morceaux = []
    for noeud in paragraphe.iter():
        if noeud.tag == q("w:t"):
            morceaux.append(noeud.text or "")
        elif avec_supprime and noeud.tag == q("w:delText"):
            morceaux.append(noeud.text or "")
        elif noeud.tag == q("w:tab"):
            morceaux.append("\t")
    return "".join(morceaux)


def runs_visibles(paragraphe):
    """Runs porteurs de texte, hors texte déjà supprimé par une révision."""
    supprimes = set()
    for suppression in paragraphe.iter(q("w:del")):
        for run in suppression.iter(q("w:r")):
            supprimes.add(id(run))
    dedans = []
    for run in paragraphe.iter(q("w:r")):
        if id(run) in supprimes:
            continue
        if run.find(q("w:t")) is None:
            continue
        dedans.append(run)
    return dedans


def rpr(run, creer_si_absent=False):
    proprietes = run.find(q("w:rPr"))
    if proprietes is None and creer_si_absent:
        proprietes = ET.Element(q("w:rPr"))
        run.insert(0, proprietes)
    return proprietes


def ppr(paragraphe, creer_si_absent=False):
    proprietes = paragraphe.find(q("w:pPr"))
    if proprietes is None and creer_si_absent:
        proprietes = ET.Element(q("w:pPr"))
        paragraphe.insert(0, proprietes)
    return proprietes


def copier_rpr(run):
    proprietes = run.find(q("w:rPr"))
    if proprietes is None:
        return None
    import copy

    return copy.deepcopy(proprietes)


def run_texte(contenu, modele_rpr=None):
    """Un run neuf portant `contenu`, éventuellement au format d'un run existant."""
    import copy

    run = ET.Element(q("w:r"))
    if modele_rpr is not None:
        run.append(copy.deepcopy(modele_rpr))
    t = ET.SubElement(run, q("w:t"))
    t.text = contenu
    t.set(XML_ESPACE, "preserve")
    return run


# -- ordre imposé par le schéma -------------------------------------------

ORDRE_RPR = [
    "w:ins", "w:del", "w:rStyle", "w:rFonts", "w:b", "w:bCs", "w:i", "w:iCs",
    "w:caps", "w:smallCaps", "w:strike", "w:dstrike", "w:outline", "w:shadow",
    "w:emboss", "w:imprint", "w:noProof", "w:snapToGrid", "w:vanish",
    "w:webHidden", "w:color", "w:spacing", "w:w", "w:kern", "w:position",
    "w:sz", "w:szCs", "w:highlight", "w:u", "w:effect", "w:bdr", "w:shd",
    "w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang",
    "w:eastAsianLayout", "w:specVanish", "w:oMath",
]

ORDRE_PPR = [
    "w:pStyle", "w:keepNext", "w:keepLines", "w:pageBreakBefore",
    "w:framePr", "w:widowControl", "w:numPr", "w:suppressLineNumbers",
    "w:pBdr", "w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku",
    "w:wordWrap", "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE",
    "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid",
    "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents",
    "w:suppressOverlap", "w:jc", "w:textDirection", "w:textAlignment",
    "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr",
    "w:sectPr", "w:pPrChange",
]


# Début de la séquence imposée à w:settings — assez pour y insérer
# displayBackgroundShape au bon endroit sans casser le reste.
ORDRE_SETTINGS = [
    "w:writeProtection", "w:view", "w:zoom", "w:removePersonalInformation",
    "w:removeDateAndTime", "w:doNotDisplayPageBoundaries",
    "w:displayBackgroundShape", "w:printPostScriptOverText",
    "w:printFractionalCharacterWidth", "w:printFormsData",
    "w:embedTrueTypeFonts", "w:embedSystemFonts", "w:saveSubsetFonts",
    "w:saveFormsData", "w:mirrorMargins", "w:alignBordersAndEdges",
    "w:bordersDoNotSurroundHeader", "w:bordersDoNotSurroundFooter",
    "w:gutterAtTop", "w:hideSpellingErrors", "w:hideGrammaticalErrors",
    "w:activeWritingStyle", "w:proofState", "w:formsDesign",
    "w:attachedTemplate", "w:linkStyles", "w:stylePaneFormatFilter",
    "w:stylePaneSortMethod", "w:documentType", "w:mailMerge",
    "w:revisionView", "w:trackChanges", "w:doNotTrackMoves",
    "w:doNotTrackFormatting", "w:documentProtection", "w:autoFormatOverride",
    "w:styleLockTheme", "w:styleLockQFSet", "w:defaultTabStop",
    "w:autoHyphenation", "w:consecutiveHyphenLimit", "w:hyphenationZone",
    "w:doNotHyphenateCaps", "w:showEnvelope", "w:summaryLength",
    "w:clickAndTypeStyle", "w:defaultTableStyle", "w:evenAndOddHeaders",
    "w:bookFoldRevPrinting", "w:bookFoldPrinting", "w:bookFoldPrintingSheets",
    "w:drawingGridHorizontalSpacing", "w:drawingGridVerticalSpacing",
    "w:displayHorizontalDrawingGridEvery", "w:displayVerticalDrawingGridEvery",
    "w:doNotUseMarginsForDrawingGridOrigin", "w:drawingGridHorizontalOrigin",
    "w:drawingGridVerticalOrigin", "w:doNotShadeFormData",
    "w:noPunctuationKerning", "w:characterSpacingControl", "w:printTwoOnOne",
    "w:strictFirstAndLastChars", "w:noLineBreaksAfter", "w:noLineBreaksBefore",
    "w:savePreviewPicture", "w:doNotValidateAgainstSchema",
    "w:saveInvalidXml", "w:ignoreMixedContent", "w:alwaysShowPlaceholderText",
    "w:doNotDemarcateInvalidXml", "w:saveXmlDataOnly", "w:useXSLTWhenSaving",
    "w:saveThroughXslt", "w:showXMLTags", "w:alwaysMergeEmptyNamespace",
    "w:updateFields", "w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr",
    "w:compat", "w:docVars", "w:rsids",
]


def poser_enfant(parent, nom, ordre, **attributs):
    """Remplace ou insère un enfant en respectant l'ordre imposé par le schéma."""
    balise = q(nom)
    existant = parent.find(balise)
    if existant is not None:
        for cle, valeur in attributs.items():
            existant.set(q("w:" + cle), str(valeur))
        return existant

    element = ET.Element(balise)
    for cle, valeur in attributs.items():
        element.set(q("w:" + cle), str(valeur))

    try:
        rang = ordre.index(nom)
    except ValueError:
        parent.append(element)
        return element

    position = len(parent)
    for i, enfant in enumerate(parent):
        nom_enfant = _nom_court(enfant.tag)
        if nom_enfant in ordre and ordre.index(nom_enfant) > rang:
            position = i
            break
    parent.insert(position, element)
    return element


def retirer_enfants(parent, noms):
    if parent is None:
        return 0
    compte = 0
    for nom in noms:
        for enfant in parent.findall(q(nom)):
            parent.remove(enfant)
            compte += 1
    return compte


def _nom_court(balise):
    for prefixe, uri in NS.items():
        marque = "{%s}" % uri
        if balise.startswith(marque):
            return "%s:%s" % (prefixe, balise[len(marque):])
    return balise


# -- conservation des déclarations de namespaces ---------------------------


def _balise_racine(donnees):
    correspondance = re.search(rb"<([A-Za-z_][\w.:-]*)(\s[^>]*?)?>", donnees)
    if not correspondance:
        return None
    return correspondance.group(0)


def _declarations(balise):
    if not balise:
        return {}
    return dict(re.findall(rb'(xmlns(?::[\w.-]+)?)="([^"]*)"', balise))


def _reinjecter_namespaces(sortie, balise_origine):
    """ElementTree ne redéclare que les namespaces qu'il utilise.

    Un mc:Ignorable qui cite w14 sans que w14 soit déclaré casse le fichier :
    on repart donc de la balise racine d'origine, complétée des déclarations
    qu'ElementTree a ajoutées.
    """
    if not balise_origine:
        return sortie
    balise_sortie = _balise_racine(sortie)
    if not balise_sortie:
        return sortie

    origine = _declarations(balise_origine)
    ajoutees = _declarations(balise_sortie)
    manquantes = b"".join(
        b' %s="%s"' % (cle, valeur)
        for cle, valeur in sorted(ajoutees.items())
        if cle not in origine
    )
    remplacement = balise_origine[:-1] + manquantes + b">"
    return sortie.replace(balise_sortie, remplacement, 1)
