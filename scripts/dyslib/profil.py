"""Besoins déclarés, propositions et choix confirmés, sans diagnostic déduit."""
import copy
import json
import math
import os
import re
from datetime import datetime
from pathlib import Path

DEFAUTS = {
    'version': 2, 'difficultes': [], 'troubles_declares': [],
    'besoin_libre': '', 'priorites': [], 'reperes_a_preserver': [],
    'support': 'les_deux', 'acces': 'visuel', 'fond': 'blanc',
    'police': 'Arial', 'taille_pt': 13, 'interligne': 1.5,
    'espacement_lettres_pt': 0.0, 'longueur_ligne': 66,
    'couleur_texte': 'auto', 'alignement': 'conserver', 'couleurs_utilisateur': {},
    'sans_couleurs': False, 'texte_intact': True,
    'lettres_miroir': {'actif': False, 'teinte': 'C2410C'},
    'chiffres': {'grouper': False, 'paires': False, 'teinte': '0B6E4F'},
    'listes': {'numeroter': False, 'grouper_par': 0, 'compteur': False},
    'segmentation': {'actif': False, 'seuil_mots': 28},
    'air_proportionnel': False, 'filet_section': False, 'marge_annotation': False,
    'tableaux': {'max_colonnes': 3, 'action': 'conserver'},
    'reformulation': {'actif': False}, 'mnemotechniques': {'actif': False},
    'decisions': {}, 'propositions': {}, 'conflits': [], 'essais': [],
}
COURANTS = {k: DEFAUTS[k] for k in ('police', 'taille_pt', 'interligne', 'fond', 'longueur_ligne')}
BRANCHES = {
    'ligne': 'dechiffrage', 'lettres': 'dechiffrage', 'attention': 'attention',
    'chiffres': 'chiffres', 'reperage': 'reperage', 'fatigue': 'fatigue',
    'comprehension': 'comprehension', 'memoire': 'memoire',
    'vision': 'vision', 'surcharge': 'vision', 'navigation': 'navigation',
    'ecriture': 'navigation', 'autre': 'autre',
}
# Conservé comme symbole de compatibilité ; aucun diagnostic n'active de besoin.
TROUBLE_VERS_DIFFICULTES = {}
POLICES = {'a': 'Verdana', 'b': 'Arial', 'c': 'OpenDyslexic',
           'verdana': 'Verdana', 'arial': 'Arial', 'opendyslexic': 'OpenDyslexic',
           'tahoma': 'Tahoma', 'century_gothic': 'Century Gothic'}
FONDS = {'blanc': 'blanc', 'creme': 'creme', 'sombre': 'sombre',
         'a': 'blanc', 'b': 'creme', 'c': 'sombre'}
COULEURS_NOMMEES = {'bleu': '1D4ED8', 'vert': '047857', 'orange': 'C2410C',
                   'rouge': 'B91C1C', 'violet': '6D28D9', 'jaune': 'A16207',
                   'rose': 'BE185D', 'gris': '4B5563'}
PLAGES = {'taille_pt': (8, 72), 'interligne': (1, 3),
          'espacement_lettres_pt': (0, 4), 'longueur_ligne': (20, 120),
          'segmentation.seuil_mots': (6, 200), 'listes.grouper_par': (0, 20),
          'tableaux.max_colonnes': (2, 20)}
CHOIX = {'alignement': {'conserver', 'gauche'}, 'fond': set(FONDS) & {'blanc', 'creme', 'sombre'},
         'support': {'ecran', 'papier', 'les_deux'},
         'acces': {'visuel', 'lecteur_ecran', 'vocal', 'clavier'},
         'tableaux.action': {'conserver', 'signaler', 'decouper'}}


def emplacement(contexte=None):
    chemin = Path(os.environ.get('DYSPOSITIF_PROFIL', '~/.dyspositif/profil.json')).expanduser()
    if contexte:
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,40}', contexte):
            raise ValueError('Contexte : lettres, chiffres, tirets, 40 caractères maximum.')
        chemin = chemin.with_name(chemin.stem + '-' + contexte + chemin.suffix)
    return chemin


def _fusion(base, donnees):
    resultat = copy.deepcopy(base)
    for cle, valeur in donnees.items():
        if isinstance(valeur, dict) and isinstance(resultat.get(cle), dict):
            resultat[cle] = _fusion(resultat[cle], valeur)
        else:
            resultat[cle] = copy.deepcopy(valeur)
    return resultat


