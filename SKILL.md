---
name: dyspositif
description: >
  Utiliser pour rendre accessible ou adapter une synthèse existante fournie
  par une personne : difficultés de lecture, compréhension, attention,
  mémoire, nombres, vision, navigation ou fatigue, avec ou sans diagnostic,
  seules ou combinées. Convient aussi pour conserver un système personnel
  de repères. Ne pas utiliser pour adapter un cours brut, créer une synthèse,
  résumer, sélectionner l'essentiel ou inventer du contenu pédagogique.
---

# Dyspositif

**Adapter la synthèse de la personne à sa façon de lire et de l’utiliser, en conservant son information et ses repères.**

Une synthèse accessible pour une personne peut ne pas convenir à une autre.
Les besoins exprimés, le contexte et l’essai sur sa synthèse déterminent les
adaptations. Un diagnostic est facultatif ; il ne déclenche aucun réglage.
Accueillir les besoins non prévus, sans promettre de résoudre tous les troubles.

## Contrat de sortie

- La synthèse adaptée conserve informations, termes, valeurs, unités, relations,
  exceptions, citations, images, tableaux, liens et notes.
- Chaque adaptation répond à un choix explicite ou à un essai validé. Les
  propositions non validées restent des propositions.
- Un refus explicite prime sur une déduction. Les besoins combinés donnent
  lieu à un arbitrage, jamais à une accumulation automatique de réglages.
- L’original est conservé sous son nom ; travailler sur des copies distinctes.
- Livrer une vue de lecture confortable, la possibilité de contrôler les
  changements et un bilan court des limites réellement rencontrées.

## 1 — Recevoir la synthèse et situer l’usage

Recevoir le fichier avant toute comparaison visuelle. Si sa nature est ambiguë,
demander seulement si c’est déjà une synthèse ; ni son nom ni sa longueur ne
suffisent pour décider. Un cours envoyé pour être résumé ou adapté reste hors
périmètre de cette version. Expliquer simplement que l’outil attend une synthèse
existante ; ne pas proposer en substitution l’adaptation intégrale du cours.

DOCX : édition directe. PDF : analyser l’extractibilité, puis convertir avec un
outil disponible et vérifier texte, formules, tableaux et images contre le PDF
avant l’adaptation. Il n’existe pas de conversion PDF/OCR intégrée ici. Si elle
n’est pas fiable ou disponible, demander le fichier éditable ou expliquer la
limite. Ne jamais appeler « accessible » un fichier extrait incomplet.

```bash
python scripts/dys.py analyser synthese.docx --json
python scripts/dys.py accessibilite synthese.docx
python scripts/dys.py profil --contexte ecran --json
```

`accessibilite` retourne 4 : l’audit automatisé reste à vérifier en usage.
L’absence de profil est normale. Un profil existant évite de tout redemander :
vérifier seulement la personne destinataire, le support et ce qui a changé.
Une migration v1 fournit des propositions à reconfirmer, pas un profil validé.

## 2 — Comprendre le besoin et ce qu’il faut préserver

Lire `references/questionnaire.json` et `references/troubles.md`. Réutiliser les
informations déjà données ; le catalogue n’est pas une liste à poser en entier.
Commencer par le principal obstacle dans cette synthèse et les repères à garder.
Noter le support et le moyen d’accès : lecture visuelle, vocale, lecteur d’écran,
clavier ou combinaison. Demander seulement ce qui change la prochaine décision.

```bash
python scripts/dys.py questions
python scripts/dys.py questions --difficultes attention,fatigue --rythme 1
python scripts/dys.py questions --difficultes navigation,autre --acces lecteur_ecran
```

Choix courts par défaut, explication libre ou dictée facultative. Toujours
permettre « autre », « je ne sais pas », « aucune variante » et l’arrêt.
Ne pas imposer une grille, une image ou des pastilles à quelqu’un qui ne peut
pas les utiliser. Pour l’accès non visuel, comparer le document navigable et
son ordre de lecture ; une capture d’écran ne constitue pas un essai suffisant.

