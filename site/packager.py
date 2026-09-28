"""Préparer uniquement les fichiers publics, sans dépendance externe."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('archive', type=Path)
args = parser.parse_args()
source = Path(__file__).resolve().parent.parent / 'dist'
fichiers = ['index.html', 'dyspositif-skill.zip']
fichiers += [str(p.relative_to(source)) for p in sorted((source / 'assets').rglob('*')) if p.is_file()]
if len(fichiers) == 2:
    parser.error('Lancer npm run build avant de préparer l’archive.')
# Lire toutes les sources avant de créer l’archive pour éviter un résultat partiel.
contenus = {nom: (source / nom).read_bytes() for nom in fichiers}
if args.archive.resolve().is_relative_to(source):
    parser.error('Placer l’archive hors du dossier public dist.')
with ZipFile(args.archive, 'w', ZIP_DEFLATED) as archive:
    for nom, contenu in contenus.items():
        archive.writestr(nom, contenu)
print(args.archive.resolve())
