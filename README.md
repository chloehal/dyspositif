# dyspositif

**Une skill Claude qui adapte un cours au lieu de le résumer.**

Tu lui donnes le Word de ton prof, elle te rend le même Word — mêmes mots,
mêmes images, mêmes tableaux — mais lisible pour toi. Pas une fiche, pas un
résumé, pas une carte mentale : *toute* l'information est encore là.

```
cours.docx  ──▶  questionnaire  ──▶  aperçu 1 page  ──▶  sortie.docx
                  (une fois)          (tu valides)        + fichier de contrôle
```

---

## Le principe

Les personnes dys ont déjà leurs contournements : codes couleur, repères
visuels, moyens mnémotechniques inventés. Elles n'attendent pas qu'on leur
enseigne une bonne façon de lire.

> **dyspositif encode le système de l'utilisateur. Il n'impose pas le sien.**

Les préréglages par trouble sont un point de départ quand la personne ne sait
pas quoi demander — jamais une prescription. Chaque fois qu'une règle générale
s'oppose à une préférence exprimée, c'est la préférence qui gagne.

## En quoi ça aide

Chaque réglage répond à une gêne précise, décrite par la personne dans ses
mots. Rien n'est appliqué « parce que c'est bien pour les dys ».

| Ce que tu dis | Ce qui change dans le document | Pourquoi ça aide |
|---|---|---|
| « Je perds ma ligne, je relis la même phrase » | Lignes raccourcies à ~58 caractères, interligne 1.8, texte non justifié | Plus la ligne est courte, plus le retour à la ligne suivante est court : l'œil a moins de distance à parcourir, donc moins d'occasions de retomber sur la mauvaise. Le justifié fabrique des rivières blanches verticales qui tirent le regard hors de la ligne |
| « Je confonds les lettres qui se ressemblent » | `b` `d` `p` `q` reçoivent une nuance de couleur, espacement entre lettres augmenté | Le mot garde sa silhouette d'ensemble — celle qu'on reconnaît d'un coup d'œil — mais le caractère qui trompe s'annonce. Pas de police bizarre imposée : juste un signal là où ça coince |
| « Je décroche, je pense à autre chose » | Phrases longues coupées à leurs articulations, listes groupées par trois, compteurs « 3 sur 7 », filet coloré en marge | Une phrase de quarante mots demande de tenir quarante mots en mémoire avant de comprendre. Coupée en trois, chaque morceau se comprend seul. Et après une pause, le filet en marge et le compteur disent où tu en étais |
| « Les chiffres et les tableaux me perdent » | `1247893` → `1 247 893`, distinction visuelle du 3/8 et du 1/7, tableaux de six colonnes découpés en tableaux de trois | Un nombre en tranches de trois se lit par blocs au lieu de se compter chiffre par chiffre. Un tableau large oblige à suivre une ligne *et* une colonne en même temps : découpé, il n'y a plus qu'un seul fil à tenir |
| « Je ne sais pas où regarder sur la page » | Hiérarchie des titres remise d'aplomb, air proportionnel à la densité, un seul fil de lecture | La page cesse d'être un mur uniforme : elle indique par sa forme où commence quoi, et les passages difficiles respirent plus que les faciles |
| « Je lis bien, c'est juste fatigant » | Corps à 14, fond crème plutôt que blanc pur, marges plus larges | Moins de contraste brutal, moins d'effort d'accommodation : on tient plus longtemps avant que ça pique |
| « J'ai mes couleurs à moi » | Tes couleurs sont reprises telles quelles, et l'outil va chercher ailleurs pour les siennes | Ton système existe déjà et il marche. Le travail de la skill est de l'appliquer plus vite qu'à la main, pas de le remplacer |

### Ce que ça change vraiment

**Tu ne repars pas de zéro.** C'est ton cours, avec les schémas de ton prof, les
tableaux de ton prof, la numérotation de ton prof. Pas un document reconstruit
où il manquerait le schéma qui tombe à l'examen.

**Tu gardes la main.** Chaque changement de texte est une modification suivie :
si une coupure de phrase te gêne, tu la rejettes d'un clic, dans Word, sans
revenir demander quoi que ce soit. L'outil propose, tu tranches.

**Tu remplis le questionnaire une fois.** Pas à chaque cours. Le deuxième
document commence par une ligne — « Profil actif : Verdana 14, interligne 1.8,
fond sombre. J'applique tel quel ? » — et enchaîne directement.