Séparer dans le profil : besoins déclarés, priorités, repères à préserver,
réglages proposés, choix validés/refusés et origine des décisions. Les réponses
sur une gêne ne sont pas une permission de reformuler ou de colorer.

## 3 — Proposer un essai ciblé et arbitrer

Lire `references/reglages.md`. Proposer seulement les changements utiles au
besoin prioritaire et à la synthèse réelle. Partir des habitudes de la personne.
Les propriétés non choisies restent celles du document. Les valeurs du profil
ne sont pas des recommandations médicales ; une valeur technique proposée pour
un essai doit rester annoncée comme provisoire.

Arbitrer avant l’essai :

| Situation exprimée | Décision à tester |
|---|---|
| Perte de ligne et surcharge | Essayer espacement et lignes sans multiplication des couleurs |
| Reprise difficile et gêne avec les chiffres | Repère de titre ou signet ; compteur seulement s’il aide |
| Compréhension difficile et mots exacts à conserver | Segmenter sans réécrire ; garder les termes |
| Tableau difficile et comparaisons nécessaires | Comparer tableau entier et parties ; vérifier les relations |
| Couleurs personnelles et faible distinction des teintes | Préserver leur sens ; proposer des labels ou styles redondants |
| Grossissement et fatigue | Vérifier navigation et volume dans le logiciel réellement utilisé |

Ces exemples répondent à des besoins, pas à des diagnostics. Si deux choix
restent incompatibles, expliquer le compromis et montrer au plus deux options.
`pour_application` désactive les nouveaux repères colorés si `sans_couleurs` est
actif et la reformulation si `texte_intact` est actif ; le bilan consigne cela.

```bash
python scripts/dys.py profil --reponses reponses.json --contexte ecran
python scripts/dys.py profil --contexte ecran --definir sans_couleurs=true texte_intact=true
# Essai sans écraser le profil habituel ; rediriger le JSON vers un fichier.
python scripts/dys.py profil --contexte ecran --definir interligne=1.8 --temporaire --json > essai.json
```

Une couleur personnelle peu lisible doit être signalée et ajustée avec la
personne ; ne pas la remplacer silencieusement. « Sans nouvelles couleurs »
préserve les couleurs préexistantes. Un rendu monochrome nécessite d’abord de
remplacer leurs fonctions par des repères équivalents, pas de tout effacer.

## 4 — Calibrer sur un passage représentatif

Choisir un extrait contenant la gêne réelle : paragraphe dense, tableau, formule,
visuel ou plusieurs de ces éléments. Inclure les titres, unités, légendes et
exceptions nécessaires pour le comprendre. La première page n’est pas un choix
par défaut. Les indices des blocs d’extrait et des paragraphes de structure sont
deux inventaires distincts ; ne pas les confondre.

```bash
python scripts/dys.py extrait synthese.docx --inventaire
python scripts/dys.py extrait synthese.docx extrait.docx --debut 3 --fin 5
python scripts/dys.py appliquer extrait.docx essai.docx --nature synthese --profil essai.json
python scripts/dys.py apercu essai.docx --pages 2
```

Indices zéro, fin incluse. `extrait` conserve les blocs et leurs ressources dans
une copie de calibration ; les renvois, sections et la pagination doivent être
vérifiés. Ce fichier n’est jamais livré comme la synthèse complète.
L’ancien `appliquer --pages` ne découpe pas le fichier et ne limite pas toutes
les opérations : employer `extrait` pour la calibration.

Regarder le rendu produit. Tester avec le moyen d’accès de la personne.
Vérifier notamment les mots coupés dans les cellules après agrandissement,
les lignes de tableau séparées entre pages et le contraste des bordures sur
le fond choisi. Si un essai dégrade ces repères, ajuster les réglages concernés
et comparer à nouveau avant de les retenir.
Demander un retour concret : suivre la ligne, retrouver une information,
comparer les bonnes cellules, reprendre après une pause. Accepter « aucune ».
Les outils manquants et les essais non réalisés sont annoncés comme tels.

Enregistrer seulement les réglages confirmés :

