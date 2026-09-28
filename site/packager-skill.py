"""Emballer la skill du dépôt ; --check vérifie la synchronisation du ZIP."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
root = Path(__file__).resolve().parent.parent
archive = root / 'site/public/dyspositif-skill.zip'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
files = [root / name for name in ('SKILL.md', 'README.md', 'LICENSE')]
files += sorted((root / 'scripts').rglob('*.py'))
files += sorted(p for p in (root / 'references').rglob('*') if p.is_file() and p.suffix in ('.md', '.json'))
contents = {'dyspositif/' + str(p.relative_to(root)): p.read_bytes() for p in files}
if args.check:
    with ZipFile(archive) as z:
        assert set(z.namelist()) == set(contents), 'Archive à régénérer'
        assert all(z.read(name) == data for name, data in contents.items()), 'Skill modifiée : régénérer le ZIP'
else:
    with ZipFile(archive, 'w', ZIP_DEFLATED) as z:
        for name, data in contents.items():
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
print(f'Skill : {len(contents)} fichiers vérifiés' if args.check else archive)
