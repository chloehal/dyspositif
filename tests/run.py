#!/usr/bin/env python3
"""Suite complète ; un environnement temporaire par fichier de tests."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    tests = sorted(Path(__file__).parent.glob('test_*.py'))
    failed = []
    for test in tests:
        with tempfile.TemporaryDirectory(prefix='dyspositif-suite-') as d:
            env = dict(os.environ, DYSPOSITIF_PROFIL=str(Path(d) / 'profil.json'))
            print('\n' + test.name, flush=True)
            r = subprocess.run([sys.executable, str(test)], env=env)
            if r.returncode:
                failed.append(test.name)
    if failed:
        print('ÉCHEC : ' + ', '.join(failed), file=sys.stderr)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