**Tu vois avant de t'engager.** Une page d'aperçu, regardée par la skill avant
de t'être montrée, et la question posée à l'envers : « qu'est-ce qui ne va
pas ? » plutôt que « ça te va ? ». C'est ce qui fait remonter les vrais
problèmes au lieu d'un oui poli.

**Rien n'est ajouté en douce.** Ce que la skill invente — un moyen
mnémotechnique, un avertissement sur un tableau — va en commentaire Word, jamais
dans le texte, et figure dans le fichier de contrôle. Tu sais toujours ce qui
vient de ton prof et ce qui vient de l'outil.

### Une session type

> **Toi** — Je suis dyslexique et j'ai un TDAH. J'ai ce cours de droit
> constitutionnel de 30 pages à réviser, je n'arrive pas à le lire.
>
> **La skill** — Cinq questions, plus quelques-unes selon tes réponses. Tu peux
> t'arrêter quand tu veux, je prends des réglages courants pour le reste.
> *(1/3)* Quand tu lis un document, qu'est-ce qui te gêne le plus ? …
>
> *[trois questions, puis trois autres — dont deux où on te montre le même
> paragraphe en plusieurs versions au lieu de te parler de polices]*
>
> **La skill** — D'après tes réponses : Verdana 14, interligne 1.8, fond sombre,
> lignes de 58 caractères, b/d teintés en orange, listes numérotées et groupées
> par trois. Tu m'avais dit garder le bleu pour les définitions : je ne
> l'utilise pas ailleurs. Ça te va ?
>
> **La skill** — 30 pages, 214 blocs. 34 passages denses repérés, soit 16 %. Je
> peux les alléger, ou m'en tenir à la mise en forme et à la structure.
>
> **La skill** — Voilà à quoi ressemble la première page. Qu'est-ce qui ne va
> pas ?
>
> **Toi** — L'interligne est trop grand en fait.
>
> *[réglage, nouvelle page d'aperçu — le cycle coûte quelques secondes]*
>
> **La skill** — Voilà le document complet. 34 phrases longues coupées, 6 listes
> sorties, 2 tableaux découpés, aucun mot changé. Pour annuler quoi que ce
> soit : onglet Révision → Rejeter.

## Ce qu'elle fait, ce qu'elle ne fait pas

Un seul critère tranche tous les cas ambigus :

> *Le document de sortie contient-il **toute** l'information du document
> d'entrée ?*

| ✅ Dans le périmètre | ❌ Hors périmètre |
|---|---|
| Police, corps, interligne, longueur de ligne, fond | Résumé, synthèse |
| Couper les phrases de quarante mots à leurs articulations | Fiche de révision |
| Sortir et numéroter les listes enfouies dans une phrase | Carte mentale |
| Regrouper les chiffres, teinter les b/d/p/q | Version audio |
| Découper les tableaux de six colonnes | Ajouter du contenu au cours |

Hors périmètre ne veut pas dire « refus sec » : la skill le dit et propose ce
qu'elle sait faire à la place.

## À quoi ça ressemble

**Avant** — une phrase de quarante mots, justifiée, en Calibri 11 :

> La séparation des pouvoirs, qui constitue le principe cardinal du droit
> constitutionnel moderne, suppose que les fonctions législative, exécutive et
> juridictionnelle soient confiées à des organes distincts, car la concentration
> de ces fonctions conduirait à l'arbitraire, tandis que leur répartition
> garantit un contrôle mutuel.

**Après** — coupée à ses connecteurs, **sans un mot changé** :

> La séparation des pouvoirs, qui constitue le principe cardinal du droit
> constitutionnel moderne, suppose que les fonctions législative, exécutive et
> juridictionnelle soient confiées à des organes distincts,
> **car** la concentration de ces fonctions conduirait à l'arbitraire,
> **tandis que** leur répartition garantit un contrôle mutuel.

Et une liste que la phrase annonçait sans la montrer :

| Avant | Après |
|---|---|
| « Les six causes de la Révolution française sont la crise financière, la mauvaise récolte, la pression fiscale, la contestation des privilèges, la diffusion des idées des Lumières et le blocage des états généraux. » | Les six causes de la Révolution française sont :<br>1 sur 6 — la crise financière<br>2 sur 6 — la mauvaise récolte<br>3 sur 6 — la pression fiscale<br><br>4 sur 6 — la contestation des privilèges<br>5 sur 6 — la diffusion des idées des Lumières<br>6 sur 6 — le blocage des états généraux |

Savoir qu'il y en a **six**, c'est pouvoir vérifier qu'on n'en oublie aucune.
Le groupement par trois, c'est pour ne pas saturer la mémoire de travail.

## Les trois garanties

**1. Rien ne peut être perdu.** Un `.docx` est une archive XML : la skill
l'ouvre, modifie les propriétés concernées, la referme. Elle ne reconstruit
jamais un document à partir de son texte extrait — la manière la plus sûre de
perdre un schéma dans un cours de sciences. Images, tableaux, en-têtes, notes
de bas de page, numérotations, liens : jamais touchés, donc jamais perdus.
C'est structurel, pas un effort.

**2. Tout est rejetable.** Chaque modification du texte est une modification
suivie Word (`<w:ins>` / `<w:del>`) signée « dyspositif ». Tu vois l'original
juste à côté, et l'onglet *Révision* te laisse rejeter n'importe quel
changement, un par un. La mise en forme, elle, ne touche à aucun mot.

**3. C'est vérifiable par machine.** Pas « fais-moi confiance » :

```bash
python scripts/dys.py verifier sortie.docx --original cours.docx
```

```json
{
  "validate.py":        { "passe": true },
  "images":             { "avant": 1, "apres": 1 },
  "tableaux":           { "avant": 2, "apres": 5 },
  "valeurs_numeriques": { "identiques": true, "manquants_ou_modifies": [] },
  "verdict": "passe"
}
```

La commande échoue si du texte a changé sans modification suivie autour, si une
image ou un tableau a disparu, ou si une valeur numérique du cours ne se
retrouve pas à l'identique.

## Installer

```bash
git clone https://github.com/ChloeHal/dyspositif.git
ln -s "$PWD/dyspositif" ~/.claude/skills/dyspositif
```

La skill s'appuie sur la skill `docx` livrée avec Claude Code (`merge_runs.py`,
`comment.py`, `validate.py`, `soffice.py`) — elle ne réimplémente rien. Si elle
n'est pas trouvée toute seule :

