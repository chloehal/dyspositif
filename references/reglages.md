# Chaque paramètre et sa justification

À charger à l'étape 2, quand il faut traduire les réponses en réglages, ou à
l'étape 4 en cas de doute sur un mécanisme. Tout ce qui est décrit ici est
appliqué par `scripts/dyslib/forme.py` — sauf mention contraire, aucun de ces
réglages ne touche à un mot du cours.

## Ce qui est établi, et ce qui ne l'est pas

| Ce qui aide, mesuré | Ce qui se dit sans preuve solide |
|---|---|
| Raccourcir la ligne (55–65 caractères) | OpenDyslexic améliorerait la lecture |
| Augmenter l'espacement entre lettres et entre mots | Une couleur de fond précise « soignerait » la dyslexie |
| Augmenter l'interligne | Le bleu serait « la » bonne couleur |
| Éviter le texte justifié | Une police unique conviendrait à tout le monde |
| Écarter le blanc pur | |

**Sur OpenDyslexic.** On la propose parce que des personnes la préfèrent, et
c'est une raison suffisante. Les études disponibles ne montrent pas de gain
mesurable par rapport à Arial ou Verdana. Ne jamais la présenter comme un
traitement, ne jamais l'imposer, ne jamais la refuser non plus.

## Police et corps

| Paramètre | Valeurs | Où c'est écrit |
|---|---|---|
| `police` | Verdana (défaut), Arial, Tahoma, Century Gothic, OpenDyslexic | `styles.xml` : `docDefaults/rPrDefault/rPr/w:rFonts` + chaque style + tout `rPr` direct |
| `taille_pt` | 12–16, défaut 13 ; 14 minimum si fatigue déclarée | `w:sz` et `w:szCs`, en demi-points |

Les tailles des styles existants ne sont pas écrasées mais **mises à l'échelle**
par le rapport entre la nouvelle taille de base et l'ancienne : un titre reste
plus gros que le corps. La hiérarchie du document est une information, on ne
l'aplatit pas.

**Police non installée.** Word substitue en silence et tout le bénéfice
disparaît chez l'utilisateur. Cette skill n'incorpore pas les polices dans le
fichier : elle préfère des polices présentes partout (Verdana, Arial, Tahoma).
Si quelqu'un choisit OpenDyslexic, le lui dire en une phrase :

> OpenDyslexic n'est pas installée par défaut. Si tu ne l'installes pas, Word
> remplacera la police sans prévenir. Je peux la mettre quand même, ou partir
> sur Verdana qui est déjà là.

## Espacement

| Paramètre | Valeurs | Où c'est écrit |
|---|---|---|
| `espacement_lettres_pt` | 0.4 à 0.8 pt, 0.6 si confusion de lettres | `w:spacing` dans `rPr` (vingtièmes de point) |
| `interligne` | 1.4 à 2.0, défaut 1.5 ; 1.8 si perte de ligne fréquente | `w:spacing w:line` (240 = simple), `lineRule="auto"` |
| `longueur_ligne` | 55 à 70 caractères, 58 si perte de ligne fréquente | marges de section, calculées depuis le corps |

Le calcul de la longueur de ligne : largeur de texte ≈ `longueur_ligne × 0.52 ×
taille_pt × 20` twips, le reste part en marges. Une ligne courte est le réglage
le mieux établi contre la perte de ligne, et le seul qui coûte de la place.

**Air proportionnel à la densité.** L'espacement avant et après chaque
paragraphe suit son indice de lisibilité, bloc par bloc : les passages
difficiles respirent, les faciles restent compacts. Sans cela, un document
adapté double de longueur sans rien gagner, et il devient impossible à
imprimer.

**Jamais de texte justifié.** `w:jc w:val="both"` est ramené à `left`, dans les
styles comme dans le formatage direct. Le justifié fabrique des rivières
blanches verticales qui attirent l'œil hors de la ligne.

## Fond et couleurs

| `fond` | Page | Texte | Pour qui |
|---|---|---|---|
| `blanc` | `FFFFFF` | `1A1A1A` | Impression, ou préférence explicite |
| `creme` | `FBF6EC` | `24211C` | Défaut : le blanc pur fatigue |
| `sombre` | `22262B` | `E7E3DC` | Écran, sensibilité à la luminosité |

