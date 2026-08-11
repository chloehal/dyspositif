# Règles de fidélité au contenu

À charger avant de toucher au texte — c'est-à-dire avant la segmentation, et à
plus forte raison avant toute reformulation.

## Le seul critère

> Le document de sortie contient-il **toute** l'information du document
> d'entrée ?

Oui → c'est le travail de cette skill. Non → c'est de la synthèse : le dire et
proposer ce qu'on sait faire. Un résumé, une fiche, une carte mentale, une
version audio sont hors périmètre, quelle que soit la façon dont c'est demandé.

## La segmentation avant la reformulation

Couper une phrase de quarante mots à ses connecteurs logiques, en gardant
exactement les mêmes mots, rend sa structure visible sans rien risquer. Cela
règle la majorité des cas.

> La séparation des pouvoirs, qui constitue le principe cardinal du droit
> constitutionnel moderne, suppose que les fonctions soient confiées à des
> organes distincts, **car** la concentration conduirait à l'arbitraire,
> **tandis que** leur répartition garantit un contrôle mutuel.

Coupée à `car` et `tandis que` : trois segments courts, pas un mot changé, pas
un mot perdu. Ne reformuler que ce qui résiste à ce traitement.

Où couper : aux connecteurs logiques (`mais`, `donc`, `car`, `or`, `cependant`,
`tandis que`, `parce que`, `si bien que`, `c'est-à-dire`…), aux relatives
détachées (`, qui`, `, que`, `, dont`), après un deux-points. Jamais à moins de
six mots d'un bord : un membre de trois mots isolé sur sa ligne désoriente.

## Ce qui ne se reformule jamais

- **Les valeurs numériques.** Aucun arrondi, aucune conversion, aucun ordre de
  grandeur « simplifié ». Le regroupement par tranches de trois est le seul
  traitement autorisé, et il ne change pas la valeur.
- **Les dates, les noms propres, les intitulés d'articles et de lois.**
- **Les termes techniques et les définitions.** Un terme de droit, de médecine
  ou de sciences est ce qu'il faut savoir : le remplacer par un synonyme
  approximatif fait échouer à l'examen. Le garder et l'expliquer à côté est
  autorisé ; le remplacer ne l'est pas.
- **Les citations**, y compris leur ponctuation.
- **Les négations et les modalisateurs.** « ne peut pas », « sauf si », « à
  moins que », « uniquement », « sauf exception » portent tout le sens d'une
  règle. Une phrase simplifiée qui perd un `sauf` est fausse.
- **L'ordre des idées**, quand il porte une chronologie ou une hiérarchie.

## Ce qui peut être reformulé

Uniquement les blocs signalés par le diagnostic (`paragraphes_denses`), et
seulement si le profil l'autorise (`reformulation.actif`, issu de la question
qui montre une version segmentée et une version réécrite).

Opérations acceptables :

- passer une tournure passive à l'actif quand l'agent est nommé dans la phrase ;
- défaire une double négation (« il n'est pas exclu que » → « il se peut que ») ;
- sortir une incise de plus de dix mots dans une phrase à part ;
- remplacer un pronom lointain par le nom auquel il renvoie ;
- couper une phrase à son deux-points.

Chacune garde le sens et le vocabulaire technique. Aucune n'invente
d'explication.

## Révéler n'est pas créer

| Révéler — autorisé, gratuit | Créer — à signaler |
|---|---|
| Sortir une liste enfouie dans une phrase | Ajouter un exemple |
| Numéroter et compter ses éléments | Ajouter une définition |
| Rendre visible une chronologie déjà écrite | Fabriquer un acronyme |
| Grouper neuf éléments par trois | Ajouter un titre qui n'existe pas |

Ce qui est créé va **en commentaire Word**, jamais dans le corps du texte, et
est consigné dans le fichier de contrôle. Un commentaire est sans ambiguïté une
annotation : impossible de le confondre avec le cours du professeur, et
l'utilisateur le supprime d'un clic.

**Jamais de mnémotechnique sur un contenu qu'on n'est pas sûr d'avoir
compris.** Un acronyme faux est pire que pas d'acronyme : il s'ancre en mémoire
et il faudra le désapprendre.

## Toute modification du texte passe par les modifications suivies

Segmentation, regroupement de chiffres, sortie de liste, reformulation :
chacune est un `w:ins` / `w:del` signé « dyspositif ». L'utilisateur voit
l'original juste à côté et accepte ou rejette chaque changement un par un dans
son traitement de texte. C'est ce qui rend l'outil sûr à essayer.

La mise en forme pure n'a pas à être suivie : elle ne touche à aucun mot.

Vérification, à chaque livraison :

```bash
python scripts/dys.py verifier sortie.docx --original cours.docx
```

Elle échoue si du texte a changé sans modification suivie autour, si une image
ou un tableau a disparu, ou si une valeur numérique du cours ne se retrouve pas
à l'identique. La règle de fidélité devient vérifiable par machine, au lieu de
reposer sur la bonne volonté.

## En cas de doute

S'abstenir et le dire. Un paragraphe dense laissé tel quel est un échec
mineur ; une phrase dont le sens a glissé est une erreur qui sera révisée,
apprise, et récitée à l'examen.
