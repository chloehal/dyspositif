"""Fidélité matérielle indépendante du nombre d'objets dans l'archive."""
from collections import Counter
from . import ooxml, paquet
from .ooxml import q


def _mathematique(element):
    # Conserver opérateurs, fractions, indices et attributs, ignorer seulement
    # la typographie Word qui peut changer lors de la mise en forme autorisée.
    if element.tag == q('w:rPr'):
        return None
    return (element.tag, tuple(sorted(element.attrib.items())), element.text or '',
            tuple(x for x in (_mathematique(e) for e in element) if x is not None))


def _inventaire(source):
    with paquet.DossierTemporaire() as d:
        paquet.ouvrir(source, d)
        fichiers = {str(p.relative_to(d)): p.read_bytes() for p in d.rglob('*') if p.is_file()}
    relations = Counter()
    objets = Counter()
    for nom, contenu in fichiers.items():
        if nom.endswith('.rels'):
            for r in ooxml.lire(contenu):
                relations[(nom, r.get('Id'), r.get('Type'), r.get('Target'), r.get('TargetMode'))] += 1
        if nom.startswith('word/') and nom.endswith('.xml') and nom != 'word/styles.xml':
            racine = ooxml.lire(contenu)
            for tag in ('m:oMath', 'w:instrText', 'w:footnoteReference', 'w:endnoteReference', 'a:blip', 'w:hyperlink'):
                for e in racine.iter(q(tag)):
                    if tag == 'm:oMath':
                        contenu_objet = _mathematique(e)
                    elif tag == 'w:hyperlink':
                        contenu_objet = (e.get(q('r:id')), e.get(q('w:anchor')), ooxml.texte_paragraphe(e))
                    elif tag == 'a:blip':
                        contenu_objet = (e.get(q('r:embed')), e.get(q('r:link')))
                    elif tag.endswith('Reference'):
                        contenu_objet = e.get(q('w:id'))
                    else:
                        contenu_objet = ''.join(e.itertext())
                    objets[(nom, tag, str(contenu_objet))] += 1
    return fichiers, relations, objets


def _texte_restitue(fichiers):
    racine = ooxml.lire(fichiers['word/document.xml'])
    insertions = {id(e) for ins in racine.iter(q('w:ins')) for e in ins.iter()}
    textes = []
    for p in racine.iter(q('w:p')):
        texte = ''.join(e.text or '' for e in p.iter()
                        if e.tag in (q('w:t'), q('w:delText')) and id(e) not in insertions)
        if texte:
            textes.append(texte)
    return textes


def comparer(avant, apres):
    a, ra, oa = _inventaire(avant)
    b, rb, ob = _inventaire(apres)
    proteges = [n for n in a if n.startswith('word/media/') or
                (n.startswith('word/') and (n.split('/')[-1].startswith(('footnotes', 'endnotes', 'header', 'footer'))))]
    modifies = [n for n in proteges if a[n] != b.get(n)]
    relations = [str(x) for x in (ra - rb)]
    objets = [str(x) for x in (oa - ob)]
    restituable = _texte_restitue(a) == _texte_restitue(b)
    return {'passe': not (modifies or relations or objets) and restituable, 'texte_restituable': restituable, 'modifies_ou_perdus': modifies,
            'relations_perdues': relations, 'objets_perdus_ou_modifies': objets,
            'limite': 'Ne prouve pas le sens, les unités ni les relations entre cellules après réécriture ; comparer aussi manuellement.'}