Écrit dans `w:background` + `w:displayBackgroundShape` dans `settings.xml` —
sans ce second réglage, Word ignore purement et simplement la couleur de fond.
Un profil « papier » force le blanc : un fond sombre à l'impression est
illisible et vide une cartouche.

**Les couleurs de l'utilisateur d'abord.** Si la personne a déjà un système
(bleu = définitions, vert = à retenir), il est repris tel quel et **aucune
couleur de l'outil ne vient s'y superposer** : `couleur_libre()` choisit une
teinte non prise pour les lettres miroir ou les chiffres. C'est le point où la
skill encode le système de l'utilisateur au lieu d'imposer le sien.

## Mécanismes de repérage

**Lettres miroir teintées.** b, d, p, q reçoivent une nuance légère (défaut
`C2410C`), pas une police différente : le mot garde sa silhouette, seul le
caractère qui trompe attire l'œil. Techniquement, le run est découpé en
plusieurs runs et seuls les caractères visés reçoivent un `w:color` — aucun
texte n'est modifié, donc aucune modification suivie n'est nécessaire.

**Chiffres.** Deux mécanismes distincts :

- *Distinction visuelle* des paires confondues (3/8, 1/7) : même mécanisme de
  teinte, aucune modification de texte.
- *Regroupement par trois* (`1247893` → `1 247 893`) : c'est du texte, donc
  **modification suivie obligatoire**, avec une espace fine insécable (U+202F)
  qui ne casse pas le nombre en fin de ligne. La valeur ne change jamais ;
  `dys.py verifier` le contrôle nombre par nombre.

**Filet de section en marge.** Un trait vertical coloré sur les titres de
niveau 1 et 2, couleur changeant à chaque grande partie : savoir où l'on est
sans relire le titre. `w:pBdr/w:left`.

**Colonne d'annotation.** Si la personne écrit sur ses cours, la marge de
droite est élargie et les marges deviennent asymétriques. Une marge où l'on
peut écrire vaut mieux qu'une page pleine.

**Un seul fil de lecture.** Jamais deux éléments à suivre en parallèle. Les
tableaux de plus de trois colonnes sont soit signalés en commentaire, soit
découpés en tableaux de trois colonnes avec la première colonne répétée
(`tableaux.action`). Le découpage n'est tenté que sur les tableaux réguliers :
avec des cellules fusionnées, on signale, on ne déforme pas.

## Structure

**Listes enfouies.** Sorties uniquement quand la phrase annonce l'énumération
(« les conditions sont… », « on distingue… », deux points). Deux virgules et un
« et » ne suffisent pas : une fausse liste désoriente plus qu'un paragraphe
dense. Chaque élément est numéroté et le total est visible (« 3 sur 7 »), parce
que savoir combien il y en a, c'est pouvoir vérifier qu'on n'en oublie aucun.

**Groupement par trois.** Neuf éléments d'affilée saturent la mémoire de
travail. Trois groupes de trois, sans toucher aux éléments ni à leur ordre.

## Pièges

- **Ne jamais reformater le XML.** Word interprète les espaces entre balises
  comme du contenu. Pas d'indentation, pas de jolie mise en page du fichier.
- **Les déclarations de namespaces de la racine se conservent.** Un
  `mc:Ignorable="w14 wpc"` qui cite un préfixe non déclaré casse le document ;
  `ooxml.Document` réinjecte la balise racine d'origine à l'enregistrement.
- **L'ordre des enfants est imposé par le schéma.** `w:jc` après `w:spacing`
  dans un `pPr`, `w:ins` en premier dans un `rPr`, `displayBackgroundShape` à
  sa place exacte dans `settings.xml`. `poser_enfant()` s'en charge — s'en
  passer produit un fichier que Word refuse d'ouvrir.
- **Le formatage direct l'emporte sur les styles.** Un cours récupéré en est
  truffé : sans neutralisation, la moitié du document ignore le profil.
- **Le XML valide ne garantit pas un rendu lisible.** Regarder l'aperçu
  (`dys.py apercu`) avant de le montrer.