```bash
export DYSPOSITIF_SKILL_DOCX=/chemin/vers/skills/docx
export DYSPOSITIF_PYTHON=/chemin/vers/python   # validate.py veut lxml + defusedxml, Python ≥ 3.10
```

Pour l'aperçu visuel (facultatif mais recommandé) :

```bash
brew install --cask libreoffice && brew install poppler
```

Sans eux, `dys.py apercu` s'arrête en le disant. Il ne montre jamais une page
que personne n'a regardée.

## Le parcours en six étapes

Chaque étape a une **condition de sortie**. On ne passe pas à la suivante tant
qu'elle n'est pas remplie : c'est ce qui évite de produire quarante pages que
personne ne voulait.

| # | Étape | Condition de sortie |
|---|---|---|
| 1 | **Cerner les besoins** — questionnaire, une seule fois dans une vie | L'utilisateur a répondu, ou a demandé à s'arrêter |
| 2 | **Appliquer les besoins** — montrer les réglages avant d'agir | Le profil est enregistré et validé |
| 3 | **Recevoir le document** — format, PDF scanné, volume et coût annoncés | L'utilisateur sait ce que ça va coûter |
| 4 | **Modifier** — forme, segmentation, structure, puis reformulation | Le document s'ouvre sans erreur |
| 5 | **Aperçu d'une page** — regardée avant d'être montrée | L'utilisateur a validé. Un silence n'est pas une validation |
| 6 | **Document complet** — vérifié, livré avec le mode d'emploi du retour arrière | L'utilisateur sait comment annuler |

### Le questionnaire, en détail

C'est la partie la plus travaillée de la skill, parce que c'est celle qui fait
abandonner les gens. Quatre règles :

- **La première question n'est pas un diagnostic.** Beaucoup d'adultes n'ont
  jamais été testés. Demander une étiquette exclut précisément ceux qui en
  auraient le plus besoin. On entre par « qu'est-ce qui te gêne le plus quand tu
  lis ? », et l'étiquette n'est jamais renvoyée à quelqu'un qui ne l'a pas
  revendiquée.