```bash
python scripts/dys.py profil --contexte ecran --valider interligne longueur_ligne
```

Cette commande valide des propositions déjà présentes ; ne pas l’appeler sans
retour correspondant. Un silence ne valide pas. Une consigne explicite de
l’utilisateur autorisant ses propres réglages suffit, sans re-questionnaire.
Pour un essai créé seulement avec `--definir ... --temporaire`, ses valeurs sont
marquées `essai` et ne sont pas sauvegardées comme propositions. Après son retour
positif, enregistrer exactement les valeurs retenues avec :

```bash
python scripts/dys.py profil --contexte ecran --definir interligne=1.8
```

Pour imprimer temporairement avec les préférences écran :
`profil --contexte ecran --definir support=papier --temporaire --json`.
Un nom de contexte sélectionne un fichier ; il ne change pas le support tout seul.

## 5 — Appliquer et rendre la structure accessible

Lire `references/reformulation.md` avant toute intervention textuelle. Appliquer
le profil validé à une copie de la synthèse complète. Conserver l’original.

```bash
python scripts/dys.py appliquer synthese.docx adaptee.docx --nature synthese --contexte ecran
```

Moteur : forme, segmentation autorisée, regroupement des entiers autorisé,
tableaux conservés/signalés/découpés selon choix. Listes : candidats explicitement
confirmés avec `--listes-spec` ; ne pas supposer que toute énumération doit changer.
La reformulation n’est pas exécutée par cette commande. Elle relève de l’agent,
uniquement si autorisée, avec suivi des modifications et comparaison du sens.

Corriger la structure à partir d’une spécification vérifiée contre le document :
langue, niveaux des titres existants, descriptions fidèles de visuels et lignes
d’en-tête confirmées. Aucun titre ni contenu pédagogique n’est inventé.

```bash
python scripts/dys.py structurer adaptee.docx structuree.docx --spec structure.json
```

Format, indices et limites dans `references/reglages.md`. Utiliser la skill DOCX
pour les éléments complexes non couverts : listes imbriquées ou complexes,
relations de tableaux complexes, ordre de lecture et passages multilingues.
Contrôler le document complet, pas uniquement l’extrait validé.

Ne pas créer de mnémotechniques, nouveaux exemples, résumés ou définitions.
Une description fidèle d’un visuel déjà présent est une alternative d’accès,
pas une synthèse inventée. Une lecture vocale intégrale n’est pas un résumé ;
la compatibilité avec elle fait partie de l’accès, mais la génération audio
n’est pas fournie par ce moteur.

## 6 — Vérifier et livrer

```bash
python scripts/dys.py verifier structuree.docx --original synthese.docx
python scripts/dys.py accessibilite structuree.docx
```

`verifier` distingue échec (3), contrôle technique incomplet (4) et contrôles
techniques réussis (0). Il vérifie notamment restitution du texte original,
identité des médias/notes/en-têtes, relations, objets protégés et nombres.
Ce n’est pas une preuve automatique de conservation du sens après reformulation,
ni de compréhension des images ou tableaux. Comparer les transformations et
résoudre les alertes avant de déclarer la vérification complète.

Laisser une vue sans marques pour lire confortablement dans Word et une copie
avec historique pour contrôler. Si une copie avec changements acceptés est
produite via la skill DOCX, la vérifier séparément : conserver la copie révisée.
Ne pas supprimer silencieusement les révisions préexistantes de la personne.

Livraison : fichier adapté, original préservé, bilan court des choix et des
limites, comment ajuster ou revenir en arrière. Si des vérifications restent
impossibles, dire lesquelles ; ne jamais annoncer « accessible à tous ».

## Références

- `references/troubles.md` : besoins, décisions et profils de contexte.
- `references/questionnaire.json` : catalogue de questions adaptatives.
- `references/reglages.md` : capacités réelles, commandes, structure et contrastes.
- `references/reformulation.md` : fidélité, suivi et protection du contenu.
- `references/validation-utilisateurs.md` : protocole d’essais et critères de réussite.
