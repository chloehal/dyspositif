---
name: dyspositif
description: >
  Adapte un document Word ou PDF existant pour une personne dyslexique,
  dysorthographique, dyscalculique, dyspraxique ou ayant un TDAH, en modifiant
  le fichier d'origine plutôt qu'en le reconstruisant. Utiliser cette skill dès
  qu'un utilisateur parle d'adapter, rendre lisible, rendre accessible, aérer,
  simplifier ou reformater un cours, une synthèse, un support de révision, un
  article ou un document, et dès qu'il mentionne dyslexie, dys, TDAH, troubles
  de l'attention, difficultés de lecture ou de concentration — même sans employer
  le mot « adapter ». Utiliser aussi quand l'utilisateur dit qu'un document est
  trop dense, illisible, indigeste, ou qu'il n'arrive pas à le lire. Ne pas
  utiliser pour produire un résumé, une fiche, une carte mentale ou une version
  audio : ces fonctions relèvent de la synthèse et ne sont pas dans cette skill.
---

# dyspositif

Cette skill améliore un document existant. Elle ne le résume pas.

**Le critère de partage**, à appliquer dès qu'un cas semble ambigu :

> Le document de sortie contient-il toute l'information du document d'entrée ?
> Oui → c'est le travail de cette skill. Il en produit une version condensée →
> hors périmètre, le dire à l'utilisateur et proposer ce qu'on sait faire.

## Le principe qui gouverne tout le reste

Les personnes dys développent leurs propres contournements — codes couleur,
repères visuels, moyens mnémotechniques inventés. Elles n'attendent pas qu'on
leur enseigne une bonne façon de lire : elles attendent qu'on exécute la leur
plus vite qu'à la main.

Cette skill encode donc **le système de l'utilisateur**, elle n'impose pas le
sien. Les préréglages par trouble sont un point de départ quand la personne ne
sait pas quoi demander, jamais une prescription. Chaque fois qu'un choix oppose
une règle générale à une préférence exprimée, suivre la préférence.

---

# Le parcours en six étapes

Chaque étape a une condition de sortie. **Ne pas passer à la suivante tant
qu'elle n'est pas remplie** — c'est ce qui évite de produire quarante pages que
personne ne voulait.

## Étape 1 — Cerner les besoins

Charger le profil : `python scripts/dys.py profil`.

**S'il existe**, le rappeler en une ligne et passer directement à l'étape 3 :

> Profil actif : dyslexie + TDAH, Verdana 14, interligne 1.8, fond sombre.
> J'applique tel quel, ou tu veux ajuster ?

Ne jamais reposer le questionnaire. C'est ce qui rend la skill supportable à
l'usage : personne n'accepte de remplir un formulaire à chaque document.

**S'il n'existe pas**, dérouler le questionnaire. Il se ramifie : cinq questions
pour tout le monde, puis seulement celles qui concernent les difficultés
déclarées. Huit questions pour la plupart des gens, quatorze au maximum pour
quelqu'un qui cumule plusieurs troubles.

`python scripts/dys.py questions --difficultes ligne,chiffres` renvoie les
questions à poser — et **elles seules** —, déjà groupées par trois et
accompagnées des règles de présentation à appliquer. Le texte exact des
questions est dans `references/questionnaire.json`.

### La première question n'est pas un diagnostic

Beaucoup d'adultes n'ont jamais été diagnostiqués, ou l'ont été il y a longtemps,
ou hésitent entre plusieurs troubles. Demander une étiquette exclut précisément
ceux qui en auraient le plus besoin. Entrer par la difficulté ressentie :

> Quand tu lis un document, qu'est-ce qui te gêne le plus ?
> *(plusieurs réponses possibles)*
> — Je perds ma ligne, je relis la même phrase
> — Je confonds des lettres qui se ressemblent
> — Je décroche, je pense à autre chose
> — Les chiffres et les tableaux me perdent
> — Je ne sais pas où regarder sur la page
> — Je lis bien, c'est juste fatigant
> — Je connais mon diagnostic, je préfère le dire