- **Toujours des réponses à cocher.** Devant une dysorthographie, demander
  d'écrire, c'est demander exactement ce qui coûte le plus.
- **Montrer plutôt que décrire.** « Veux-tu teinter les lettres miroir ? » est
  une question sans réponse possible. On montre trois versions du *même*
  paragraphe et on fait choisir.
- **On peut s'arrêter à tout moment.** On complète avec des réglages courants,
  on le dit en une phrase, on n'insiste pas.

Le questionnaire se ramifie : cinq questions pour tout le monde, puis seulement
les branches correspondant aux difficultés déclarées. Huit questions pour la
plupart des gens.

```bash
python scripts/dys.py questions --troubles dyscalculie
# → branche « chiffres » seule, progression figurée ●●○○ (jamais « 3 sur 14 »)
```

## Les commandes

| Commande | Ce qu'elle fait |
|---|---|
| `dys.py profil` | Charge, enregistre ou oublie le profil (`~/.dyspositif/profil.json`) |
| `dys.py questions` | Les questions à poser — et elles seules |
| `dys.py analyser` | Volume, densité, tableaux larges, listes enfouies, PDF scanné |
| `dys.py listes` | Énumérations repérées, à confirmer avant d'agir |
| `dys.py appliquer` | Adapte le document, écrit le fichier de contrôle |
| `dys.py commenter` | Ajoute un commentaire Word (les mnémotechniques vont là) |
| `dys.py apercu` | Rend les premières pages en images, à regarder |
| `dys.py verifier` | validate.py + images, tableaux, valeurs numériques |

Une session type :

```bash
python scripts/dys.py profil                                   # déjà un profil ?
python scripts/dys.py analyser cours.docx                      # 38 pages, 14 % dense
python scripts/dys.py appliquer cours.docx apercu.docx --pages 1
python scripts/dys.py apercu apercu.docx                       # regarder
python scripts/dys.py appliquer cours.docx sortie.docx         # tout
python scripts/dys.py verifier sortie.docx --original cours.docx
```

Chaque `appliquer` écrit un **fichier de contrôle** `.controle.md` à côté du
document : ce qui a changé, ce qui a été ajouté par l'outil, et chaque nombre
regroupé avec sa valeur d'origine.

## Quelques choix expliqués

<details>
<summary><b>Pourquoi la segmentation avant la reformulation</b></summary>

Couper une phrase à ses connecteurs logiques garde exactement les mêmes mots :
zéro risque de déformer le cours. Ça règle la majorité des cas. On ne reformule
que ce qui résiste — et seulement si le profil l'autorise, après une question
qui montre les deux versions et laisse choisir.
</details>

<details>
<summary><b>Pourquoi les mnémotechniques sont des commentaires Word</b></summary>

Un commentaire est sans ambiguïté une annotation : impossible de le confondre
avec le cours du professeur, et il se supprime d'un clic. Dans le corps du
texte, un acronyme ajouté par l'outil deviendrait, trois relectures plus tard,
une phrase du prof. Et jamais de mnémotechnique sur un contenu qu'on n'est pas
sûr d'avoir compris : un acronyme faux s'ancre en mémoire, et il faudra le
désapprendre.
</details>

<details>
<summary><b>Pourquoi OpenDyslexic n'est pas présentée comme un remède</b></summary>

Elle est proposée parce que des personnes la préfèrent, et c'est une raison
suffisante. Mais les études disponibles ne montrent pas de gain mesurable par
rapport à Arial ou Verdana. Ce qui est mieux établi : raccourcir les lignes,
augmenter l'espacement entre lettres et entre mots, éviter le texte justifié,
écarter le blanc pur. C'est là que va l'effort.
</details>

<details>
<summary><b>Pourquoi une fausse liste est pire qu'un paragraphe dense</b></summary>

`dys.py listes` ne propose une énumération que si la phrase l'annonce
(« les conditions sont… », « on distingue… », deux points). Deux virgules et un
« et » ne suffisent pas : une liste inventée fait apprendre une structure qui
n'existe pas. En cas de doute, on s'abstient — et on le dit.
</details>

## Comment ça marche, sous le capot

### Un .docx est un fichier zip

Rien de plus. À l'intérieur, du XML :

