"""Ouvrir, refermer et vérifier un .docx — en s'appuyant sur la skill docx.

Rien n'est réimplémenté ici de ce que la skill docx fait déjà : merge_runs.py,
validate.py, comment.py et soffice.py sont appelés là où ils sont installés.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

RACINES_SKILL_DOCX = [
    "~/.claude/skills/docx",
    "~/.agents/skills/docx",
    "~/.config/claude/skills/docx",
]

MOTIFS_RECHERCHE = [
    "~/.claude/plugins",
    "~/Library/Application Support/Claude",
    "~/.claude/skills",
]


class ErreurPaquet(Exception):
    pass


def skill_docx(obligatoire=True):
    """Chemin du dossier de la skill docx, ou None."""
    depuis_env = os.environ.get("DYSPOSITIF_SKILL_DOCX")
    if depuis_env:
        chemin = Path(depuis_env).expanduser()
        if (chemin / "scripts" / "office" / "validate.py").is_file():
            return chemin
        raise ErreurPaquet(
            "DYSPOSITIF_SKILL_DOCX pointe sur %s, qui ne contient pas "
            "scripts/office/validate.py" % chemin
        )

    for candidat in RACINES_SKILL_DOCX:
        chemin = Path(candidat).expanduser()
        if (chemin / "scripts" / "office" / "validate.py").is_file():
            return chemin

    for racine in MOTIFS_RECHERCHE:
        base = Path(racine).expanduser()
        if not base.is_dir():
            continue
        for trouve in base.glob("**/skills/docx/scripts/office/validate.py"):
            return trouve.parents[2]

    if obligatoire:
        raise ErreurPaquet(
            "Skill docx introuvable. Elle fournit merge_runs.py, validate.py et "
            "comment.py, sur lesquels dyspositif s'appuie.\n"
            "Indiquer son emplacement : export DYSPOSITIF_SKILL_DOCX=/chemin/vers/skills/docx"
        )
    return None


def python_docx():
    """Interpréteur capable de faire tourner validate.py (il lui faut lxml)."""
    candidats = [os.environ.get("DYSPOSITIF_PYTHON"), sys.executable, "python3"]
    for candidat in candidats:
        if not candidat:
            continue
        essai = subprocess.run(
            [candidat, "-c", "import lxml, defusedxml"],
            capture_output=True,
        )
        if essai.returncode == 0:
            return candidat
    return None


# -- archive ---------------------------------------------------------------


def ouvrir(docx, destination):
    """Décompresse le .docx et supprime les liens symboliques.

    Un document reçu d'un tiers n'est pas de confiance : une entrée de type
    lien symbolique dans l'archive peut écrire hors du dossier de travail.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx) as archive:
        for entree in archive.infolist():
            cible = (destination / entree.filename).resolve()
            if not str(cible).startswith(str(destination.resolve())):
                raise ErreurPaquet("entrée d'archive hors du dossier : %s" % entree.filename)
            mode = entree.external_attr >> 16
            if mode and (mode & 0xF000) == 0xA000:  # lien symbolique
                continue
            archive.extract(entree, destination)
    for chemin in destination.rglob("*"):
        if chemin.is_symlink():
            chemin.unlink()
    return destination


def refermer(dossier, docx):
    """Rezippe en gardant [Content_Types].xml en tête, sans dossiers superflus."""
    dossier = Path(dossier)
    docx = Path(docx)
    if docx.exists():
        docx.unlink()
    fichiers = sorted(p for p in dossier.rglob("*") if p.is_file())
    tete = dossier / "[Content_Types].xml"
    if tete in fichiers:
        fichiers.remove(tete)
        fichiers.insert(0, tete)
    with zipfile.ZipFile(docx, "w", zipfile.ZIP_DEFLATED) as archive:
        for chemin in fichiers:
            archive.write(chemin, str(chemin.relative_to(dossier)))
    return docx


def fusionner_runs(dossier):
    """merge_runs.py : recoller les runs éclatés, sinon une recherche sur trois échoue."""
    skill = skill_docx()
    interprete = python_docx() or sys.executable
    script = skill / "scripts" / "merge_runs.py"
    resultat = subprocess.run(
        [interprete, str(script), str(dossier)], capture_output=True, text=True
    )
    if resultat.returncode != 0:
        raise ErreurPaquet("merge_runs.py a échoué : %s" % (resultat.stderr or resultat.stdout))
    return resultat.stdout.strip()