La dernière option ouvre la liste des troubles pour ceux qui la connaissent. Les
autres réponses s'y ramènent en interne, sans jamais renvoyer l'étiquette à la
figure de quelqu'un qui ne l'a pas demandée. Correspondances dans
`references/troubles.md`.

### Trois règles pour toutes les questions

**1. Toujours des réponses à cocher.** Jamais de champ libre. Devant quelqu'un
qui a une dysorthographie, demander d'écrire, c'est demander précisément ce qui
coûte le plus.

**2. Partir d'une situation vécue, jamais d'un réglage.** « Veux-tu teinter les
lettres miroir ? » est une question sans réponse possible : elle suppose qu'on
sache ce que ça donne. « Devant un mot avec des b et des d, tu ralentis pour
vérifier ? » se répond en une seconde. La question porte sur ce que la personne
connaît — sa propre expérience — et c'est nous qui en tirons le réglage.

**3. Montrer plutôt que décrire.** Dès qu'une question porte sur l'apparence ou
sur la forme du texte, présenter deux ou trois versions du **même paragraphe** et
faire choisir. Aucun vocabulaire technique n'est nécessaire, et la réponse est
plus fiable que n'importe quelle déclaration d'intention.

La seule question qui peut rester théorique est celle du trouble, pour ceux qui
connaissent leur diagnostic et préfèrent le donner directement.

### Le socle — pour tout le monde

**1. Qu'est-ce qui te gêne le plus quand tu lis ?** *(voir ci-dessus)*

**2. Où est-ce que tu révises le plus souvent ?**
Sur écran · Sur des feuilles imprimées · Les deux

**3. Laquelle de ces trois pages est la plus reposante pour tes yeux ?**
*(montrer le même paragraphe sur fond blanc, crème et sombre)*

**4. Laquelle de ces versions se lit le plus facilement ?**
*(montrer le même paragraphe en trois polices, sans donner leurs noms)*

**5. Quand tu prends des notes ou que tu révises, tu utilises des couleurs ?**
J'ai mes couleurs pour des choses précises · Je surligne un peu au hasard · Non

Si la première réponse est choisie, enchaîner avec une grille à cocher —
définitions, exemples, à retenir, dates — et reprendre ces couleurs telles
quelles dans le document. C'est le moment le plus important du questionnaire :
on récupère un système déjà construit au lieu d'en imposer un.

### Les branches — seulement si la difficulté est déclarée

**Déchiffrage** *(perte de ligne, confusion de lettres)*

- **Ça t'arrive de relire une ligne parce que tu l'as sautée ou refaite ?**
  Souvent · De temps en temps · Non
- **Devant un mot avec des b, des d, des p ou des q, tu ralentis pour vérifier ?**
  Oui · Parfois · Non
- **Laquelle de ces deux versions t'aide le plus ?**
  *(montrer une vraie phrase de cinq lignes tirée du cours : à gauche coupée en
  segments courts avec les mêmes mots, à droite réécrite plus simplement)*
- **Quand un mot compliqué arrive dans ton cours, tu fais quoi ?**
  Je continue et j'espère comprendre plus loin · Je m'arrête et je bloque ·
  Je devine d'après le reste

**Attention** *(décrochage)*

- **Tu écris sur tes cours quand tu révises ?** *(surligner, annoter, dessiner)*
  Oui souvent · Un peu · Jamais
