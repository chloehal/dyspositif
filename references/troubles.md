# Besoins, choix et contextes

Le nom du fichier est conservé pour compatibilité. Il ne contient plus de table
« diagnostic → réglages ». Aucun diagnostic n'est requis, inféré ou transformé
automatiquement en difficulté. Une personne peut mentionner n'importe quel
trouble ; l'adaptation se décide sur ses besoins réels et son contexte.

## Dimensions combinables

| Clés de difficultés | Ce qu'il faut clarifier sur la synthèse |
|---|---|
| ligne, lettres | Décodage, suivi des lignes, repères déjà utiles |
| comprehension | Syntaxe, liens entre idées, implicite ou vocabulaire ; conserver les termes |
| attention | Entrée dans le texte et reprise après une pause |
| memoire | Informations à garder actives, regroupements ou repères stables |
| chiffres | Nombres, symboles, unités et comparaisons entre cellules |
| vision, surcharge | Grossissement, couleurs distinguables, densité des repères |
| reperage | Hiérarchie et recherche d'une information |
| navigation, ecriture | Moyen d'accès, clavier, lecteur d'écran, annotation |
| fatigue | Nature de l'effort et durée ; ne pas présumer une origine visuelle |
| autre ou clé inconnue | Accueillir le besoin, proposer un essai ou une description facultative |

Les mêmes besoins confirmés peuvent conduire aux mêmes essais malgré des
diagnostics différents. Deux personnes avec le même diagnostic peuvent préférer
des sorties opposées. Ne pas transformer une simple différence en gêne à corriger.

## Profil v2

Les réglages effectifs restent lisibles à la racine pour le moteur. Les champs
`decisions` et `propositions` distinguent choix et hypothèses. Une décision
contient `valeur`, `origine`, `etat` (`valide` ou `refuse`). Une propriété explicitement conservée porte `etat: conserve`. Un essai temporaire
porte `etat: essai`, jamais `valide`. Une proposition a
`etat: propose` et ne s'applique pas tant qu'elle n'a pas été retenue.
`essais` garde les paramètres validés et la date. `conflits` décrit les arbitrages
du profil d'application sans écraser les préférences enregistrées.

```json
{
  "q1_gene": ["ligne", "attention", "surcharge"],
  "q2_support": "ecran",
  "q_acces": "visuel",
  "q_sans_couleurs": "oui",
  "d1_relire": "souvent",
  "d3_segmenter_ou_reecrire": "segmentee",
  "priorites": ["suivre les lignes"],
  "reperes_a_preserver": ["termes exacts", "titres"],
  "besoin_libre": "Les lettres colorées me distraient."
}
```

`d1_relire` propose un interligne et une longueur de ligne ; il ne les impose
pas. Le choix montré de segmentation autorise celle-ci et interdit la
reformulation. Une gêne ultérieure ne révoque pas ce refus. `q1_troubles` est
facultatif et descriptif seulement. Les diagnostics ne sont pas affichés dans
le rappel du profil ni requis dans le bilan du fichier.

## Traduction des réponses

- Situation vécue (`d1`, `d2=oui`, `c2`, `a1`, `a3`, `r1`) : proposition à essayer.
- Choix entre versions (`q3`, `q4`, `c1`, `a2`, `q_tableaux`, `c3_teintes`,
  `q_compteur`) : décision correspondant au choix observé.
- Refus (`d2=non`, `a1=jamais`, `c1=colle`, etc.) : désactivation explicite.
- Réponse inconnue/non renseignée : conserver la décision existante.
- Arrêt : conserver les réponses et les choix, ne pas compléter par des
  « corrections » automatiques. Les propriétés non choisies sont conservées telles qu’elles sont dans le document.

Les questions ouvertes des nouvelles dimensions guident le travail de l'agent.
Le moteur n'infère pas de réglage depuis leur texte. L'agent prépare un essai
avec `--definir ... --temporaire`, puis enregistre les paramètres retenus.
Pour `besoin_libre`, enregistrer l'explication effective, pas « dire » ou « essai ».

## Combinaisons et ordre de priorité

1. Conserver l'information et reconnaître les limites du format/outillage.
2. Respecter les contraintes explicites (`texte_intact`, `sans_couleurs`).
3. Appliquer les choix et essais confirmés pour ce contexte.
4. Présenter les propositions non validées sans les appliquer.
5. Préserver les propriétés non choisies ; une nouvelle hypothèse reste un essai annoncé.

Les conflits non résolus par ces contraintes sont expliqués puis testés.
`priorites`, `reperes_a_preserver` et `besoin_libre` sont des informations à lire
par l'agent, pas des règles interprétées automatiquement. L'ordre des difficultés
ne change ni les branches ni le rythme du questionnaire.

## Réutilisation et migration

```bash
python scripts/dys.py profil --contexte ecran --reponses reponses.json
python scripts/dys.py profil --contexte papier --reponses papier.json
python scripts/dys.py profil --contexte ecran --definir taille_pt=16 --temporaire --json > essai.json
python scripts/dys.py profil --contexte ecran --valider interligne
python scripts/dys.py profil --contexte ecran --oublier
```

Sans contexte : `~/.dyspositif/profil.json`. Avec contexte : fichier voisin
`profil-ecran.json`, par exemple. `DYSPOSITIF_PROFIL` remplace le chemin de base.
Les profils sont locaux. Ne pas enregistrer leurs données dans le dépôt.
L'essai temporaire ne modifie aucun profil sauvegardé.
Un profil v1 est migré en propositions : confirmer les choix pertinents sur
extrait. Les mises à jour partielles conservent les autres réponses. Les champs
inutilisés `espacement_mots` des anciens profils n'ont pas d'effet.

Après un essai temporaire créé uniquement par `--definir`, sauvegarder les valeurs effectivement confirmées avec la même commande sans `--temporaire`. `--valider` est réservé aux propositions déjà enregistrées. Un contexte nommé sélectionne un fichier, il ne déduit aucun support.
