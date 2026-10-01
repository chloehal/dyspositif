# La landing dyspositif

Site statique, construit avec Vite, sans appel à une IA. Les choix du formulaire restent en mémoire dans la page : aucun envoi, stockage local, outil d’analyse ou dépôt de document n’est ajouté par le site. La copie vers une IA se fait ensuite à l’initiative de la personne.

## Aperçu

```sh
npm ci
npm run dev
```

Ouvrir `http://127.0.0.1:5173`. Servir par HTTP plutôt que d’ouvrir le fichier HTML directement, car les modules JavaScript nécessitent un serveur.

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

Le site est une application **statique Vite**. Node sert uniquement à construire les fichiers publics. Il n’y a aucun serveur Node à démarrer en production.

Après fusion de la correction dans `main`, configurer l’import GitHub dans Hostinger :

| Réglage | Valeur |
|---|---|
| Préréglage de framework | **Vite** |
| Branche | `main` |
| Répertoire root | `./` |
| Version Node | `22.x` (22.12 minimum) |
| Gestionnaire de paquets | `npm` |
| Commande de compilation | `npm run build` |
| Répertoire de sortie | `dist` |
| Fichier d’entrée | Aucun ; effacer l’ancienne valeur `site/server.mjs` si elle reste visible |

Enregistrer, puis redéployer. Si le formulaire ne propose pas Vite, réimporter le dépôt avec la version corrigée et sélectionner le déploiement statique Vite. Ne pas conserver le préréglage Other de l’ancienne configuration.

Hostinger décrit les applications Vite statiques dans son [guide de déploiement](https://www.hostinger.com/support/how-to-deploy-apps-built-with-codex-on-hostinger/). La validation locale et la CI ne prouvent pas le succès du déploiement sur le compte Hostinger.

### Vérifier la version construite en local

```sh
npm ci
npm run build
npm run preview
```

Ouvrir `http://127.0.0.1:4173`. `preview` sert uniquement aux essais locaux.

### Hébergement statique par gestionnaire de fichiers

Après `npm run build`, déposer **le contenu** de `dist/` dans le dossier public du domaine : `index.html`, le dossier `assets/` et `dyspositif-skill.zip`. Ne pas déposer les sources du dépôt dans le dossier public.

```sh
python3 site/packager.py /tmp/dyspositif-hostinger.zip
```

L’archive contient uniquement les fichiers publics construits. L’artefact GitHub Actions `dyspositif-hostinger` fournit également ces fichiers après vérification.

Aucun workflow ne déploie le site. La publication reste à la main de la mainteneuse.

## Parcours étudiant et accessibilité

La page présente un schéma en trois étapes puis un cas interactif en quatre temps : besoins combinés, essai, retour de l’étudiant, ajustement. Le document illustratif contient une définition, une méthode et un point de vigilance. Les repères par titres sont conservés après le retour ; les étapes trop fragmentées sont regroupées. Le scénario est préparé, sans appel à une IA et indépendant du générateur.

Contrôles réalisés : build et 10 tests Node, rendu à 320 et 1280 pixels, activation des quatre étapes au clavier et identité du texte de l’extrait à chaque étape. Les contrôles restent masqués sans JavaScript ; un texte alternatif explique le cas. Les instructions d’installation restent dans un volet natif.

Références : [reflow WCAG](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) et [taille des cibles](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html). Ces contrôles ne valent pas certification WCAG : essais avec lecteur d’écran et étudiants concernés encore nécessaires.
