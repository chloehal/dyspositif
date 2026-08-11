# dyspositif

Skill Claude qui **adapte un document existant** pour une personne dys ou TDAH :
mise en forme, segmentation des phrases longues, listes enfouies sorties,
chiffres regroupés, tableaux larges découpés. Elle ne résume rien.

Elle modifie le fichier d'origine plutôt que de le reconstruire : les images,
les tableaux, les en-têtes et les notes ne peuvent donc pas être perdus. Toute
modification du texte est une modification suivie Word, rejetable une par une.

## Installer

```bash
ln -s "$PWD" ~/.claude/skills/dyspositif
```

La skill s'appuie sur la skill `docx` (fournie avec Claude Code) pour
`merge_runs.py`, `comment.py`, `validate.py` et `soffice.py`. Si elle n'est pas
trouvée automatiquement :

```bash
export DYSPOSITIF_SKILL_DOCX=/chemin/vers/skills/docx
export DYSPOSITIF_PYTHON=/chemin/vers/python   # validate.py a besoin de lxml + defusedxml
```

`dys.py apercu` a besoin de LibreOffice et de poppler :

```bash
brew install --cask libreoffice && brew install poppler
```

Sans eux, l'aperçu s'arrête en le disant — il ne montre jamais une page que
personne n'a regardée.

## Utiliser

```bash
python scripts/dys.py profil                                  # profil enregistré ?
python scripts/dys.py questions --difficultes ligne,chiffres  # les questions à poser
python scripts/dys.py profil --reponses reponses.json         # enregistrer le profil
python scripts/dys.py analyser cours.docx                     # volume et coût
python scripts/dys.py appliquer cours.docx apercu.docx --pages 1
python scripts/dys.py apercu apercu.docx                      # regarder avant de montrer
python scripts/dys.py appliquer cours.docx sortie.docx        # document complet
python scripts/dys.py verifier sortie.docx --original cours.docx
```

Le profil vit dans `~/.dyspositif/profil.json` (`DYSPOSITIF_PROFIL` pour en
changer). Chaque `appliquer` écrit un fichier de contrôle `.controle.md` à côté
du document : ce qui a changé, ce qui a été ajouté, et les nombres regroupés
avec leur valeur d'origine.

## Structure

```
SKILL.md                     le parcours en six étapes — c'est le document qui décide
references/questionnaire.json le texte exact des questions et leur branchement
references/troubles.md        ce que chaque réponse implique
references/reglages.md        chaque paramètre et sa justification
references/reformulation.md   règles de fidélité au contenu
scripts/dys.py                les commandes
scripts/dyslib/               ooxml, profil, analyse, suivi, forme, texte, tableaux, listes
tests/                        fixtures et tests
evals.json                    scénarios d'évaluation de la skill
```

## Tests

```bash
python3 tests/test_dys.py
```

Ils fabriquent un cours de test (image, tableau de six colonnes, formatage
appliqué à la main, phrase de quarante mots, liste enfouie de six éléments,
nombres longs) et vérifient, dans cet ordre :

1. le document produit s'ouvre (`validate.py`, XSD) ;
2. rejeter les modifications suivies restitue **exactement** le texte d'origine ;
3. les images et les tableaux d'origine sont toujours là ;
4. aucune valeur numérique du cours n'a bougé ;
5. le questionnaire ne pose que les branches déclarées.

Les points 1 et 4 sont sautés — explicitement, jamais silencieusement — si la
skill docx ou un Python avec `lxml` manquent.