def valider(docx, original=None, auteur=None, reparer=False):
    """validate.py : XSD, et modifications suivies si --original et --author."""
    skill = skill_docx()
    interprete = python_docx()
    if interprete is None:
        return (
            None,
            "Validation impossible : aucun interpréteur Python avec lxml et defusedxml.\n"
            "Installer : python3 -m pip install lxml defusedxml\n"
            "ou : export DYSPOSITIF_PYTHON=/chemin/vers/python",
        )
    commande = [interprete, "scripts/office/validate.py", str(Path(docx).resolve())]
    if original:
        commande += ["--original", str(Path(original).resolve())]
    if auteur:
        commande += ["--author", auteur]
    if reparer:
        commande += ["--auto-repair"]
    resultat = subprocess.run(
        commande, cwd=str(skill), capture_output=True, text=True
    )
    sortie = (resultat.stdout or "") + (resultat.stderr or "")
    return resultat.returncode == 0, sortie.strip()


def commenter(dossier, texte, auteur="dyspositif"):
    """comment.py : les six fichiers croisés qu'exige un commentaire Word.

    Renvoie l'identifiant du commentaire ; les marqueurs restent à placer
    dans document.xml (commentRangeStart / commentRangeEnd / commentReference).
    """
    skill = skill_docx()
    interprete = python_docx() or sys.executable
    commande = [interprete, "comment.py", str(Path(dossier).resolve()), texte]
    if auteur:
        commande += ["--author", auteur, "--initials", "dys"]
    # comment.py importe `office.helpers` : il doit tourner depuis scripts/.
    resultat = subprocess.run(
        commande, cwd=str(skill / "scripts"), capture_output=True, text=True
    )
    if resultat.returncode != 0:
        raise ErreurPaquet("comment.py a échoué : %s" % (resultat.stderr or resultat.stdout))
    return resultat.stdout


# -- rendu -----------------------------------------------------------------


def soffice_disponible():
    if shutil.which("soffice"):
        return True
    return Path("/Applications/LibreOffice.app/Contents/MacOS/soffice").exists()


def rendre_images(docx, dossier_sortie, page_max=1):
    """docx -> pdf -> jpg, pour pouvoir regarder le résultat avant de le montrer."""
    skill = skill_docx()
    interprete = python_docx() or sys.executable
    dossier_sortie = Path(dossier_sortie)
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    if not soffice_disponible():
        raise ErreurPaquet(
            "LibreOffice (soffice) n'est pas installé : impossible de regarder le "
            "rendu avant de le montrer.\n"
            "macOS : brew install --cask libreoffice ; poppler pour pdftoppm : brew install poppler"
        )
    if not shutil.which("pdftoppm"):
        raise ErreurPaquet("pdftoppm manquant (paquet poppler) : brew install poppler")

    docx = Path(docx).resolve()
    subprocess.run(
        [
            interprete,
            str(skill / "scripts" / "office" / "soffice.py"),
            "--headless",
            "--convert-to",
            "pdf",
            str(docx),
        ],
        cwd=str(dossier_sortie),
        check=True,
        capture_output=True,
    )
    pdf = dossier_sortie / (docx.stem + ".pdf")
    if not pdf.exists():
        raise ErreurPaquet("la conversion PDF n'a rien produit")
    subprocess.run(
        [
            "pdftoppm", "-jpeg", "-r", "100",
            "-f", "1", "-l", str(page_max),
            str(pdf), str(dossier_sortie / "page"),
        ],
        check=True,
        capture_output=True,
    )
    return sorted(dossier_sortie.glob("page*.jpg"))


class DossierTemporaire(object):
    def __init__(self, prefixe="dyspositif-"):
        self.chemin = Path(tempfile.mkdtemp(prefix=prefixe))

    def __enter__(self):
        return self.chemin

    def __exit__(self, *_):
        shutil.rmtree(self.chemin, ignore_errors=True)