```
cours.docx
├── word/document.xml      le texte et sa structure  ← le seul qu'on modifie vraiment
├── word/styles.xml        les styles (police, corps, interligne par défaut)
├── word/settings.xml      les réglages du document
├── word/media/image1.png  les images  ← jamais touchées
└── word/_rels/…           qui pointe vers quoi
```

D'où la chaîne, identique à chaque exécution :

```
ouvrir (unzip)
   └─ supprimer les liens symboliques      un document reçu d'un tiers n'est pas de confiance
   └─ merge_runs.py                        recoller les runs éclatés
        ├─ segmentation                    ┐
        ├─ chiffres                        ├─ étapes qui touchent au texte → suivies
        ├─ listes                          ┘
        ├─ tableaux                        signalés (commentaire) ou découpés
        └─ mise en forme                   styles, marges, fond, air, teintes
   └─ enregistrer sans reformater le XML
refermer (zip)
   └─ validate.py --original --author dyspositif
```

**Pourquoi `merge_runs` d'abord ?** Word éclate une phrase en dizaines de
« runs » XML (une correction orthographique, un identifiant de révision, et hop,
un run de plus). Une phrase qu'on lit à l'écran n'existe donc souvent nulle part
comme chaîne continue dans le fichier. Sans cette étape, une recherche sur trois
échoue *en silence*.

**Pourquoi le texte avant la mise en forme ?** Teinter les `b` et les `d` oblige
à découper chaque run en morceaux d'une lettre. Si on faisait ça d'abord, les
étapes suivantes travailleraient sur des confettis. Le texte passe donc en
premier, sur des runs encore entiers ; la forme ferme la marche.

### La modification suivie, concrètement

Regrouper `1247893` en `1 247 893`, c'est modifier du texte. Donc :

```xml
<w:del w:author="dyspositif" w:date="…">
  <w:r><w:delText>1247893</w:delText></w:r>      <!-- ce qui disparaît -->
</w:del>
<w:ins w:author="dyspositif" w:date="…">
  <w:r><w:t>1 247 893</w:t></w:r>                 <!-- ce qui apparaît -->
</w:ins>
```

Dans Word, tu vois les deux, et *Révision → Rejeter* restaure le premier.
D'où l'invariant que tout le projet respecte :

> **Si on retire les `<w:ins>` et qu'on rend leur texte aux `<w:del>`, on doit
> retomber sur le document d'origine, caractère pour caractère.**

C'est exactement ce que `validate.py --original --author` vérifie, et ce que le
test `test_rejeter_tout_restitue_loriginal` re-vérifie de son côté, sans lui.
Un paragraphe inséré entier suit la même logique : sa marque de fin de
paragraphe est marquée insérée, et tous ses runs sont dans un `<w:ins>`.

### Ce que fait chaque module

| Module | Rôle |
|---|---|
| `ooxml.py` | Ouvre et referme `document.xml` sans l'abîmer : conserve les déclarations de namespaces de la racine, respecte l'ordre des enfants imposé par le schéma, ne reformate jamais |
| `paquet.py` | zip/unzip, sécurité de l'archive, et appels à la skill docx |
| `profil.py` | Traduit les réponses du questionnaire en paramètres, les enregistre, les résume en une ligne |
| `analyse.py` | Lit le document *sans le faire entrer en contexte* : volume, densité, tableaux, listes enfouies, PDF scanné |
| `suivi.py` | Les primitives de modification suivie. Tout passage par le texte transite ici — c'est le point de contrôle |
| `forme.py` | Le degré « mise en forme » : styles, formatage direct neutralisé, marges, fond, air, filets, teintes |
| `texte.py` | Segmentation et regroupement des chiffres |
| `listes.py` | Sortie des énumérations confirmées |
| `tableaux.py` | Signalement ou découpage des tableaux larges |
| `annotations.py` | Commentaires Word (mnémotechniques, avertissements) |
| `controle.py` | Écrit le fichier de contrôle |

### Deux ou trois détails qui font la différence

**L'air est proportionnel à la densité.** Chaque paragraphe reçoit un indice de
lisibilité (longueur moyenne de phrase + proportion de mots longs), et son
espacement en découle. Les passages difficiles respirent, les faciles restent
compacts. Sans ça, un document adapté double de longueur sans rien gagner — et
devient impossible à imprimer.

