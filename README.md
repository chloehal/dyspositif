# dyspositif

**Ta synthèse, adaptée à ta façon de la lire.**

Dyspositif est une skill qui rend une **synthèse existante** plus utilisable pour
la personne qui la lit. Elle conserve son contenu et ses repères, propose des
adaptations ciblées, puis les ajuste sur un extrait réel.

Elle ne transforme pas un cours en synthèse, ne résume pas davantage et n'invente
pas de contenu pédagogique. Le diagnostic est facultatif : les besoins, choix
et outils de lecture comptent, y compris lorsqu'ils se combinent.

## Le parcours

1. Recevoir la synthèse et identifier son usage.
2. Reprendre les besoins déjà connus et ce qu'il faut conserver.
3. Proposer les adaptations utiles et résoudre les conflits.
4. Comparer sur un extrait représentatif, avec le moyen de lecture habituel.
5. Appliquer les choix confirmés et corriger la structure nécessaire.
6. Vérifier le fichier complet et expliquer les limites restantes.

Une personne qui perd ses lignes et supporte mal les repères colorés peut tester
un espacement différent sans coloration. Une autre peut conserver ses couleurs
personnelles. Deux diagnostics identiques n'impliquent pas deux sorties identiques.

## Ce qui change dans cette refonte

- Profils par besoins, sans réglages déclenchés par diagnostic.
- Refus explicites, provenance des choix, propositions à valider sur extrait.
- Profils nommés et essais temporaires sans écraser les habitudes.
- Questionnaire ouvert aux besoins inconnus, rythme ajustable, accès non visuel.
- Extraits choisis par blocs, tableaux compris.
- Contraste des nouvelles teintes et préservation des codes couleur existants.
- Corrections structurelles confirmées et audit d'accessibilité partiel.
- Contrôle d'identité des médias, relations, objets et restitution du texte.

## Utiliser la skill

Charger [SKILL.md](SKILL.md) dans un agent capable de lire les fichiers et
exécuter Python. Fournir sa synthèse DOCX et expliquer le besoin, par exemple :

> Voici ma synthèse. Je perds ma ligne et les couleurs me distraient. Garde
> les mots exacts et mes titres. Je la lis sur écran.

L'agent suit les consignes et s'appuie sur les outils ci-dessous. La CLI seule
ne remplace pas l'échange ni la vérification avec la personne.

## Outils

Python 3.9+ ; `defusedxml` recommandé. La skill DOCX et un Python avec `lxml`
et `defusedxml` permettent validation et commentaires. Le rendu nécessite
LibreOffice et pdftoppm. Aucun OCR ni convertisseur PDF→DOCX intégré.

```bash
python3 scripts/dys.py analyser synthese.docx --json
python3 scripts/dys.py questions --difficultes ligne,attention --rythme 1
python3 scripts/dys.py profil --reponses reponses.json --contexte ecran
python3 scripts/dys.py profil --contexte ecran --definir interligne=1.8 --temporaire --json > essai.json
python3 scripts/dys.py extrait synthese.docx --inventaire
python3 scripts/dys.py extrait synthese.docx extrait.docx --debut 3 --fin 5
python3 scripts/dys.py appliquer extrait.docx essai.docx --nature synthese --profil essai.json
python3 scripts/dys.py apercu essai.docx --pages 2
# Après un essai effectivement validé :
python3 scripts/dys.py profil --contexte ecran --valider interligne
python3 scripts/dys.py appliquer synthese.docx adaptee.docx --nature synthese --contexte ecran
python3 scripts/dys.py verifier adaptee.docx --original synthese.docx
python3 scripts/dys.py accessibilite adaptee.docx
```

L'exemple suppose que la réponse sur la perte de ligne a créé une proposition
`interligne`. Les indices de l'extrait doivent être choisis dans l'inventaire.
`--nature synthese` atteste la nature confirmée par l'agent et la personne ;
le moteur ne prétend pas la classifier automatiquement.

La source ne peut pas être la sortie. Les profils sont locaux, supprimables
avec `profil --contexte ecran --oublier`. L'ancien profil v1 devient une série
de propositions à reconfirmer. Les modalités et champs sont décrits dans
[les profils](references/troubles.md) et [les réglages](references/reglages.md).

## Ce qui est vérifié — et ce qui reste à vérifier

Les tests couvrent les préférences contradictoires, les mises à jour, les
combinaisons de besoins, le questionnaire et des transformations de fichiers.
Les contrôles du moteur ne certifient pas l'accessibilité universelle ni la
fidélité sémantique d'une reformulation. Les contrastes sur fonds locaux,
l'ordre de lecture et l'utilité doivent être vérifiés dans le logiciel cible.

Le code de sortie de `verifier` est 0 pour les contrôles techniques réussis,
3 pour un échec et 4 pour un contrôle technique incomplet. `accessibilite`
retourne 4 même sans alerte : une vérification humaine reste nécessaire.

Les listes confirmées sont créées avec une numérotation Word sémantique.
La correction de listes imbriquées complexes, de visuels VML ou d'objets flottants
reste guidée par l'agent et les outils DOCX. La reformulation autorisée est une
intervention suivie de l'agent, pas une passe de la commande `appliquer`.
Les descriptions d'images sont fidèles à un visuel observé, jamais devinées.

Le [protocole d'essais utilisateurs](references/validation-utilisateurs.md)
explique comment vérifier le sur-mesure en situation. Ces essais réels ne sont
pas remplacés par les tests automatiques.

## Développer

```bash
python3 tests/run.py
```

Les tests isolent leurs profils et leurs fichiers. La validation externe peut
être ignorée lorsque ses dépendances sont absentes ; cela apparaît dans le résultat.
Pour l'activer : `DYSPOSITIF_SKILL_DOCX` et `DYSPOSITIF_PYTHON` (voir les réglages).
Les [scénarios d'évaluation](evals.json) complètent les tests de code.

Contributions : [CONTRIBUTING.md](CONTRIBUTING.md). Sécurité : [SECURITY.md](SECURITY.md).
Licence : [MIT](LICENSE).
