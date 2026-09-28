# Sécurité

## Ce que cet outil manipule

Des synthèses existantes. C'est-à-dire des fichiers venant de tiers — un prof, un camarade,
une plateforme de cours — ouverts sur la machine de quelqu'un d'autre. Un
`.docx` est une archive zip contenant du XML : les deux formats ont une longue
histoire d'abus.

**Le principe appliqué partout : le document d'entrée n'est pas de confiance.**

## Ce qui est déjà en place

| Risque | Protection | Où |
|---|---|---|
| Chemin sortant de l'archive (`../../.ssh/authorized_keys`) | Chaque entrée est résolue et refusée si elle sort du dossier de travail | `dyslib/paquet.py` |
| Lien symbolique dans l'archive | Les entrées de type lien sont ignorées, puis les liens trouvés sont supprimés | `dyslib/paquet.py` |
| Bombe de décompression (zip bomb) | Plafond de 5 000 entrées et de 800 Mo décompressés | `dyslib/paquet.py` |
| Bombe d'entités XML, entités externes (XXE) | Parsing via `defusedxml` quand il est présent, avertissement explicite sinon | `dyslib/ooxml.py` |
| Flux PDF gonflé | Décompression plafonnée à 32 Mo par flux | `dyslib/analyse.py` |
| Injection de commande | Aucun appel shell : les sous-processus reçoivent une liste d'arguments, jamais une chaîne | partout |
| Vérification silencieusement absente | Une vérification qui ne peut pas tourner renvoie `verdict: incomplet`, jamais `passe` | `dys.py verifier` |

## Ce qui sort de la machine

**Le moteur Python ne fait aucun appel réseau et n’envoie aucun document.**
L’agent qui utilise la skill peut traiter le contenu via son fournisseur : ses
conditions de confidentialité s’appliquent séparément. Ne pas promettre que
l’ensemble du parcours de l’agent reste local. Les
seuls fichiers écrits sont : le document produit, son fichier de contrôle, et
les extraits de calibration, les copies de structure et le profil dans `~/.dyspositif/profil.json` (ou le chemin de
`DYSPOSITIF_PROFIL`). Les contextes nommés ajoutent un suffixe au fichier ;
les supprimer avec `profil --contexte NOM --oublier`. Ne pas publier ces profils.

Le profil contient des informations sur les difficultés de lecture de la
personne. Ces informations peuvent être sensibles. Le fichier du moteur reste local et
se supprime avec `python scripts/dys.py profil --oublier`.

## Limites connues

- Les documents produits **conservent les métadonnées d'origine** (auteur,
  organisation). Si tu partages une synthèse adaptée, ce sont celles du prof.
- Le nom d'auteur des modifications suivies est « dyspositif » par défaut, mais
  `--auteur` accepte n'importe quoi. Rien n'est vérifié.
- L'outil ne chiffre rien : les documents temporaires passent par le dossier
  temporaire du système, supprimé en fin d'exécution.

## Signaler une faille

**N'ouvre pas d'issue publique.** Utilise l'onglet *Security* du dépôt →
*Report a vulnerability* (advisory privé), ou un message privé sur
[LinkedIn](https://www.linkedin.com/in/chloé-halloin/).

Réponse sous une semaine. Si la faille est confirmée, le correctif est publié
avec mention de la personne qui l'a signalée — sauf demande contraire.

## Versions suivies

La dernière version publiée. Le projet est jeune : il n'y a pas encore de
branche de maintenance.
