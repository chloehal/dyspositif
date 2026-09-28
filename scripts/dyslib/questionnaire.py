"""Questions par besoin ; le diagnostic n'est pas un branchement."""
from .profil import branches_a_poser


def preparer(catalogue, difficultes, acces='visuel', rythme=None):
    difficultes = sorted(set(d for d in difficultes if d))
    branches = branches_a_poser(difficultes)
    questions = list(catalogue['socle']) if not difficultes else []
    for branche in branches:
        questions += catalogue['branches'].get(branche, [])
    presentation = {
        'par_groupe': rythme or (1 if set(difficultes) & {'attention', 'fatigue', 'comprehension'} else 3),
        'progression': 'texte', 'champ_libre_facultatif': True,
        'colonnes': 1, 'acces': acces, 'comparaison_visuelle': acces == 'visuel',
    }
    if acces != 'visuel':
        questions = [q for q in questions if not q.get('visuel_seulement')]
    taille = presentation['par_groupe']
    groupes = [questions[i:i+taille] for i in range(0, len(questions), taille)]
    return {
        'total': len(questions),
        'annonce': "%s question(s) disponible(s). Tu peux t'arrêter quand tu veux ou garder l'original." % len(questions),
        'presentation': presentation, 'groupes': groupes, 'branches_ouvertes': branches,
        'progression': ['Étape %s sur %s' % (i+1, len(groupes)) for i in range(len(groupes))],
    }
