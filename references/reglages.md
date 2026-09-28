# Réglages et capacités vérifiables

Les choix sont individuels. Les propositions de taille, police, espacement ou
fond ne sont ni un traitement ni une règle universelle. Comparer sur la synthèse
réelle. Ne pas attribuer de bénéfice clinique à une police ou à une couleur.

## Commandes

| Commande | Capacité et limite |
|---|---|
| profil | Profils v2 locaux, contexte nommé, mises à jour partielles, propositions et décisions |
| questions | Catalogue filtré par besoins, ordre invariant, rythme 1–3, accès non visuel |
| analyser | Densité heuristique, paragraphes/index, tableaux et images ; aucune inférence médicale |
| extrait | Inventaire puis copie de blocs entiers, tableaux compris, pour calibration |
| appliquer | Mise en forme, segmentation optionnelle, entiers groupés optionnels, tableaux selon choix |
| listes | Candidats à confirmer ; les nouvelles listes utilisent une numérotation Word sémantique |
| structurer | Langue par défaut, niveaux de plan de titres existants, alternatives de visuels, en-têtes confirmés |
| accessibilite | Audit partiel de structure et contrastes, avec limites explicites |
| apercu | Rendu via LibreOffice/pdftoppm ; ne teste pas le lecteur d'écran |
| verifier | Contrôle technique externe et interne ; ne certifie ni le sens ni l'accessibilité d'usage |

Les propriétés sans décision sont conservées telles quelles ; les paramètres non
choisis ne provoquent pas une remise en forme globale. Repartir de l’original
pour retirer une adaptation précédente.

## Réglages du moteur

`profil --definir parametre=valeur` représente un choix explicite. Pour un essai,
utiliser `--temporaire --json > essai.json`, puis `appliquer --profil essai.json`
(avec `--nature synthese`). Le bilan les étiquette `essai`. Après confirmation,
répéter les valeurs retenues sans `--temporaire`.

| Paramètre | Utilisation |
|---|---|
| police, taille_pt | Police disponible sur l'appareil cible, taille 8–72 pt (bornes techniques, pas recommandations) |
| alignement | conserver ou gauche, sans changement implicite |
| interligne | 1–3 ; tester confort, regroupement et volume |
| espacement_lettres_pt | 0–4 pt ; ne pas présumer qu'augmenter aide |
| longueur_ligne | 20–120 caractères estimés par les marges, pas une mesure typographique exacte |
| fond | blanc, creme, sombre ; préserver le choix même sur papier, signaler le compromis |
| couleur_texte | auto selon fond, ou six chiffres hexadécimaux ; audit du contraste |
| sans_couleurs | Désactive les nouveaux repères colorés, conserve le code existant |
| texte_intact | Empêche la reformulation ; segmentation et groupement préservent les mots/valeurs |
| lettres_miroir.actif, chiffres.paires | Uniquement après essai utile ; éviter les runs déjà colorés/surlignés/stylés |
| chiffres.grouper | Regroupement des entiers ; vérifier identifiants et notations particulières |
| listes.grouper_par, listes.compteur | Groupement et compteur optionnels ; rien n'est activé par diagnostic |
| tableaux.action | conserver (défaut), signaler, decouper ; cellules fusionnées non découpées automatiquement |
| tableaux.max_colonnes | Seuil technique, pas nombre de colonnes universellement accessible |
| filet_section, marge_annotation | Repères ou marge uniquement si utiles et retenus |
| segmentation.actif | Coupures visuelles suivies ; désactivées par défaut |
| air_proportionnel | Espacement variable heuristique, désactivé par défaut ; peut gêner des repères stables |

Les polices non installées peuvent être substituées : vérifier dans le logiciel
cible. Le moteur ne gère pas un espacement des mots indépendant, la création
automatique de chronologies, ni la classification automatique « définition /
exemple » pour appliquer des couleurs. Le code couleur est conservé et réservé ;
une nouvelle affectation sémantique demande de vérifier les passages concernés.

Les teintes ajoutées sont choisies avec un contraste d'au moins 4,5:1 sur le
fond de page et sans réutiliser une couleur personnelle. Les couleurs existantes
ne sont pas corrigées silencieusement. L'audit signale les associations suspectes ;
les fonds locaux, thèmes, images, contrastes réels et usages de la couleur sont
à vérifier dans le rendu. Le [repère WCAG sur le contraste](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum)
est utilisé pour guider ce contrôle, pas pour certifier un DOCX.

## Structure confirmée

`analyser --json` donne les indices de paragraphes. `accessibilite` indique les
identifiants des visuels concernés et indices de tableaux. Exemple de
`structure.json` (les indices doivent être remplacés par ceux vérifiés) :

```json
{
  "langue": "fr-BE",
  "titres": {"0": 1, "4": 2},
  "alternatives": {"1": "Description fidèle du visuel effectivement observé."},
  "entetes_tableaux": {"0": 1}
}
```

`titres` : index de paragraphe → niveau de plan 1–6, sans changer ses mots.
`alternatives` : identifiant `wp:docPr` unique du corps → description confirmée.
`entetes_tableaux` : index de tableau → nombre de premières lignes d'en-tête.
`langue` : langue par défaut ; ne remplace pas les langues explicites des passages.
Les alternatives dans en-têtes/notes ou objets VML, les tableaux complexes,
les listes imbriquées et l'ordre des objets flottants nécessitent une correction
avec les outils DOCX ou le logiciel cible. Ne pas inventer l'information manquante.

Les bonnes pratiques de [Microsoft pour Word](https://support.microsoft.com/en-us/accessibility/word/make-your-word-documents-accessible-to-people-with-disabilities)
comprennent structure, alternatives et vérification avec les moyens de lecture.
Un niveau de plan ou une description présente ne prouve pas sa pertinence.

## Fidélité et contrôles

Le validateur extérieur vérifie le schéma et les révisions quand la skill DOCX,
lxml et defusedxml sont disponibles. `verifier` complète par restitution du texte
original, identité des médias et parties protégées, conservation des relations,
liens, champs, références et contenu mathématique. Le contrôle numérique est un
filet supplémentaire, pas une preuve de conservation des unités ou relations.

Les sorties distinguent : contrôles passés, échec, contrôle non exécuté. Le bilan
rapporte les conflits, choix, propositions laissées en attente et alertes.
L'audit d'accessibilité retourne toujours 4 : il reste une validation humaine.

## Dépendances

Python 3.9+. `defusedxml` recommandé pour les documents tiers. La skill DOCX
fournit fusion des runs, commentaires, validation XSD et rendu :

```bash
export DYSPOSITIF_SKILL_DOCX=/chemin/vers/skills/docx
export DYSPOSITIF_PYTHON=/chemin/vers/python-avec-lxml-et-defusedxml
```

LibreOffice et pdftoppm sont nécessaires au rendu. Ne pas présenter un rendu
non exécuté comme vérifié. Ne pas exposer ces détails à la personne sauf si la
limite empêche son résultat et qu'une action de sa part peut la résoudre.
