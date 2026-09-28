#!/usr/bin/env python3
"""Fabrique les documents de test : un cours .docx et deux PDF.

Le .docx contient tout ce qui peut casser : une image, un tableau de six
colonnes, un tableau de trois, du formatage appliqué à la main, du texte
justifié, une phrase de quarante mots, une liste enfouie de six éléments et
des nombres longs.
"""

import struct
import sys
import zipfile
import zlib
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent / "documents"


def png(largeur=240, hauteur=140, couleur=(60, 90, 160)):
    def chunk(nom, donnees):
        morceau = nom + donnees
        return (
            struct.pack(">I", len(donnees))
            + morceau
            + struct.pack(">I", zlib.crc32(morceau) & 0xFFFFFFFF)
        )

    entete = struct.pack(">2I5B", largeur, hauteur, 8, 2, 0, 0, 0)
    lignes = b"".join(
        b"\x00" + bytes(couleur) * largeur for _ in range(hauteur)
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", entete)
        + chunk(b"IDAT", zlib.compress(lignes, 9))
        + chunk(b"IEND", b"")
    )


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/></Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""

DOCUMENT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/><Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/></Relationships>"""

SETTINGS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/></w:settings>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="259" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="36"/><w:szCs w:val="36"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:style></w:styles>"""

ENTETE_DOCUMENT = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
    'mc:Ignorable="w14 wpc">'
)

IMAGE = (
    '<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
    '<wp:extent cx="1905000" cy="1143000"/>'
    '<wp:docPr id="1" name="Schéma 1"/>'
    '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
    '<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="image1.png"/><pic:cNvPicPr/></pic:nvPicPr>'
    '<pic:blipFill><a:blip r:embed="rId5"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
    '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1905000" cy="1143000"/></a:xfrm>'
    '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
    "</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
)


def paragraphe(texte, style=None, justifie=False, police=None, taille=None):
    proprietes = ""
    if style or justifie:
        proprietes = "<w:pPr>"
        if style:
            proprietes += '<w:pStyle w:val="%s"/>' % style
        if justifie:
            proprietes += '<w:jc w:val="both"/>'
        proprietes += "</w:pPr>"
    run_pr = ""
    if police or taille:
        run_pr = "<w:rPr>"
        if police:
            run_pr += '<w:rFonts w:ascii="%s" w:hAnsi="%s"/>' % (police, police)
        if taille:
            run_pr += '<w:sz w:val="%s"/><w:szCs w:val="%s"/>' % (taille, taille)
        run_pr += "</w:rPr>"
    return '<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (
        proprietes,
        run_pr,
        texte,
    )


def tableau(entetes, lignes):
    colonnes = len(entetes)
    largeur = int(9000 / colonnes)
    xml = [
        '<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/><w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        "</w:tblBorders></w:tblPr><w:tblGrid>"
    ]
    for _ in range(colonnes):
        xml.append('<w:gridCol w:w="%s"/>' % largeur)
    xml.append("</w:tblGrid>")
    for ligne in [entetes] + lignes:
        xml.append("<w:tr>")
        for cellule in ligne:
            xml.append(
                '<w:tc><w:tcPr><w:tcW w:w="%s" w:type="dxa"/></w:tcPr>'
                '<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p></w:tc>'
                % (largeur, cellule)
            )
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


PHRASE_LONGUE = (
    "La séparation des pouvoirs, qui constitue le principe cardinal du droit "
    "constitutionnel moderne, suppose que les fonctions législative, exécutive "
    "et juridictionnelle soient confiées à des organes distincts, car la "
    "concentration de ces fonctions entre les mains d'un seul organe conduirait "
    "inévitablement à l'arbitraire, tandis que leur répartition garantit un "
    "contrôle mutuel dont dépend la protection des libertés fondamentales."
)

LISTE_ENFOUIE = (
    "Les six causes de la Révolution française sont la crise financière, "
    "la mauvaise récolte, la pression fiscale, la contestation des privilèges, "
    "la diffusion des idées des Lumières et le blocage des états généraux."
)