- **Laquelle de ces deux listes tu retiendrais mieux ?**
  *(montrer neuf éléments d'affilée, puis les mêmes en trois groupes de trois)*
- **Quand tu reprends ton cours après une pause, tu retrouves où tu en étais ?**
  Tout de suite · Je cherche un peu · Je recommence la page

**Chiffres**

- **Lequel des deux tu lis le plus vite ?**
  *(montrer `1247893` puis `1 247 893`)*
- **Devant un tableau de six colonnes, tu fais quoi ?**
  J'arrive à le lire · Je suis les lignes avec le doigt · J'abandonne

**Repérage dans la page**

- **Sur une page bien remplie, tu sais où poser les yeux en premier ?**
  Oui · Pas vraiment · Je suis perdu

**Pour tout le monde, en dernier**

- **Tu utilises des trucs pour retenir ?** *(phrases, images, acronymes)*
  Oui, j'en invente · J'aimerais bien mais je n'y arrive pas ·
  Non, ça m'embrouille plus qu'autre chose

La troisième réponse compte autant que les deux autres : pour certaines
personnes, un moyen mnémotechnique ajoute une couche à mémoriser. Ne pas
l'imposer.

### Adapter aussi la façon de poser les questions

Le questionnaire est le seul moment de la skill qui n'est encore adapté à
personne. Dès la première réponse, ajuster la présentation :

| Difficulté déclarée | Ce qui change dans la suite du questionnaire |
|---|---|
| Déchiffrage | Phrases courtes, jamais de négation ni de double question. Montrer, ne pas décrire |
| Attention | Annoncer combien il en reste, une question à la fois, aucun pavé de texte |
| Chiffres | Progression figurée (●●●○○), jamais « 3 sur 14 » |
| Repérage dans la page | Options sur une seule colonne, bien séparées, jamais de grille |
| Écriture | Uniquement des réponses à choisir, jamais de champ libre |

Ces règles valent aussi pour la première question, qui précède toute adaptation :
la formuler donc au plus accessible par défaut — courte, concrète, sans jargon.

Annoncer d'emblée le nombre de questions et la possibilité de s'arrêter :

> Cinq questions, plus quelques-unes selon tes réponses. Tu peux t'arrêter quand
> tu veux, je prends des réglages courants pour le reste.

Si la personne s'arrête, compléter avec les réglages courants, le dire en une
phrase, ne pas relancer.

> **Condition de sortie :** l'utilisateur a répondu, ou a demandé à s'arrêter.

## Étape 2 — Appliquer les besoins

Traduire les réponses en paramètres concrets, et **les montrer avant d'aller plus
loin**. C'est une étape distincte de la précédente : l'utilisateur a parlé dans
ses mots, il faut vérifier qu'on a compris.

> D'après tes réponses : Verdana 14, interligne 1.8, fond sombre, lignes de
> 62 caractères, b/d teintés en bleu, listes numérotées et groupées par trois.
> Tu m'avais dit utiliser le bleu pour les définitions : je le garde pour ça et
> je prends du orange pour les lettres. Ça te va ?

Enregistrer le profil :

```bash
python scripts/dys.py profil --reponses reponses.json   # traduit puis enregistre
python scripts/dys.py profil --definir taille_pt=15     # ajuster un réglage
```

Les correspondances entre réponses et paramètres sont dans
`references/troubles.md` et `references/reglages.md` — ne charger ces fichiers
qu'à ce moment, et seulement ceux qui concernent les troubles déclarés.

> **Condition de sortie :** le profil est enregistré et validé par l'utilisateur.

## Étape 3 — Recevoir le document

Vérifier avant tout traitement :

- **Format.** `.docx` → édition directe. `.pdf` → convertir en `.docx` d'abord.
  La sortie est toujours du Word, pour que l'utilisateur garde la main.
- **PDF scanné.** Aucun texte extractible : le détecter et le dire en langage
  simple, plutôt que de produire un document vide.
- **Sécurité.** Un document reçu d'un tiers n'est pas de confiance : les liens
  symboliques sont supprimés à la décompression.

```bash
python scripts/dys.py analyser cours.docx      # volume, densité, tableaux, listes
python scripts/dys.py analyser cours.pdf       # texte extractible, ou pages scannées
```

L'analyse ne fait pas entrer le document en contexte. **Annoncer le volume et le
coût avant de lancer quoi que ce soit** :

> 38 pages, 240 blocs. 34 passages denses repérés, soit 14 %.
> Je peux les alléger, ou m'en tenir à la mise en forme et à la structure.

Devant un PDF sans texte extractible, ne pas produire de document vide. Dire ce
qui se passe et proposer une suite concrète :

> Ton PDF contient des photos de pages, pas du texte : il n'y a rien à adapter
> en l'état. Si tu as le fichier Word d'origine, je pars de là. Sinon, il faut
> d'abord une reconnaissance de texte — je peux t'indiquer comment faire.

> **Condition de sortie :** le format est traitable et l'utilisateur sait ce que
> ça va coûter.

## Étape 4 — Modifier le document

Ordre d'application, du moins risqué au plus risqué :

1. **Mise en forme** — styles du document, puis neutralisation du formatage
   direct qui les contredit.
2. **Segmentation** — phrases longues coupées à leurs articulations.
3. **Structure** — listes enfouies, chronologies, groupements.
4. **Reformulation** — uniquement les blocs signalés par le diagnostic.

```bash
python scripts/dys.py listes cours.docx > candidats.json   # à confirmer, pas à appliquer
python scripts/dys.py appliquer cours.docx apercu.docx \
    --pages 1 --etapes forme,segmentation,chiffres,tableaux,listes \
    --listes-spec candidats.json
```

Détail dans `references/reglages.md` et `references/reformulation.md`.

**Économie de tokens à cette étape :** les trois premiers degrés sont
déterministes et s'appliquent au document entier sans coût. Ce qui se paie —
reformulation, confirmation des listes — reste limité à `--pages 1` à ce stade :
inutile de payer pour quarante pages que l'utilisateur va peut-être refuser.

**Toute modification du texte passe par les modifications suivies de Word.**
Chaque changement est un `<w:ins>`/`<w:del>` signé « dyspositif ». L'utilisateur
voit l'original juste à côté et accepte ou rejette chaque changement un par un,
dans son traitement de texte. La mise en forme pure n'a pas à être suivie : elle
ne touche à aucun mot.

Ce que la skill ajoute d'elle-même — moyens mnémotechniques, avertissement sur
un tableau — va **en commentaire Word**, jamais dans le corps du texte :

```bash
python scripts/dys.py commenter entree.docx sortie.docx --paragraphe 12 \
    --texte "Moyen mnémotechnique ajouté par l'outil : ..."
```

Chaque exécution écrit un **fichier de contrôle** à côté du document
(`sortie.controle.md`) : ce qui a changé, ce qui a été ajouté, et la liste des
nombres regroupés avec leur valeur d'origine.

> **Condition de sortie :** le document modifié s'ouvre sans erreur.

## Étape 5 — Renvoyer un aperçu d'une page

**Ne jamais livrer le document complet en premier.**

Produire une seule page, et **la regarder avant de la montrer** :

```bash
python scripts/dys.py apercu apercu.docx --pages 1
```

Puis lire l'image produite. Une police substituée, un contraste illisible ou un
tableau cassé se voient à l'œil et jamais dans le XML. Si le rendu est mauvais,
corriger avant de le montrer — pas après. (La commande a besoin de LibreOffice
et de `pdftoppm` ; si elle dit qu'ils manquent, le signaler à l'utilisateur
plutôt que de montrer une page qu'on n'a pas vue.)

Présenter la page et demander franchement :

> Voilà à quoi ça ressemble. Qu'est-ce qui ne va pas ?

Poser la question à l'envers — « qu'est-ce qui ne va pas » plutôt que « ça te
va ? » — donne des retours utiles au lieu d'un oui poli.

Si l'utilisateur veut des ajustements, retourner à l'étape 2, régler, et
reproduire une page. Le cycle est court et ne coûte presque rien : c'est tout
l'intérêt de s'arrêter ici.

> **Condition de sortie :** l'utilisateur a validé explicitement. Un silence
> n'est pas une validation.

## Étape 6 — Renvoyer le document complet

Appliquer les mêmes réglages à l'ensemble, sans `--pages`, y compris la
reformulation des blocs restants.

Vérifier que rien n'est passé en douce :

```bash
python scripts/dys.py verifier sortie.docx --original cours.docx
```

Cette commande signale tout texte modifié **sans** modification suivie autour
(via `validate.py` de la skill docx), toute image ou tableau disparu, et toute
valeur numérique du cours qui ne se retrouve pas à l'identique. La règle de
fidélité devient vérifiable par machine, au lieu de reposer sur la bonne
volonté.

Livrer en disant en une ligne ce qui a été fait, et **comment revenir en
arrière** : dans Word, l'onglet Révision permet de rejeter n'importe quel
changement. C'est ce qui rend l'outil sûr à essayer.

> **Condition de sortie :** le document est livré, il s'ouvre, et l'utilisateur
> sait comment annuler ce qui ne lui convient pas.

---

# Références

## Les commandes

| Commande | Ce qu'elle fait |
|---|---|
| `dys.py profil` | Charge, enregistre ou oublie le profil |
| `dys.py questions` | Les questions à poser, et elles seules |
| `dys.py analyser` | Volume, densité, tableaux larges, listes enfouies, PDF scanné |
| `dys.py listes` | Énumérations repérées, à confirmer avant d'agir |
| `dys.py appliquer` | Adapte le document, écrit le fichier de contrôle |
| `dys.py commenter` | Ajoute un commentaire Word |
| `dys.py apercu` | Rend les premières pages en images, à regarder |
| `dys.py verifier` | validate.py + images, tableaux, valeurs numériques |

## S'appuyer sur la skill docx, ne rien réimplémenter

La skill `docx` fournit déjà toute la chaîne d'édition OOXML. La réécrire serait
du travail perdu et moins fiable. `dys.py` l'appelle : `merge_runs.py` pour
recoller les runs éclatés — sans lui, une recherche sur trois échoue en
silence —, `comment.py` pour les six fichiers croisés qu'exige un commentaire
Word, `validate.py` pour la vérification, `soffice.py` pour le rendu.

Si elle n'est pas trouvée automatiquement :

```bash
export DYSPOSITIF_SKILL_DOCX=/chemin/vers/skills/docx
export DYSPOSITIF_PYTHON=/chemin/vers/python-avec-lxml   # validate.py a besoin de lxml
```

La chaîne, si un traitement doit être fait à la main :

```bash
unzip -q cours.docx -d unpacked/
find unpacked -type l -delete              # document tiers : pas de confiance
python scripts/merge_runs.py unpacked/     # recoller les runs fragmentés
# modifier unpacked/word/document.xml — ne jamais reformater ni indenter
(cd unpacked && zip -Xr ../sortie.docx .)
python scripts/office/validate.py sortie.docx --original cours.docx --author "dyspositif"
```

## On modifie le fichier, on ne le refabrique pas

Un `.docx` est une archive XML. Ouvrir, modifier les propriétés de mise en forme,
refermer. Les images, tableaux, en-têtes, notes de bas de page, numérotations et
liens ne sont jamais touchés — donc jamais perdus. C'est une garantie
structurelle, pas un effort.

Ne jamais reconstruire un document à partir de son texte extrait : c'est la
manière la plus sûre de perdre un schéma dans un cours de sciences.

## Les cinq degrés d'intervention

| Degré | Ce qui change | Coût |
|---|---|---|
| **Mise en forme** | Police, taille, espacement, couleurs, marges | Nul |
| **Segmentation** | Phrases longues coupées à leurs articulations | Nul |
| **Structure** | Listes enfouies, chronologies, groupements | Faible |
| **Aération** | Pavés découpés, sous-titres, repères | Faible |
| **Reformulation** | Phrases lourdes simplifiées | Modéré, ciblé |

**La segmentation avant la reformulation.** Couper une phrase longue à ses
connecteurs logiques, en gardant exactement les mêmes mots, rend sa structure
visible sans rien risquer. Essayer cela d'abord. Ne reformuler que ce qui résiste.

## Révéler, plutôt qu'inventer

> Rendre visible une structure déjà présente dans le texte → autorisé, et gratuit.
> Fabriquer un support qui n'y était pas → c'est de la création, à signaler.

Un cours qui écrit « les conditions sont l'urgence, la proportionnalité, la
nécessité et la subsidiarité » contient une liste de quatre enfouie dans une
phrase. La sortir et la numéroter n'invente rien — et savoir qu'il y en a
**quatre**, c'est déjà pouvoir vérifier qu'on n'en oublie aucune.

- **Listes enfouies** — sortir les énumérations noyées dans une phrase.
- **Chronologies** — repérer les marqueurs de séquence et rendre la suite visible.
- **Groupement** — neuf éléments d'affilée saturent la mémoire de travail ;
  trois groupes de trois, sans toucher aux éléments.
- **Compteur de position** — « 3 sur 7 » dans une longue énumération.

En cas de doute sur le fait qu'une énumération en soit vraiment une, s'abstenir :
une fausse liste désoriente plus qu'un paragraphe dense. `dys.py listes` ne
propose que les énumérations que la phrase annonce, et laisse la décision.

## Les moyens mnémotechniques

Activables en option. Ils sont **de la création**, pas de la révélation :

- **Toujours en commentaire Word**, jamais dans le corps du texte. Un commentaire
  est sans ambiguïté une annotation : impossible de le confondre avec le cours du
  professeur, et l'utilisateur le supprime d'un clic.
- **Jamais sur un contenu qu'on n'est pas sûr d'avoir compris.** Un acronyme faux
  est pire que pas d'acronyme : il s'ancre en mémoire et il faudra le désapprendre.

## Mécanismes de mise en forme

Détail et justification dans `references/reglages.md`.

- **Air proportionnel à la densité** — l'espacement suit l'indice de lisibilité
  bloc par bloc. Les passages difficiles respirent, les faciles restent compacts.
- **Filet de section en marge** — un trait vertical coloré par grande partie,
  pour savoir où l'on est sans relire le titre.
- **Lettres miroir teintées** — b, d, p, q reçoivent une nuance légère plutôt
  qu'une police différente. L'utilisateur choisit la teinte.
- **Chiffres** — groupes de trois espacés (en modification suivie : c'est du
  texte), distinction visuelle des paires confondues (3/8, 1/7) si la
  dyscalculie est déclarée.
- **Colonne d'annotation** — marge large maintenue si demandée.
- **Un seul fil de lecture** — jamais deux éléments à suivre en parallèle.
  Tableaux au-delà de trois colonnes découpés ou signalés.

**Sur les polices.** OpenDyslexic est proposée parce que des personnes la
préfèrent, mais les études disponibles ne montrent pas de gain mesurable par
rapport à Arial ou Verdana. Ce qui est mieux établi : augmenter l'espacement
entre lettres et entre mots, raccourcir les lignes, éviter le texte justifié,
écarter le blanc pur. Ne pas présenter OpenDyslexic comme un traitement.

## Pièges connus

- **Ne jamais reformater le XML.** Word interprète les espaces entre balises
  comme du contenu.
- **Formatage direct.** Une taille appliquée à la main l'emporte sur le style.
  Neutraliser ce qui contredit le profil — un cours récupéré en est truffé.
- **Police non installée.** Word substitue en silence, et tout le bénéfice
  disparaît chez l'utilisateur. Cette skill n'incorpore pas les polices : elle
  préfère celles présentes partout (Verdana, Arial, Tahoma) et prévient quand
  le choix de l'utilisateur n'est pas dans ce cas.
- **Vérifier visuellement.** Le XML valide ne garantit pas un rendu lisible.

## Fichiers de référence

- `references/questionnaire.json` — le texte exact des questions et leur branchement
- `references/troubles.md` — ce que chaque réponse du questionnaire implique
- `references/reglages.md` — chaque paramètre et sa justification
- `references/reformulation.md` — règles de fidélité au contenu