**Le formatage direct est neutralisé.** Une taille appliquée à la main l'emporte
sur le style : un cours récupéré en est truffé. Les tailles ne sont pas écrasées
mais mises à l'échelle, pour qu'un titre reste plus gros que le corps — la
hiérarchie du document est une information, on ne l'aplatit pas.

**Les couleurs de l'utilisateur sont prioritaires.** Si le bleu est déjà pris
pour les définitions, la teinte des lettres miroir ira chercher ailleurs dans la
palette. La skill s'insère dans un système existant, elle ne le recouvre pas.

**Le coût est borné.** Les trois premiers degrés (forme, segmentation,
structure) sont déterministes : ils s'appliquent au document entier sans coûter
un token. Seul ce qui se paie — reformulation, confirmation des listes — est
limité à `--pages 1` tant que l'utilisateur n'a pas validé l'aperçu.

## Structure

```
SKILL.md                       le parcours en six étapes — c'est ce document qui décide
references/questionnaire.json  le texte exact des questions et leur branchement
references/troubles.md         ce que chaque réponse implique
references/reglages.md         chaque paramètre et sa justification
references/reformulation.md    règles de fidélité au contenu
scripts/dys.py                 les commandes
scripts/dyslib/                ooxml · profil · analyse · suivi · forme · texte · tableaux · listes
tests/                         fixtures et tests
evals.json                     scénarios d'évaluation de la skill
```

## Tests

```bash
python3 tests/test_dys.py
```

Ils fabriquent un cours de test qui contient tout ce qui peut casser — une
image, un tableau de six colonnes, du formatage appliqué à la main, du texte
justifié, une phrase de quarante mots, une liste enfouie de six éléments, des
nombres longs — puis vérifient, dans cet ordre d'importance :

1. le document produit s'ouvre (`validate.py`, schémas XSD) ;
2. rejeter les modifications suivies restitue **exactement** le texte d'origine ;
3. les images et les tableaux d'origine sont toujours là ;
4. aucune valeur numérique du cours n'a bougé ;
5. le questionnaire ne pose que les branches déclarées.

Les points 1 et 4 sont sautés — explicitement, jamais silencieusement — si la
skill docx ou un Python avec `lxml` manquent.

## Contribuer

Projet bénévole et collaboratif : les propositions sont bienvenues, d'où
qu'elles viennent.

- Tout le monde peut forker et ouvrir une **pull request** ; l'intégration
  continue rejoue les tests automatiquement.
- La **fusion sur `main`** est faite par la mainteneuse. Ce n'est pas de la
  méfiance : ce sont des documents d'étudiants qui passent dans cet outil.
- On peut contribuer **sans coder** — raconter ce qui te gêne quand tu lis,
  tester la skill sur tes cours, relire les questions du questionnaire. C'est au
  moins aussi utile.

Lis [CONTRIBUTING.md](CONTRIBUTING.md) avant d'ouvrir une PR : il dit ce qui
sera accepté sans discussion, ce qui se discute, et ce qui sera refusé (le
résumé, la synthèse et tout ce qui perd de l'information).

Voir aussi le [code de conduite](CODE_OF_CONDUCT.md), la [politique de
sécurité](SECURITY.md) et le [changelog](CHANGELOG.md).

## Limites connues

- **L'aperçu visuel demande LibreOffice et poppler.** Sans eux, la commande
  s'arrête au lieu de montrer une page non vérifiée.
- **Les polices ne sont pas incorporées au document.** Word substitue en
  silence une police absente, et tout le bénéfice disparaît. La skill préfère
  donc des polices présentes partout (Verdana, Arial, Tahoma) et prévient quand
  le choix de l'utilisateur n'en est pas.
- **Les tableaux à cellules fusionnées sont signalés, pas découpés.** Un
  découpage automatique les déformerait.
- **Les PDF scannés ne sont pas océrisés.** Ils sont détectés et dits en
  langage simple, plutôt que de produire un document vide.

## Crédits

- **Conception et recherche** —
  [Marie-Sara Raveneau](https://www.linkedin.com/in/marie-sara-raveneau-1565721b4/)
- **Conception et développement** —
  [Chloé Halloin](https://www.linkedin.com/in/chlo%C3%A9-halloin/)

Sous [licence MIT](LICENSE). Réutilise, forke, adapte — et si tu améliores
quelque chose, [reviens le proposer](CONTRIBUTING.md).
