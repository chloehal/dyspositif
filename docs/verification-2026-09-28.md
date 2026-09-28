# Vérification de la refonte — 28 septembre 2026

La refonte adapte une synthèse existante à des besoins exprimés et à des choix essayés. Elle ne démontre pas une accessibilité universelle.

## Contrôles réalisés

- Suite `python3 tests/run.py` : 57 tests réussis sous Python 3.9 et sous Python 3.12 (15 documents, 26 intégration, 16 personnalisation), avec le validateur DOCX externe activé.
- Profils, refus, migrations, combinaisons dans un ordre différent, questionnaire, périmètre synthèse, fidélité des éléments protégés, extraction et structure couverts par des tests.
- Scénarios de skill comparés avant/après par un agent : diagnostic seul, refus, combinaison avec fatigue, accès non visuel et cours hors périmètre. Cela ne constitue pas une étude avec des utilisateurs.
- Relecture indépendante puis corrections : choix « original », couleurs héritées, intégrité des structures mathématiques, polices symboles héritées. Régressions couvertes par les tests.
- Validation externe et rendu LibreOffice de deux essais sur une fixture synthétique, clair et sombre. Les deux premières pages de chaque essai ont été inspectées.
- `git diff --check` sans erreur.

## Résultats du contrôle visuel

Les textes et teintes générées se lisent dans les deux rendus. L’agrandissement provoque cependant des coupures de mots dans le tableau étroit et une ligne partagée entre pages. Les bordures noires deviennent difficiles à distinguer sur le fond sombre. Ces essais ne sont donc pas des documents certifiés accessibles ou des exemples prêts à livrer. Le parcours impose de corriger les réglages et de refaire la comparaison dans ce cas.

L’audit signale aussi les alternatives d’images, la langue et les en-têtes de tableaux manquants dans cette fixture. Il ne corrige pas leur sens par supposition. La commande `structurer` applique les informations confirmées.

## Reproduire

```sh
python3 tests/run.py
```

Pour les contrôles externes, définir `DYSPOSITIF_SKILL_DOCX` vers une installation de la skill DOCX et `DYSPOSITIF_PYTHON` vers son interpréteur disposant de lxml et defusedxml. LibreOffice et pdftoppm sont nécessaires au rendu. La CI teste Python 3.9 et 3.12 ; elle distingue l’absence du validateur externe d’un échec technique.

## Ce qui reste à valider avec des personnes

Le protocole est dans `references/validation-utilisateurs.md`. Aucun essai avec une personne concernée ni aucune session réelle au lecteur d’écran n’a été réalisé dans cette intervention. Il faut vérifier l’utilité individuelle, les combinaisons de besoins, la navigation, la conservation du sens et le confort dans le contexte réel. Les contrôles automatiques restent partiels, notamment pour les thèmes, fonds locaux, tableaux complexes et conversions PDF. La génération audio n’est pas implémentée.
