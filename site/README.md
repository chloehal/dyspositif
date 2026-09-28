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
npm ci
npm run build
npm test
python3 site/packager-skill.py --check
```

Les tests couvrent notamment les 1 024 combinaisons de besoins, les refus, le retrait des choix, la stabilité de l’ordre et les entrées invalides. Test manuel du parcours complet et de la copie exacte dans le navigateur, affichage ordinateur et mobile. Ce n’est pas une certification d’accessibilité ; des essais avec les personnes concernées restent nécessaires.

Le site expose, lorsque disponible, un outil WebMCP de lecture seule `read_assembled_prompt`, sur le même résultat que le champ visible. Il ne génère pas de texte et ne transmet pas le formulaire à un service distant.

## La skill au premier plan

La landing présente la skill avant le générateur : téléchargement de `dyspositif-skill.zip`, installation, exemple de demande avec une synthèse DOCX et essai sur extrait. Le générateur reste un avant-goût facultatif. Le parcours Claude est sourcé dans la page ; l’import et l’utilisation sur un compte Claude réel n’ont pas été testés dans cette intervention.

Le ZIP contient `dyspositif/SKILL.md`, les scripts Python, les références, le README et la licence. Il correspond aux sources de la refonte, sans documents personnels. Après modification de la skill, le régénérer avant de publier :

```sh
python3 site/packager-skill.py
python3 site/packager-skill.py --check
```

Le contrôle CI échoue si l’archive ne correspond plus aux sources. Les outils externes de rendu et de validation ne sont pas inclus dans ce ZIP : l’agent doit vérifier leur disponibilité et signaler les limites.

## Publication autonome sur Hostinger

Le `package.json` et le `package-lock.json` sont **à la racine du dépôt**. Le site utilise Node.js 22 ou plus, sans dépendance npm.

```sh
npm ci
npm run build
npm start
```

`build` copie les fichiers publics et le ZIP de la skill dans `dist/` à la racine. `start` sert uniquement ces fichiers et écoute le port fourni par `PORT`. Pour le développement : `npm run dev` sert directement `site/dist/`.

### Import du dépôt comme application Node.js

Sur une offre Hostinger prenant en charge les applications Node.js, utiliser :

| Réglage | Valeur |
|---|---|
| Racine du projet | Racine du dépôt (`.`) |
| Type de framework | Other / Autre |
| Version Node.js | 22 ou plus |
| Installation | `npm ci` |
| Construction | `npm run build` |
| Dossier de sortie | `dist` |
| Démarrage | `npm start` |
| Fichier d’entrée, si demandé | `site/server.mjs` |

Hostinger documente le type « Other » et les réglages à adapter dans son [guide Node.js](https://www.hostinger.com/support/how-to-deploy-a-nodejs-website-in-hostinger/). Ces commandes sont vérifiées localement ; aucun déploiement sur le compte Hostinger de la mainteneuse n’a été effectué.

### Hébergement statique par gestionnaire de fichiers

Il est aussi possible de déposer le contenu de `dist/` dans le dossier public du domaine, avec `index.html` à la racine. Les cinq fichiers incluent le téléchargement de la skill. Ne pas déposer les sources du serveur ni `package.json` dans le dossier public. Voir le [guide du gestionnaire de fichiers Hostinger](https://www.hostinger.com/support/4548688-basic-actions-in-the-file-manager-in-hostinger/).

### Archive et CI

```sh
python3 site/packager.py /tmp/dyspositif-hostinger.zip
```

Cette archive est destinée à l’hébergement **statique** ; pour l’import Node.js, connecter le dépôt complet contenant le `package.json` racine. L’artefact GitHub Actions `dyspositif-hostinger` fournit les fichiers statiques après vérification.

Aucun workflow ne déploie le site. La publication reste à la main de la mainteneuse. L’ancien aperçu privé est indépendant et n’est pas actualisé par cette PR.
