# Changelog

Toutes les évolutions notables de dyspositif sont consignées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnage suit [SemVer](https://semver.org/lang/fr/). Pour cette skill :

- **MAJEUR** — le parcours en six étapes change, ou un profil existant n'est
  plus lisible ;
- **MINEUR** — une capacité s'ajoute (nouveau degré d'intervention, nouvelle
  commande, nouvelle branche du questionnaire) ;
- **CORRECTIF** — une correction sans changement d'interface.

Une règle particulière à ce projet : **toute modification qui touche à la
fidélité au document** (modifications suivies, valeurs numériques, conservation
des images et des tableaux) est signalée explicitement, même quand c'est un
correctif.

## [Non publié]

## [0.1.0] — 2026-08-11

Première version utilisable.

### Ajouté

- **Le parcours en six étapes** (`SKILL.md`), chacune avec sa condition de
  sortie : cerner les besoins, les appliquer, recevoir le document, modifier,
  aperçu d'une page, document complet.
- **Questionnaire ramifié** (`references/questionnaire.json`) : cinq questions
  pour tout le monde, puis seulement les branches correspondant aux difficultés
  déclarées. Entrée par la difficulté ressentie et non par le diagnostic,
  réponses à cocher uniquement, questions de forme qui montrent au lieu de
  décrire, arrêt possible à tout moment.
- **Profil persistant** dans `~/.dyspositif/profil.json` : le questionnaire ne
  se repose jamais, il est rappelé en une ligne.
- **Degrés d'intervention** : mise en forme (police, corps, interligne,
  longueur de ligne, fond, air proportionnel à la densité, filets de section,
  teinte des lettres miroir et des paires de chiffres), segmentation des
  phrases longues à leurs articulations, sortie des listes enfouies avec
  numérotation et groupement par trois, regroupement des chiffres par tranches
  de trois, découpage ou signalement des tableaux de plus de trois colonnes.
- **Commandes** `dys.py` : `profil`, `questions`, `analyser`, `listes`,
  `appliquer`, `commenter`, `apercu`, `verifier`.
- **Fichier de contrôle** écrit à côté de chaque document produit : ce qui a
  changé, ce que l'outil a ajouté, chaque nombre regroupé avec sa valeur
  d'origine.
- **Détection des PDF scannés** : signalée en langage simple plutôt que de
  produire un document vide.
- **26 tests** (`tests/test_dys.py`) sur un cours fabriqué contenant tout ce
  qui peut casser — image, tableau de six colonnes, formatage appliqué à la
  main, phrase de quarante mots, liste enfouie, nombres longs.

### Fidélité au document

- Toute modification du texte passe par les modifications suivies de Word
  (`<w:ins>` / `<w:del>` signés « dyspositif »), rejetables une par une.
- Le document est modifié en place, jamais reconstruit : images, tableaux,
  en-têtes, notes et numérotations ne peuvent pas être perdus.
- `dys.py verifier` échoue si du texte a changé sans modification suivie, si
  une image ou un tableau a disparu, ou si une valeur numérique du cours ne se
  retrouve pas à l'identique.

### Sécurité

- Archives traitées comme non fiables : chemins sortants refusés, liens
  symboliques supprimés, nombre d'entrées et taille décompressée plafonnés.
- XML parsé via `defusedxml` quand il est disponible, avec avertissement
  explicite sinon.
- Flux PDF décompressés sous plafond mémoire.
- Une vérification qui ne peut pas tourner est signalée comme telle
  (`verdict: incomplet`), jamais présentée comme réussie.

[Non publié]: https://github.com/ChloeHal/dyspositif/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ChloeHal/dyspositif/releases/tag/v0.1.0
