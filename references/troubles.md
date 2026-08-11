# Ce que chaque réponse implique

À charger **au moment de traduire les réponses en paramètres** (étape 2), et
seulement pour les difficultés déclarées.

Deux règles tiennent tout ce fichier :

> **On n'exige jamais de diagnostic.** Beaucoup d'adultes n'ont jamais été
> testés. Demander une étiquette exclut précisément ceux qui en auraient le
> plus besoin.
>
> **On ne renvoie jamais l'étiquette à quelqu'un qui ne l'a pas revendiquée.**
> Les correspondances ci-dessous servent à choisir des réglages, pas à annoncer
> à une utilisatrice qu'elle est dyslexique. Si elle a dit « je relis trois fois
> la même ligne », on répond sur la ligne, pas sur le mot.

---

## De la difficulté ressentie à la branche

| Réponse cochée (q1) | Clé | Branche ouverte | Ce qu'on en déduit |
|---|---|---|---|
| Je perds ma ligne, je relis la même phrase | `ligne` | déchiffrage | Empan visuel court, saut de ligne. Ligne courte, interligne large, repères en marge |
| Je confonds des lettres qui se ressemblent | `lettres` | déchiffrage | Confusion de lettres miroir. Espacement inter-lettres, teinte sur b/d/p/q |
| Je décroche, je pense à autre chose | `attention` | attention | Coût d'entrée élevé, reprise difficile. Blocs courts, groupement par trois, compteurs de position |
| Les chiffres et les tableaux me perdent | `chiffres` | chiffres | Traitement du nombre coûteux. Groupes de trois, distinction 3/8 et 1/7, tableaux découpés |
| Je ne sais pas où regarder sur la page | `reperage` | repérage | Balayage visuel désorganisé. Un seul fil de lecture, filet de section, hiérarchie nette |
| Je lis bien, c'est juste fatigant | `fatigue` | (aucune) | Fatigue visuelle. Corps plus grand, fond non blanc, plus d'air |
| Je connais mon diagnostic | — | selon le trouble | Ouvre la liste des troubles |

Une seule branche par difficulté, jamais toutes : quelqu'un qui n'a coché que
« les chiffres me perdent » ne doit pas se voir poser de questions sur les
lettres miroir. C'est ce qui garde le questionnaire à huit questions.

## Du diagnostic déclaré aux difficultés

Pour ceux qui préfèrent donner leur diagnostic directement. Les difficultés
listées ne sont **pas** une définition du trouble : ce sont les réglages
qu'on active par défaut, à confirmer par les questions de la branche.

| Trouble déclaré | Difficultés supposées | Branches ouvertes |
|---|---|---|
| Dyslexie | `ligne`, `lettres` | déchiffrage |
| Dysorthographie | `lettres` | déchiffrage — et surtout : **aucun champ libre**, jamais |
| Dyscalculie | `chiffres` | chiffres |
| Dyspraxie | `reperage` | repérage |
| TDAH | `attention` | attention |
| Dysphasie | `ligne` | déchiffrage — segmentation avant reformulation |
| Trouble visuel | `reperage`, `fatigue` | repérage |

Le cumul est la norme, pas l'exception : dyslexie et TDAH vont souvent
ensemble. Deux troubles déclarés donnent deux branches, soit onze questions au
maximum — jamais quatorze si les branches se recoupent.

## Des réponses aux paramètres

Correspondances appliquées par `scripts/dyslib/profil.py` (`depuis_reponses`).
Les valeurs sont des points de départ : toute préférence exprimée les écrase.

| Question | Réponse | Paramètre |
|---|---|---|
| q2 support | `papier` | fond forcé au blanc (un fond sombre à l'impression est illisible et ruineux) |
| q3 fond | choix montré | `fond` = blanc / crème / sombre |
| q4 police | choix montré | `police` — le nom n'est jamais annoncé pendant le choix |
| q5 couleurs | `systeme` | `couleurs_utilisateur` : la grille est reprise telle quelle |
| d1 relire | `souvent` | interligne 1.8, ligne de 58 caractères, espacement lettres 0.6 pt |
| d1 relire | `parfois` | interligne 1.6, ligne de 64 caractères |
| d2 lettres miroir | `oui` / `parfois` | teinte sur b, d, p, q |
| d3 montrer segmenté vs réécrit | `segmentee` | segmentation seule, **pas** de reformulation |
| d3 | `reecrite` | reformulation autorisée sur les blocs signalés |
| d4 mot compliqué | `bloque` | reformulation autorisée |
| a1 écrire dessus | `oui` / `un_peu` | colonne d'annotation en marge |
| a2 listes | `groupes` | listes groupées par trois, compteur de position |
| a3 reprise | `cherche` / `recommence` | filet de section, compteurs |
| c1 groupes de chiffres | `espace` | regroupement par tranches de trois |
| c2 tableau six colonnes | `doigt` | tableaux larges signalés |
| c2 tableau six colonnes | `abandonne` | tableaux larges découpés |
| r1 où regarder | `pas_vraiment` / `perdu` | filet de section, air proportionnel |
| z1 mnémotechniques | `embrouille` | **désactivés** — cette réponse compte autant que les autres |

## Adapter la façon de poser les questions

Le questionnaire est le seul moment de la skill qui n'est encore adapté à
personne. Dès la première réponse, la présentation change (`dys.py questions`
renvoie ces réglages dans `presentation`) :

| Difficulté | Ce qui change |
|---|---|
| `ligne`, `lettres` | Phrases courtes, aucune négation, aucune double question, montrer plutôt que décrire |
| `attention` | Une question à la fois, annoncer combien il en reste, aucun pavé |
| `chiffres` | Progression figurée `●●●○○`, jamais « 3 sur 14 » |
| `reperage` | Options sur une seule colonne, bien séparées, jamais de grille |
| écriture (dysorthographie) | Uniquement des réponses à cocher |

## Si la personne s'arrête

Elle a le droit. On complète avec les réglages courants (`profil.COURANTS`), on
le dit en une phrase, on n'insiste pas et on ne relance pas :

> J'ai pris des réglages courants pour le reste : Verdana 14, interligne 1.5,
> fond crème. On ajustera sur l'aperçu si ça ne va pas.

Ce qu'elle a répondu avant de s'arrêter n'est jamais écrasé par ces valeurs.
