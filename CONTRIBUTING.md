# Contribuer à dyspositif

Projet bénévole et collaboratif : les propositions sont bienvenues, d'où
qu'elles viennent. Ce document dit comment elles sont accueillies et selon
quelles règles elles sont acceptées.

## Comment ça se passe

1. **Fork** le dépôt (bouton *Fork* en haut de la page GitHub).
2. **Une branche par sujet** : `git checkout -b sortie-des-chronologies`.
3. **Les tests doivent passer** : `python3 tests/test_dys.py`.
4. **Ouvre une pull request** vers `main`. L'intégration continue rejoue les
   tests automatiquement.
5. **La fusion est faite par la mainteneuse** (Chloé Halloin). Personne d'autre
   n'a le droit d'écrire sur `main` — c'est volontaire, pas de la méfiance : ce
   sont des documents d'étudiants qui passent dans cet outil.

Aucune contribution n'est trop petite. Une faute de frappe dans une question du
questionnaire compte autant qu'une nouvelle fonctionnalité — parfois plus, parce
que c'est la formulation qui fait abandonner les gens.

## Ce qui sera accepté sans discussion

- Corrections de bugs accompagnées d'un test qui échouait avant.
- Formulations de questions plus claires, plus courtes, moins jargonneuses.
- Nouvelles correspondances dans `references/troubles.md`, si elles reposent sur
  du vécu ou sur une source.
- Traductions des messages, tant que le vocabulaire reste simple.
- Documentation.

## Ce qui sera discuté avant

- **Un nouveau degré d'intervention** (au-delà des cinq existants). Il faut
  d'abord répondre à : est-ce que le document de sortie contient toujours
  *toute* l'information du document d'entrée ?
- **Une dépendance nouvelle.** L'outil tourne aujourd'hui avec la bibliothèque
  standard de Python. Chaque dépendance ajoutée est une chose de plus à
  installer pour quelqu'un qui veut juste lire son cours.
- **Un changement du parcours en six étapes.** Les conditions de sortie sont ce
  qui empêche de produire quarante pages que personne ne voulait.

## Ce qui sera refusé

- **Le résumé, la synthèse, la fiche, la carte mentale, l'audio.** Le critère :
  *le document de sortie contient-il toute l'information du document d'entrée ?*
  Si non, c'est un autre outil — un bon outil peut-être, mais pas celui-ci.
- **Toute modification du texte qui ne passe pas par les modifications
  suivies.** C'est la garantie centrale : l'utilisateur doit pouvoir tout
  rejeter dans Word.
- **Toute réécriture de valeurs numériques**, y compris « pour simplifier ».
- **Réimplémenter ce que la skill docx fait déjà** (`merge_runs.py`,
  `comment.py`, `validate.py`, `soffice.py`).
- **Présenter un réglage comme un remède.** Aucune police ne soigne la
  dyslexie ; on propose ce que des personnes préfèrent, et on le dit comme ça.

## Les règles du code

- Python 3.9+, bibliothèque standard uniquement (`defusedxml` en option, avec
  repli).
- Le code, les commentaires et les commits sont en français — comme les
  utilisateurs de la skill.
- **Un commentaire explique pourquoi, jamais quoi.** Le code dit déjà ce qu'il
  fait.
- Tout ce qui touche au texte passe par `dyslib/suivi.py`. Si tu as besoin
  d'écrire ailleurs, c'est probablement le signe qu'il faut en parler d'abord.
- Ne jamais reformater ni indenter le XML : Word interprète les espaces entre
  balises comme du contenu.
- Un nouveau comportement vient avec un test. Un bug corrigé vient avec le test
  qui échouait.

## Si tu contribues sans coder

C'est au moins aussi utile :

- **Raconter ce qui te gêne** quand tu lis un cours, et ce que tu fais pour t'en
  sortir. Le questionnaire est fait de ça.
- **Tester la skill sur tes propres cours** et dire ce qui rate.
- **Relire les questions** : est-ce qu'elles se répondent en une seconde ?
  est-ce qu'elles supposent de savoir ce qu'est un interligne ?

Ouvre une *issue*, ça suffit.

## Code de conduite

Ce projet suit son [code de conduite](CODE_OF_CONDUCT.md). En participant, tu
acceptes de le respecter.

## Licence

En contribuant, tu acceptes que ta contribution soit publiée sous [licence
MIT](LICENSE), comme le reste du projet.
