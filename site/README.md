# La landing dyspositif

Site statique, sans dépendance ni appel à une IA. Les choix du formulaire restent en mémoire dans la page : aucun envoi, stockage local, outil d’analyse ou dépôt de document n’est ajouté par le site. La copie vers une IA se fait ensuite à l’initiative de la personne.

## Aperçu

```sh
python3 -m http.server 4173 --directory site/dist
```

Ouvrir `http://127.0.0.1:4173`. Servir par HTTP plutôt que d’ouvrir le fichier HTML directement, car les modules JavaScript nécessitent un serveur.

## Modifier les pièces

- `dist/puzzle.mjs` : catalogue de besoins, consignes prédéfinies, règles d’arbitrage et assemblage déterministe.
- `dist/app.mjs` : formulaire, étapes, aperçu et copie avec sélection manuelle de secours.
- `dist/index.html` et `dist/styles.css` : landing et présentation responsive.

Les consignes sur la conservation intégrale, les refus et l’essai sur extrait sont toujours présentes. Les besoins sont ordonnés de façon stable et dédupliqués. Les diagnostics ne sont pas collectés. Le texte libre est repris tel quel ; il n’est ni interprété par une IA ni injecté en HTML. Les conflits en texte libre ne peuvent pas être détectés exhaustivement : le prompt demande de les clarifier avec la personne.

## Vérification

```sh
node --test site/tests/puzzle.test.mjs
node --check site/dist/app.mjs
```

9 tests couvrent notamment les 1 024 combinaisons de besoins, les refus, le retrait des choix, la stabilité de l’ordre et les entrées invalides. Test manuel du parcours complet et de la copie exacte dans le navigateur, affichage ordinateur et mobile. Ce n’est pas une certification d’accessibilité ; des essais avec les personnes concernées restent nécessaires.

Le site expose, lorsque disponible, un outil WebMCP de lecture seule `read_assembled_prompt`, sur le même résultat que le champ visible. Il ne génère pas de texte et ne transmet pas le formulaire à un service distant.

## Publication

Les sources restent dans le dépôt GitHub. Une copie isolée du dossier `site` sert au dépôt d’hébergement Sites, pour ne pas publier les autres fichiers du projet. `.openai/hosting.json` contient l’identité du site et la déclaration du répertoire statique `dist`, sans secret. L’aperçu hébergé est privé par défaut ; ouvrir au public constitue une étape distincte.
