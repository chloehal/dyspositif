# Synthèses sur mesure — plan d'implémentation

Objectif : appliquer l'audit approuvé par « go fait tout » : adapter une synthèse existante, conserver son contenu et respecter les préférences individuelles.

Spécification : ../specs/2026-09-28-syntheses-sur-mesure.md.
Architecture : profil versionné (besoins, décisions, propositions, conflits) ; questionnaire indépendant des diagnostics ; édition OOXML conservatrice ; contrôles automatiques distincts des validations humaines. Python 3.9+, bibliothèque standard, dépendances de rendu existantes facultatives. Exécution dans cette session, revue indépendante finale.

- [x] Profil : reproduire refus écrasés, mises à jour partielles, migration et conflits. Ajouter décisions avec provenance, validation des paramètres, propositions et contraintes. Contextes nommés et essais temporaires sans écraser le profil enregistré.
- [x] Questionnaire : tester ordre invariant, rythme réellement respecté, inconnus et accès non visuel. Socle court, branches par besoins, choix ouverts facultatifs, diagnostics sans inférence automatique.
- [x] Document : tester périmètre, sélection représentative, refus, couleurs et restitution. Extrait par blocs, contraste des couleurs générées, préservation des couleurs existantes, contrôles des éléments et de l'accessibilité structurelle.
- [x] Skill et documentation : comparer scénarios avant/après ; réécrire parcours, périmètre, références, capacités et évaluations. Décrire les procédures de calibration, fidélité sémantique et essais avec les utilisateurs.
- [x] Vérification : suite complète sous Python 3.9 et 3.12, smoke CLI, contrôle externe et rendu, revue indépendante et corrections. Détails dans `docs/verification-2026-09-28.md`.
- Livraison : commit et branche proposée sur GitHub à la finalisation.

Risques à couvrir : diagnostic sans besoin ; refus après activation ; combinaison dans un ordre différent ; ancien profil incomplet ; teintes existantes sur fond sombre ; extrait comportant tableaux/images ; texte dans notes et équations ; conversion PDF non vérifiée ; outils externes absents.

Décision : aucune nouvelle boucle d'approbation du plan : l'utilisateur a autorisé la réalisation intégrale de l'audit. Les essais utilisateurs réels ne sont pas simulés ; leur protocole et les limites de vérification sont livrés.