def valeur(profil, cle):
    cible = profil
    for morceau in cle.split('.'):
        cible = cible[morceau]
    return cible


def _poser(profil, cle, contenu):
    morceaux = cle.split('.')
    cible = profil
    for morceau in morceaux[:-1]:
        cible = cible[morceau]
    cible[morceaux[-1]] = contenu


def _parametres(d=None, prefixe=''):
    for cle, contenu in (DEFAUTS if d is None else d).items():
        if cle in {'version', 'difficultes', 'troubles_declares', 'besoin_libre', 'priorites',
                   'reperes_a_preserver', 'decisions', 'propositions', 'conflits', 'essais',
                   'couleurs_utilisateur', 'mnemotechniques'}:
            continue
        nom = prefixe + cle
        if isinstance(contenu, dict):
            yield from _parametres(contenu, nom + '.')
        else:
            yield nom, contenu


def _verifier_valeur(cle, contenu):
    parametres = dict(_parametres())
    if cle not in parametres:
        raise ValueError('Paramètre inconnu ou non modifiable : ' + cle)
    modele = parametres[cle]
    if isinstance(modele, bool):
        valide = isinstance(contenu, bool)
    elif cle in PLAGES:
        mini, maxi = PLAGES[cle]
        valide = (isinstance(contenu, (int, float)) and not isinstance(contenu, bool)
                  and math.isfinite(contenu) and mini <= contenu <= maxi)
        if isinstance(modele, int):
            valide = valide and int(contenu) == contenu
    elif cle in CHOIX:
        valide = isinstance(contenu, str) and contenu in CHOIX[cle]
    elif cle.endswith('teinte') or cle == 'couleur_texte':
        valide = isinstance(contenu, str) and bool(re.fullmatch(r'[0-9A-Fa-f]{6}', contenu) or (cle == 'couleur_texte' and contenu == 'auto'))
    else:
        valide = isinstance(contenu, str) and 0 < len(contenu) <= 100
    if not valide:
        raise ValueError('Valeur invalide pour ' + cle)


def normaliser(donnees):
    if not isinstance(donnees, dict):
        raise ValueError('Le profil doit être un objet JSON.')
    if donnees.get('version', 2) not in (1, 2):
        raise ValueError('Version de profil non prise en charge.')
    p = _fusion(DEFAUTS, donnees)
    for cle, modele in DEFAUTS.items():
        if isinstance(modele, dict) and not isinstance(p[cle], dict):
            raise ValueError(cle + ' doit être un objet.')
    for cle, _ in _parametres():
        _verifier_valeur(cle, valeur(p, cle))
    for cle in ('difficultes', 'troubles_declares', 'priorites', 'reperes_a_preserver'):
        if not isinstance(p[cle], list) or not all(isinstance(x, str) for x in p[cle]):
            raise ValueError(cle + ' doit être une liste de textes.')
    for cle in ('decisions', 'propositions', 'couleurs_utilisateur'):
        if not isinstance(p[cle], dict):
            raise ValueError(cle + ' doit être un objet.')
    for categorie in ('decisions', 'propositions'):
        for cle, entree in p[categorie].items():
            etats = {'propose'} if categorie == 'propositions' else {'valide', 'refuse', 'essai', 'conserve'}
            if (not isinstance(entree, dict) or not isinstance(entree.get('origine'), str)
                    or entree.get('etat') not in etats or 'valeur' not in entree):
                raise ValueError('Décision ou proposition invalide : ' + cle)
            if entree['etat'] == 'conserve':
                if cle not in ('fond', 'police') or entree['valeur'] != 'original':
                    raise ValueError('Conservation invalide : ' + cle)
            else:
                _verifier_valeur(cle, entree['valeur'])
                if categorie == 'decisions' and entree['valeur'] != valeur(p, cle):
                    raise ValueError('Décision incohérente avec le réglage : ' + cle)
    for couleur in p['couleurs_utilisateur'].values():
        if not isinstance(couleur, str) or not re.fullmatch(r'[0-9A-Fa-f]{6}', couleur):
            raise ValueError('Couleur utilisateur invalide.')
    if not isinstance(p['besoin_libre'], str) or not isinstance(p['essais'], list):
        raise ValueError('Besoin libre ou essais invalides.')
    # Les anciens réglages sont conservés comme propositions à reconfirmer,
    # pas convertis en préférences validées à partir de leur seule présence.
    if donnees.get('version') == 1:
        for cle, defaut in _parametres():
            ancien = valeur(p, cle)
            if ancien != defaut:
                p['propositions'][cle] = {'valeur': ancien, 'origine': 'migration_v1', 'etat': 'propose'}
                _poser(p, cle, copy.deepcopy(defaut))
        p['migration_a_confirmer'] = True
        p['decisions'] = {}
    p['version'] = 2
    p['mnemotechniques'] = {'actif': False}
    return p


