# Audit Dyspositif — adaptation personnalisée de synthèses existantes

Date : 28 septembre 2026. Version examinée : [chloehal/dyspositif, commit f8e396d](https://github.com/chloehal/dyspositif/tree/f8e396d11dc0c48d8899e343ab08eee831c65d95).

## Conclusion

La philosophie est déjà pertinente : conserver l'information, respecter les habitudes, travailler sans diagnostic obligatoire, montrer un aperçu et permettre de revenir en arrière. Mais le fonctionnement reste une traduction assez rigide de quelques réponses en réglages typographiques. Il ne garantit pas encore une adaptation personnelle lorsque les besoins se combinent ou se contredisent.

La priorité est de construire un système centré sur les besoins, les préférences confirmées et les obstacles rencontrés dans la synthèse. Ajouter des diagnostics à une liste ne suffira pas.

Promesse proposée :

> Dyspositif adapte une synthèse que tu possèdes déjà à ta façon de la lire et de l'utiliser. Il conserve son contenu et tes repères, propose des adaptations ciblées, puis les ajuste avec toi sur un extrait.

« Fonctionne pour tout type de trouble » doit devenir une ambition de couverture ouverte : accueillir tout besoin exprimé, y compris non prévu, sans promettre que chaque besoin est déjà résolu par les outils disponibles.

## Méthode et limites

Lecture de SKILL.md, des quatre références, des scripts Python, des tests, des évaluations et du workflow CI. Fichiers récupérés au commit indiqué dans une copie temporaire, sans modification du dépôt distant.

Exécution de la suite : 26 tests, dont 25 réussis et 1 ignoré. Le contrôle externe validate.py n'a pas été exécuté dans cette suite. Vérifications supplémentaires du calcul des profils, du questionnaire et de deux contrastes.

Cet audit établit des écarts de consignes et de code. Il ne constitue ni une validation clinique, ni une étude d'efficacité auprès de personnes concernées. Aucun parcours complet dans Word ou avec lecteur d'écran n'a été testé ici.

## 1. Priorité immédiate : verrouiller le périmètre

Le [README](https://github.com/chloehal/dyspositif/blob/f8e396d11dc0c48d8899e343ab08eee831c65d95/README.md) présente explicitement un outil pour adapter le cours du professeur. Le [déclencheur de SKILL.md](https://github.com/chloehal/dyspositif/blob/f8e396d11dc0c48d8899e343ab08eee831c65d95/SKILL.md#L1) couvre cours, articles et documents divers. Les évaluations portent principalement sur des cours.

À modifier ensemble :

- Entrée : une synthèse existante fournie par la personne.
- Sortie : cette synthèse adaptée, avec la même information.
- Un cours envoyé pour en obtenir une synthèse ne déclenche pas une production.
- Une demande d'adaptation d'un cours est expliquée comme hors du périmètre de cette première version.
- En cas d'ambiguïté sur la nature du fichier, une question courte suffit ; le nom ou la longueur ne permettent pas de trancher seuls.
- Supprimer du parcours initial les ajouts pédagogiques automatiques : exemples inventés, moyens mnémotechniques, explications complémentaires. Ce sont des fonctions distinctes à envisager ultérieurement.
- Une reformulation éventuelle reste ciblée, autorisée et fidèle ; elle ne sélectionne pas l'essentiel et ne raccourcit pas la synthèse en supprimant des informations.

Préserver aussi la possibilité d'ajouter une alternative textuelle fidèle à un schéma lorsque nécessaire pour l'accès : décrire une information visuelle existante ne revient pas à créer une synthèse. Ne jamais inventer les informations illisibles.

## 2. Priorité immédiate : rendre les préférences réellement souveraines

Plusieurs comportements contredisent la règle centrale du dépôt.

| Constat reproduit | Conséquence | Correction attendue |
|---|---|---|
| Difficulté « chiffres » + choix de chiffres non groupés donne quand même `grouper=true` et `paires=true` | Une difficulté supposée l'emporte sur un choix explicite | Un refus doit verrouiller la désactivation |
| Choix « segmentée » puis « je bloque sur les mots compliqués » donne `reformulation.actif=true` | Une gêne est interprétée comme une autorisation de réécrire | Séparer besoin et permission de transformation |
| Teinte des lettres activée, puis réponse « non » lors d'une mise à jour : elle reste active | Le profil mémorise les activations mais ne sait pas toujours les annuler | Traiter explicitement oui, non, inconnu et non renseigné |
| `attention,fatigue` et `fatigue,attention` donnent des tailles de groupe déclarées différentes | Le résultat dépend de l'ordre des difficultés | Résolution explicite des conflits, indépendante de l'ordre |
| Les groupes du questionnaire contiennent toujours jusqu'à trois questions | Le réglage « une question à la fois » n'est pas exécuté | Construire les groupes selon le réglage retenu |

Sources : [profil.py, réponses et règles automatiques](https://github.com/chloehal/dyspositif/blob/f8e396d11dc0c48d8899e343ab08eee831c65d95/scripts/dyslib/profil.py#L203), [dys.py, présentation du questionnaire](https://github.com/chloehal/dyspositif/blob/f8e396d11dc0c48d8899e343ab08eee831c65d95/scripts/dys.py#L97).

Ordre proposé : contraintes d'intégrité et possibilités réelles du format ; refus et préférences explicites ; adaptations validées sur extrait dans le même contexte ; propositions issues des besoins ; valeurs par défaut. Si deux exigences restent incompatibles, expliquer le compromis et faire choisir entre deux variantes.

## 3. Priorité haute : décrire des besoins indépendants des diagnostics

Le [mapping actuel](https://github.com/chloehal/dyspositif/blob/f8e396d11dc0c48d8899e343ab08eee831c65d95/scripts/dyslib/profil.py#L119) ramène notamment la dysorthographie aux lettres, la dysphasie à la perte de ligne et les troubles visuels au repérage et à la fatigue. Ces correspondances sont trop étroites pour décider d'une adaptation individuelle. La fatigue n'ouvre aucune branche.

Créer des dimensions combinables :

| Dimension | Ce qu'il faut découvrir |
|---|---|
| Décodage | Lettres, mots, vitesse et effort de lecture |
| Suivi du texte | Perte de ligne, retours à la ligne, maintien des repères |
| Compréhension | Syntaxe, implicite, vocabulaire, relations entre idées |
| Attention et reprise | Distraction, entrée dans un bloc, retour après interruption |
| Mémoire de travail | Quantité d'information à garder active, besoin de repères stables |
| Nombres et symboles | Quantités, signes, unités, formules, lecture des tableaux |
| Perception visuelle | Grossissement, contraste, couleurs distinguables, surcharge |
| Navigation et interaction | Clavier, lecteur d'écran, manipulation des pages, annotation |
| Fatigue et contexte | Durée de lecture, appareil, impression, besoins variables |

Le diagnostic est une information facultative pouvant suggérer une question, jamais une preuve qu'un réglage convient. Prévoir « autre difficulté », « aucune de ces propositions », « je ne sais pas » et la possibilité de décrire librement un besoin.

L'interdiction absolue du champ libre empêche le sur-mesure. Proposer des choix par défaut, accepter une explication courte ou dictée si la personne le souhaite, sans exiger qu'elle écrive.

Cette conception rejoint les recommandations de personnalisation du [W3C WAI](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o8p04-interface/), qui privilégient le contrôle de la présentation et la familiarité des repères.

## 4. Priorité haute : gérer les combinaisons et leurs conflits

Le système doit choisir les adaptations compatibles, et pas seulement réunir toutes les adaptations proposées par plusieurs branches.

Exemples de décisions à prévoir — hypothèses à valider avec la personne, pas recettes par diagnostic :

| Besoins exprimés ensemble | Conflit possible | Essai pertinent |
|---|---|---|
| Perte de ligne + surcharge visuelle | Les lettres colorées et nombreux repères ajoutent de la distraction | Espacement ajusté, peu de couleurs, titres stables |
| Difficulté avec les nombres + reprise après une pause | Un compteur numérique peut devenir une gêne supplémentaire | Repère verbal ou signet plutôt qu'un compteur imposé |
| Besoin de grossissement + fatigue | Le grossissement augmente les pages et la navigation | Taille confortable, structure navigable, aperçu dans le logiciel réel |
| Difficulté de compréhension + besoin de conserver les formulations | Une réécriture fait perdre des repères appris | Segmentation avec mots identiques, reformulation seulement si demandée |
| Code couleur personnel + difficulté à distinguer certaines teintes | Le code repose sur une distinction insuffisante | Garder le sens du code et ajouter un libellé ou un style distinct |
| Tableau difficile à parcourir + comparaison entre colonnes nécessaire | Le découpage impose des allers-retours | Tester tableau conservé et variante divisée avec en-têtes explicites |

Ajouter au profil : besoins prioritaires, adaptations refusées, repères à préserver, contexte, résultats des essais, origine de chaque réglage et état « proposé / validé / refusé ». Un réglage déduit ne doit pas être stocké comme une préférence certaine.

## 5. Priorité haute : partir de la synthèse réelle, puis calibrer

Le parcours actuel demande de montrer des passages du document avant l'étape où il est reçu. Il place aussi police et fond parmi les premières décisions pour tout le monde, même si le problème principal est ailleurs.

Parcours proposé :

1. Recevoir la synthèse et vérifier le périmètre, le format et l'extractibilité.
2. Reprendre un profil existant, puis vérifier seulement ce qui a changé : support, destinataire, besoin du jour.
3. Demander ce qui gêne le plus et ce qu'il faut absolument conserver.
4. Examiner les obstacles présents dans cette synthèse : tableaux, formules, blocs, images, structure.
5. Choisir un extrait représentatif. Ne pas prendre systématiquement la première page si elle ne contient que le titre.
6. Montrer au plus deux variantes sur les adaptations décisives. Proposer aussi « aucune » ou « garder l'original ».
7. Recueillir un retour concret : retrouver une information, suivre une ligne, comparer deux valeurs, reprendre après une pause.
8. Appliquer les choix confirmés, vérifier le fichier complet et enregistrer les préférences validées.

Éviter de refaire le questionnaire entier. Conserver plusieurs contextes légers, par exemple écran et papier, avec une possibilité d'ajustement temporaire sans écraser le profil habituel.

Le questionnaire doit lui aussi fonctionner avec les moyens d'accès de la personne. Des images d'aperçu et des pastilles de progression ne suffisent pas pour un usage non visuel.

## 6. Priorité haute : relier les promesses aux capacités réelles

**Codes couleur.** Le moteur utilise `couleurs_utilisateur` pour éviter certaines collisions de teintes, mais n'applique pas automatiquement une couleur aux définitions ou exemples identifiés. Les filets de section utilisent en outre leur palette propre sans recevoir le profil. Préserver les couleurs existantes n'est pas équivalent à appliquer un système sémantique personnalisé à toute la synthèse. Définir et tester ces deux fonctions séparément. [forme.py](https://github.com/chloehal/dyspositif/blob/f8e396d11dc0c48d8899e343ab08eee831c65d95/scripts/dyslib/forme.py#L31)

**Contrastes.** Les teintes par défaut orange `C2410C` et verte `0B6E4F`, sur le fond sombre `22262B`, donnent respectivement environ 2,94:1 et 2,43:1. Ce sont des valeurs calculées à partir des couleurs du code, sans mesure d'un rendu Word. Elles sont inférieures au repère de 4,5:1 pour du texte courant des [WCAG](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum). Contrôler toutes les associations effectivement utilisées, y compris le formatage direct préexistant. Ce contrôle isolé ne constitue pas une certification du DOCX.

**Paramètres sans effet assuré.** `espacement_mots` et `couleur_texte` sont présents dans le profil mais ne sont pas appliqués par le moteur de forme examiné comme des réglages personnalisés. La reformulation est guidée par les consignes de l'agent ; la commande `appliquer` ne comporte pas de passe de reformulation. Documenter ce qui est automatisé, ce qui demande l'intervention de l'agent et ce qui n'est pas disponible.

**Accessibilité structurelle.** Conserver une image ne la rend pas compréhensible au lecteur d'écran. Prévoir titres sémantiques, ordre de lecture, langue, textes alternatifs, listes et tableaux utilisables. Ces éléments font partie des pratiques d'accessibilité des documents présentées par [Microsoft](https://support.microsoft.com/en-us/accessibility/word/make-your-word-documents-accessible-to-people-with-disabilities). Le DOCX peut rester le format de départ, mais doit être testé dans les moyens de lecture visés.

**Audio.** Les références classent toute version audio comme une synthèse. Une lecture intégrale est pourtant une modalité d'accès au contenu. La génération audio peut rester hors de cette première version ; la compatibilité avec la lecture vocale doit être distinguée de la création d'un résumé.

**PDF.** Le parcours demande une conversion préalable, sans commande de conversion intégrée. Pour une entrée PDF, contrôler la fidélité après conversion avant toute adaptation. Un échec d'extraction doit être expliqué, pas transformé en promesse d'accessibilité.

**Aperçu.** `--pages 1` limite certains traitements textuels par estimation de blocs, pas l'ensemble des modifications ni le fichier à une page. La mise en forme et les tableaux restent traités au niveau du document. Clarifier cette portée et choisir explicitement l'extrait à soumettre à validation.

## 7. Priorité haute : renforcer la fidélité sans alourdir la lecture

Les modifications suivies et le fichier de contrôle sont de bonnes protections. Mais la présence des mêmes nombres, images et tableaux ne prouve pas la conservation de tout le sens.

Le vérificateur numérique cherche les valeurs de l'original dans le résultat ; il ne prouve pas leur rattachement aux bonnes unités, aux bonnes cellules ou aux bonnes propositions. Le comptage des images ne vérifie pas leur identité ni leur emplacement. [Vérification actuelle](https://github.com/chloehal/dyspositif/blob/f8e396d11dc0c48d8899e343ab08eee831c65d95/scripts/dys.py#L278)

Ajouter des contrôles des liens, notes, équations, négations, relations de tableaux et ancrages des images. Toute reformulation nécessite une comparaison du sens, avec limites explicites de l'automatisation.

Séparer la vue de lecture confortable de la vue de révision : ne pas imposer insertions, suppressions et commentaires visibles comme expérience quotidienne. Conserver l'original et un historique permettant de contrôler les changements.

Réviser aussi les formulations trop absolues des références : « le blanc pur fatigue », « neuf éléments saturent la mémoire », « une seule bonne longueur de ligne ». Présenter les réglages comme des hypothèses à essayer, et sourcer les affirmations d'efficacité avec leur population et leurs limites.

## 8. Tests nécessaires pour démontrer le sur-mesure

Les tests actuels protègent surtout la manipulation des fichiers. Certaines évaluations encouragent encore l'application automatique de réglages par diagnostic et l'absence totale de réponse libre.

À ajouter en priorité :

- Même diagnostic, préférences opposées : deux sorties différentes.
- Diagnostics différents, mêmes besoins confirmés : même proposition possible.
- Combinaison de difficultés fournie dans un autre ordre : même décision.
- Refus du regroupement numérique : jamais réactivé automatiquement.
- Refus de reformuler + difficulté de vocabulaire : pas de réécriture.
- Désactivation d'une option dans un profil existant : effet réel dans le fichier.
- Besoin non prévu ou absence de diagnostic : parcours utilisable.
- Fatigue + attention : une question à la fois si souhaité.
- Fond sombre + toutes les couleurs actives : contrastes contrôlés.
- Code couleur existant + nouvelles adaptations : aucun sens visuel écrasé.
- Lecteur d'écran + tableau ou schéma : information et navigation vérifiées.
- Changement écran/papier : profil précédent conservé.
- Cours brut ou demande de création de synthèse : respect du périmètre.
- Synthèse avec négations, unités et équations : aucune information perdue.
- Environnement sans outil de rendu ou de validation : résultat annoncé comme non vérifié, jamais comme validé.

Mesurer aussi l'utilisabilité avec des personnes concernées, sur leur propre synthèse et leur outil habituel : effort ressenti, repérage, reprise de lecture et erreurs. Un aperçu jugé joli ne suffit pas. Les recommandations du [W3C sur l'évaluation avec les utilisateurs](https://www.w3.org/WAI/test-evaluate/involving-users/) soutiennent cette vérification en contexte.

## Ordre de travail recommandé

1. Recadrer SKILL.md, README et évaluations autour des synthèses existantes.
2. Corriger les préférences écrasées, les désactivations, les conflits et les contrastes.
3. Introduire un profil par besoins avec origine et validation des choix.
4. Refaire le questionnaire autour du document, des obstacles et des repères à préserver.
5. Ajouter la sélection d'extraits représentatifs et la résolution des conflits.
6. Renforcer structure accessible, contrôles de fidélité et tests sur les outils réels.
7. Étendre la couverture à partir des besoins observés et des essais utilisateurs.

Critère de réussite : chaque changement doit être relié à un besoin confirmé ou à un choix explicite ; chaque refus doit être respecté ; une combinaison de besoins doit conduire à un arbitrage compréhensible ; aucune adaptation ne doit supprimer de contenu ni dégrader un autre moyen d'accès sans que cela soit détecté.