CHIFFRES = (
    "La population du royaume atteignait 1247893 habitants recensés en 1789, "
    "pour une dette publique de 126000000 livres et un déficit annuel de 56000 "
    "livres par district."
)


def document():
    corps = [
        paragraphe("Chapitre 1 — Les origines du droit constitutionnel", style="Heading1"),
        paragraphe(PHRASE_LONGUE, justifie=True),
        IMAGE,
        paragraphe("Section 1 — Les causes", style="Heading2"),
        paragraphe(LISTE_ENFOUIE),
        paragraphe(CHIFFRES, police="Times New Roman", taille="18"),
        tableau(
            ["Période", "Régime", "Durée", "Texte fondateur", "Suffrage", "Fin"],
            [
                ["1789-1791", "Monarchie", "2 ans", "Constitution de 1791", "Censitaire", "Chute"],
                ["1792-1795", "Convention", "3 ans", "Constitution de 1793", "Universel", "Thermidor"],
            ],
        ),
        paragraphe("Le tableau ci-dessus se lit ligne par ligne."),
        tableau(
            ["Notion", "Définition", "Exemple"],
            [["Souveraineté", "Pouvoir suprême", "Nation"]],
        ),
        paragraphe(
            "En pratique, le pouvoir de dissolution appartient au chef de l'État, "
            "mais il ne s'exerce qu'après consultation du Premier ministre et des "
            "présidents des assemblées, ce qui limite considérablement sa portée."
        ),
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1417" w:right="1417" w:bottom="1417" w:left="1417"/></w:sectPr>',
    ]
    return ENTETE_DOCUMENT + "<w:body>" + "".join(corps) + "</w:body></w:document>"


def ecrire_docx(chemin):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(chemin, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("word/document.xml", document())
        archive.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS)
        archive.writestr("word/styles.xml", STYLES)
        archive.writestr("word/settings.xml", SETTINGS)
        archive.writestr("word/media/image1.png", png())
    return chemin


# -- PDF -------------------------------------------------------------------


def _pdf(objets):
    sortie = b"%PDF-1.4\n"
    positions = []
    for numero, contenu in enumerate(objets, start=1):
        positions.append(len(sortie))
        sortie += b"%d 0 obj\n" % numero + contenu + b"\nendobj\n"
    debut_xref = len(sortie)
    sortie += b"xref\n0 %d\n" % (len(objets) + 1)
    sortie += b"0000000000 65535 f \n"
    for position in positions:
        sortie += b"%010d 00000 n \n" % position
    sortie += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objets) + 1,
        debut_xref,
    )
    return sortie


def pdf_texte(chemin):
    flux = b"BT /F1 12 Tf 72 700 Td (Le droit constitutionnel organise les pouvoirs publics.) Tj ET"
    objets = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(flux) + flux + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    chemin.write_bytes(_pdf(objets))
    return chemin


def pdf_scanne(chemin):
    image = zlib.compress(b"\xff" * (60 * 60 * 3))
    flux = b"q 595 0 0 842 0 0 cm /Im1 Do Q"
    objets = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /XObject << /Im1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(flux) + flux + b"\nendstream",
        b"<< /Type /XObject /Subtype /Image /Width 60 /Height 60 /ColorSpace /DeviceRGB "
        b"/BitsPerComponent 8 /Filter /FlateDecode /Length %d >>\nstream\n" % len(image)
        + image
        + b"\nendstream",
    ]
    chemin.write_bytes(_pdf(objets))
    return chemin


def tout(dossier=None):
    dossier = Path(dossier or DOSSIER)
    dossier.mkdir(parents=True, exist_ok=True)
    return {
        "docx": ecrire_docx(dossier / "synthese-droit-constitutionnel.docx"),
        "pdf_texte": pdf_texte(dossier / "cours-numerique.pdf"),
        "pdf_scanne": pdf_scanne(dossier / "cours-scanne.pdf"),
    }


if __name__ == "__main__":
    for nom, chemin in tout(sys.argv[1] if len(sys.argv) > 1 else None).items():
        print("%s : %s" % (nom, chemin))