def charger(contexte=None):
    chemin = emplacement(contexte)
    return normaliser(json.loads(chemin.read_text(encoding='utf-8'))) if chemin.is_file() else None


def enregistrer(profil, contexte=None):
    p = normaliser(profil)
    chemin = emplacement(contexte)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    p.setdefault('cree_le', datetime.now().strftime('%Y-%m-%d'))
    p['maj_le'] = datetime.now().strftime('%Y-%m-%d')
    chemin.write_text(json.dumps(p, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    return chemin


def oublier(contexte=None):
    chemin = emplacement(contexte)
    if chemin.is_file():
        chemin.unlink()
        return True
    return False


def resume(profil):
    if not profil:
        return 'Aucun profil enregistré.'
    regles = []
    for cle in ('police', 'taille_pt', 'interligne', 'fond'):
        decision = profil.get('decisions', {}).get(cle)
        if decision:
            regles.append('%s : %s (%s)' % (cle, decision['valeur'], decision['etat']))
    return '%s — %s proposition(s) à essayer' % (', '.join(regles) or 'Présentation d’origine conservée', len(profil.get('propositions', {})))


def branches_a_poser(difficultes):
    return sorted({BRANCHES.get(d, 'autre') for d in difficultes if d not in ('aucune', 'diagnostic', 'inconnu')}
                  | ({'autre'} if 'inconnu' in difficultes else set()))


def _decider(p, cle, contenu, origine, etat='valide'):
    _verifier_valeur(cle, contenu)
    _poser(p, cle, contenu)
    p['decisions'][cle] = {'valeur': contenu, 'origine': origine, 'etat': etat}
    p['propositions'].pop(cle, None)


def _proposer(p, cle, contenu, origine):
    if cle not in p['decisions']:
        p['propositions'][cle] = {'valeur': contenu, 'origine': origine, 'etat': 'propose'}


def depuis_reponses(reponses, base=None):
    if not isinstance(reponses, dict):
        raise ValueError('Les réponses doivent être un objet JSON.')
    p = normaliser(base or {})
    for question, cle in [('q1_gene', 'difficultes'), ('q1_troubles', 'troubles_declares'),
                          ('besoin_libre', 'besoin_libre'), ('priorites', 'priorites'),
                          ('reperes_a_preserver', 'reperes_a_preserver')]:
        if question in reponses:
            p[cle] = copy.deepcopy(reponses[question])
    # Les questions d'expérience proposent ; les comparaisons et refus décident.
    mappings = {
        'q2_support': ('support', {x: x for x in CHOIX['support']}),
        'q_acces': ('acces', {x: x for x in CHOIX['acces']}),
        'q3_fond': ('fond', FONDS), 'q4_police': ('police', POLICES),
        'q_sans_couleurs': ('sans_couleurs', {'oui': True, 'non': False}),
        'c1_groupes': ('chiffres.grouper', {'colle': False, 'espace': True}),
        'c3_teintes': ('chiffres.paires', {'oui': True, 'non': False}),
        'a2_listes': ('listes.grouper_par', {'affilee': 0, 'groupes': 3}),
        'q_compteur': ('listes.compteur', {'oui': True, 'non': False}),
        'q_tableaux': ('tableaux.action', {x: x for x in CHOIX['tableaux.action']}),
    }
    for question, (cle, choix) in mappings.items():
        rep = reponses.get(question)
        if rep == 'original':
            if cle in ('fond', 'police'):
                p['decisions'][cle] = {'valeur': 'original', 'origine': question, 'etat': 'conserve'}
                p['propositions'].pop(cle, None)
            else:
                contenu = True if cle == 'sans_couleurs' else valeur(DEFAUTS, cle)
                _decider(p, cle, contenu, question, 'refuse')
            continue
        if rep in ('inconnu', 'aucune', None):
            continue
        if not isinstance(rep, str) or rep not in choix:
            raise ValueError('Réponse invalide pour ' + question)
        _decider(p, cle, choix[rep], question)
    if 'q5_couleurs' in reponses:
        if reponses['q5_couleurs'] == 'systeme':
            p['couleurs_utilisateur'] = {k: COULEURS_NOMMEES.get(v, v.lstrip('#').upper())
                                         for k, v in reponses.get('q5_grille', {}).items()}
        elif reponses['q5_couleurs'] in ('non', 'original'):
            _decider(p, 'sans_couleurs', True, 'q5_couleurs')
    rep = reponses.get('d3_segmenter_ou_reecrire')
    if rep in ('segmentee', 'reecrite', 'original'):
        _decider(p, 'segmentation.actif', rep != 'original', 'd3_segmenter_ou_reecrire')
        _decider(p, 'reformulation.actif', rep == 'reecrite', 'd3_segmenter_ou_reecrire')
        _decider(p, 'texte_intact', rep != 'reecrite', 'd3_segmenter_ou_reecrire')
    for question, cle in [('d2_lettres_miroir', 'lettres_miroir.actif'),
                          ('a1_ecrire_dessus', 'marge_annotation')]:
        rep = reponses.get(question)
        if rep in ('non', 'jamais'):
            _decider(p, cle, False, question, 'refuse')
        elif rep in ('oui', 'parfois', 'un_peu'):
            _proposer(p, cle, True, question)
    if reponses.get('d1_relire') in ('souvent', 'parfois'):
        souvent = reponses['d1_relire'] == 'souvent'
        for cle, contenu in [('interligne', 1.8 if souvent else 1.6),
                             ('longueur_ligne', 58 if souvent else 64)]:
            _proposer(p, cle, contenu, 'd1_relire')
    if reponses.get('c2_tableau') in ('doigt', 'abandonne'):
        _proposer(p, 'tableaux.action', 'decouper' if reponses['c2_tableau'] == 'abandonne' else 'signaler', 'c2_tableau')
    if reponses.get('a3_reprise') in ('cherche', 'recommence') or reponses.get('r1_ou_regarder') in ('pas_vraiment', 'perdu'):
        _proposer(p, 'filet_section', True, 'reperage')
    p['interrompu'] = bool(reponses.get('interrompu', p.get('interrompu', False)))
    return normaliser(p)


def valider_propositions(profil, cles):
    p = normaliser(profil)
    for cle in cles:
        if cle not in p['propositions']:
            raise ValueError('Proposition absente : ' + cle)
        proposition = p['propositions'][cle]
        _decider(p, cle, proposition['valeur'], 'essai:' + proposition['origine'])
    p['essais'].append({'parametres': list(cles), 'date': datetime.now().isoformat(timespec='seconds')})
    return p


def appliquer_definitions(profil, definitions, essai=False):
    p = normaliser(profil)
    for definition in definitions:
        cle, separateur, brut = definition.partition('=')
        if not separateur:
            raise ValueError('Attendu : parametre=valeur')
        contenu = brut if cle.endswith('teinte') or cle in ('couleur_texte', 'police') else _convertir(brut)
        _decider(p, cle, contenu, 'essai_provisoire' if essai else 'choix_explicite', 'essai' if essai else ('refuse' if contenu is False else 'valide'))
    return p


def pour_application(profil):
    p = normaliser(profil)
    p['conflits'] = []
    if p['sans_couleurs']:
        for cle in ('lettres_miroir.actif', 'chiffres.paires', 'filet_section'):
            if valeur(p, cle):
                p['conflits'].append({'parametre': cle, 'raison': 'sans_couleurs prioritaire', 'action': 'desactive'})
                _poser(p, cle, False)
    if p['texte_intact'] and p['reformulation']['actif']:
        p['reformulation']['actif'] = False
        p['conflits'].append({'parametre': 'reformulation.actif', 'raison': 'texte_intact prioritaire', 'action': 'desactive'})
    if p['support'] == 'papier' and p['fond'] == 'sombre':
        p['conflits'].append({'parametre': 'fond', 'raison': 'fond sombre à tester sur impression ; préférence conservée', 'action': 'a_verifier'})
    if p['tableaux']['action'] == 'decouper':
        p['conflits'].append({'parametre': 'tableaux.action', 'raison': 'vérifier les comparaisons entre colonnes sur extrait', 'action': 'a_verifier'})
    return p


def _convertir(valeur):
    bas = valeur.strip().lower()
    if bas in ('true', 'oui', 'vrai'):
        return True
    if bas in ('false', 'non', 'faux'):
        return False
    try:
        return float(valeur) if any(x in bas for x in ('.', 'nan', 'inf')) else int(valeur)
    except ValueError:
        return valeur
