# La landing dyspositif

Site statique, sans dépendance ni appel à une IA. Les choix du formulaire restent en mémoire dans la page : aucun envoi, stockage local, outil d’analyse ou dépôt de document n’est ajouté par le site. La copie vers une IA se fait ensuite à l’initiative de la personne.

## Aperçu

```sh
python3 -m http.server 4173 --directory site/dist
```

Ouvrir `http://127.0.0.1:4173`. Servir par HTTP plutôt que d’ouvrir le fichier HTML directement, car les modules JavaScript nécessitent un serveur.

## Modifier les pièces

- `dist/puzzle.js` : catalogue de besoins, consignes prédéfinies, règles d’arbitrage et assemblage déterministe.
- `dist/app.js` : formulaire, étapes, aperçu et copie avec sélection manuelle de secours.
- `dist/index.html` et `dist/styles.css` : landing et présentation responsive.

Les consignes sur la conservation intégrale, les refus et l’essai sur extrait sont toujours présentes. Les besoins sont ordonnés de façon stable et dédupliqués. Les diagnostics ne sont pas collectés. Le texte libre est repris tel quel ; il n’est ni interprété par une IA ni injecté en HTML. Les conflits en texte libre ne peuvent pas être détectés exhaustivement : le prompt demande de les clarifier avec la personne.

## Vérification

```sh
node --test site/tests/puzzle.test.mjs
node --check site/dist/app.js
```

9 tests couvrent notamment les 1 024 combinaisons de besoins, les refus, le retrait des choix, la stabilité de l’ordre et les entrées invalides. Test manuel du parcours complet et de la copie exacte dans le navigateur, affichage ordinateur et mobile. Ce n’est pas une certification d’accessibilité ; des essais avec les personnes concernées restent nécessaires.

Le site expose, lorsque disponible, un outil WebMCP de lecture seule `read_assembled_prompt`, sur le même résultat que le champ visible. Il ne génère pas de texte et ne transmet pas le formulaire à un service distant.

## Publication autonome sur Hostinger

Les quatre fichiers de `site/dist/` sont prêts à servir tels quels :
`index.html`, `styles.css`, `app.js` et `puzzle.js`. Aucune compilation,
installation de dépendances, clé API ou base de données n’est nécessaire.
`package.json` sert uniquement aux tests locaux ; ne pas le téléverser.

1. Dans le gestionnaire de fichiers du domaine, ouvrir son dossier `public_html`.
2. Y déposer le **contenu** de `site/dist/`, avec `index.html` directement à la racine. Conserver une copie de tout site existant avant de remplacer ses fichiers.
3. Ouvrir le domaine en HTTPS, sélectionner plusieurs besoins puis vérifier la copie du prompt.

Cette procédure vise l’hébergement de fichiers HTML, et non l’éditeur Hostinger Website Builder. Voir la [documentation Hostinger sur le gestionnaire de fichiers](https://www.hostinger.com/support/4548688-basic-actions-in-the-file-manager-in-hostinger/).

### Archive prête à déposer

Depuis la racine du dépôt :

```sh
python3 site/packager.py /tmp/dyspositif-hostinger.zip
```

L’archive contient uniquement les quatre fichiers publics, sans dossier intermédiaire. Le workflow GitHub « landing » fournit aussi ces fichiers dans l’artefact `dyspositif-hostinger`, téléchargeable depuis une exécution réussie dans Actions.

Le dépôt ne déclenche aucun déploiement : la publication sur Hostinger reste manuelle. L’ancien aperçu privé est indépendant et n’est pas mis à jour par ce workflow.
