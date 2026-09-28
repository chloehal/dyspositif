"""Extrait de calibration par blocs entiers (indices zéro, bornes inclusives)."""
import copy
from pathlib import Path
from . import ooxml, paquet
from .ooxml import q


def inventaire(source):
    with paquet.DossierTemporaire() as d:
        paquet.ouvrir(source, d)
        doc = ooxml.Document(d / 'word/document.xml')
        blocs = [b for b in doc.corps if b.tag != q('w:sectPr')]
        return {'blocs': [{'index': i, 'type': 'tableau' if b.tag == q('w:tbl') else 'bloc',
                            'texte': ooxml.texte_paragraphe(b)[:180],
                            'images': len(list(b.iter(q('w:drawing')))),
                            'mots': len(ooxml.texte_paragraphe(b).split())} for i, b in enumerate(blocs)],
                'note': 'Choisir un bloc contenant la difficulté réelle ; indices zéro, fin incluse.'}


def extraire(source, sortie, debut, fin):
    if Path(source).resolve() == Path(sortie).resolve():
        raise ValueError("L'extrait doit avoir un autre nom que la source.")
    with paquet.DossierTemporaire() as d:
        paquet.ouvrir(source, d)
        doc = ooxml.Document(d / 'word/document.xml')
        blocs = [b for b in doc.corps if b.tag != q('w:sectPr')]
        if debut < 0 or fin < debut or fin >= len(blocs):
            raise ValueError('Bornes hors du document (indices zéro, fin incluse).')
        # La section du dernier bloc sélectionné peut terminer plus loin.
        section = None
        for bloc in list(doc.corps)[fin:]:
            candidate = bloc if bloc.tag == q('w:sectPr') else bloc.find('.//' + q('w:sectPr'))
            if candidate is not None:
                section = copy.deepcopy(candidate)
                break
        selection = blocs[debut:fin+1]
        for b in list(doc.corps):
            doc.corps.remove(b)
        for b in selection:
            doc.corps.append(b)
        if section is not None:
            doc.corps.append(section)
        doc.enregistrer()
        paquet.refermer(d, sortie)
    return {'sortie': str(sortie), 'debut': debut, 'fin': fin,
            'limite': 'Copie de calibration, pas document final. Ressources et relations conservées ; vérifier renvois et pagination.'}
