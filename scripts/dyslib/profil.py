"""Le profil : ce que l'utilisateur a répondu, traduit en paramètres.

Le profil est enregistré sur disque et rechargé tel quel à chaque document.
Personne n'accepte de remplir un formulaire à chaque cours.
"""

import json
import os
from datetime import datetime
from pathlib import Path


def emplacement():
    depuis_env = os.environ.get("DYSPOSITIF_PROFIL")
    if depuis_env:
        return Path(depuis_env).expanduser()
    return Path("~/.dyspositif/profil.json").expanduser()


# -- valeurs par défaut ----------------------------------------------------
#
# Point de départ quand la personne ne sait pas quoi demander, jamais une
# prescription : toute préférence exprimée écrase la valeur d'ici.

DEFAUTS = {
    "version": 1,
    "difficultes": [],
    "troubles_declares": [],
    "support": "les_deux",
    "fond": "creme",
    "police": "Verdana",
    "taille_pt": 13,
    "interligne": 1.5,
    "espacement_lettres_pt": 0.4,
    "espacement_mots": "normal",
    "longueur_ligne": 66,
    "couleur_texte": "1A1A1A",
    "couleurs_utilisateur": {},
    "lettres_miroir": {"actif": False, "teinte": "C2410C"},
    "chiffres": {"grouper": False, "paires": False, "teinte": "0B6E4F"},
    "listes": {"numeroter": True, "grouper_par": 0, "compteur": False},
    "segmentation": {"actif": True, "seuil_mots": 28},
    "air_proportionnel": True,
    "filet_section": False,
    "marge_annotation": False,
    "tableaux": {"max_colonnes": 3, "action": "signaler"},
    "reformulation": {"actif": False},
    "mnemotechniques": {"actif": False},
}

# Réglages courants, employés quand quelqu'un s'arrête en cours de
# questionnaire. On le lui dit, on ne le lui reproche pas.
COURANTS = {
    "police": "Verdana",
    "taille_pt": 14,
    "interligne": 1.5,
    "fond": "creme",
    "longueur_ligne": 64,
}


def charger():
    chemin = emplacement()
    if not chemin.is_file():
        return None
    with open(chemin, encoding="utf-8") as f:
        donnees = json.load(f)
    profil = dict(DEFAUTS)
    profil.update(donnees)
    return profil


def enregistrer(profil):
    chemin = emplacement()
    chemin.parent.mkdir(parents=True, exist_ok=True)
    complet = dict(DEFAUTS)
    complet.update(profil)
    complet.setdefault("cree_le", datetime.now().strftime("%Y-%m-%d"))
    complet["maj_le"] = datetime.now().strftime("%Y-%m-%d")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(complet, f, ensure_ascii=False, indent=2, sort_keys=True)
    return chemin


def oublier():
    chemin = emplacement()
    if chemin.is_file():
        chemin.unlink()
        return True
    return False


def resume(profil):
    """Le rappel en une ligne de l'étape 1. Pas deux lignes."""
    if not profil:
        return "Aucun profil enregistré."
    morceaux = []
    if profil.get("troubles_declares"):
        morceaux.append(" + ".join(profil["troubles_declares"]))
    elif profil.get("difficultes"):
        morceaux.append(" + ".join(profil["difficultes"]))
    morceaux.append("%s %s" % (profil.get("police"), profil.get("taille_pt")))
    morceaux.append("interligne %s" % profil.get("interligne"))
    morceaux.append("fond %s" % profil.get("fond"))
    if profil.get("lettres_miroir", {}).get("actif"):
        morceaux.append("b/d teintés")
    if profil.get("chiffres", {}).get("grouper"):
        morceaux.append("chiffres groupés")
    if profil.get("mnemotechniques", {}).get("actif"):
        morceaux.append("mnémo en commentaires")
    return ", ".join(morceaux)


# -- des réponses aux paramètres ------------------------------------------
#
# Format d'entrée attendu : voir references/troubles.md. Chaque clé est une
# question, chaque valeur une réponse à cocher (ou une liste, pour q1).

BRANCHES = {
    "ligne": "dechiffrage",
    "lettres": "dechiffrage",
    "attention": "attention",
    "chiffres": "chiffres",
    "reperage": "reperage",
    "fatigue": None,
}

TROUBLE_VERS_DIFFICULTES = {
    "dyslexie": ["ligne", "lettres"],
    "dysorthographie": ["lettres"],
    "dyscalculie": ["chiffres"],
    "dyspraxie": ["reperage"],
    "tdah": ["attention"],
    "dysphasie": ["ligne"],
    "trouble_visuel": ["reperage", "fatigue"],
}

POLICES = {
    "a": "Verdana",
    "b": "Arial",
    "c": "OpenDyslexic",
    "verdana": "Verdana",
    "arial": "Arial",
    "opendyslexic": "OpenDyslexic",
    "tahoma": "Tahoma",
    "century_gothic": "Century Gothic",
}

FONDS = {"blanc": "blanc", "creme": "creme", "sombre": "sombre",
         "a": "blanc", "b": "creme", "c": "sombre"}

COULEURS_NOMMEES = {
    "bleu": "1D4ED8", "vert": "047857", "orange": "C2410C",
    "rouge": "B91C1C", "violet": "6D28D9", "jaune": "A16207",
    "rose": "BE185D", "gris": "4B5563",
}


def branches_a_poser(difficultes):
    """Seules les branches correspondant aux difficultés déclarées."""
    sortie = []
    for difficulte in difficultes:
        branche = BRANCHES.get(difficulte)
        if branche and branche not in sortie:
            sortie.append(branche)
    return sortie


def depuis_reponses(reponses, base=None):
    """Traduit les réponses du questionnaire en paramètres concrets."""
    profil = dict(base or DEFAUTS)
    profil = json.loads(json.dumps(profil))  # copie profonde

    difficultes = list(reponses.get("q1_gene", []))
    troubles = list(reponses.get("q1_troubles", []))
    for trouble in troubles:
        for difficulte in TROUBLE_VERS_DIFFICULTES.get(trouble, []):
            if difficulte not in difficultes:
                difficultes.append(difficulte)
    profil["difficultes"] = difficultes
    profil["troubles_declares"] = troubles

    if "q2_support" in reponses:
        profil["support"] = reponses["q2_support"]
        if profil["support"] == "papier":
            profil["fond"] = "blanc"  # une page imprimée en fond sombre est illisible

    if "q3_fond" in reponses:
        profil["fond"] = FONDS.get(reponses["q3_fond"], profil["fond"])
    if profil.get("support") == "papier" and profil["fond"] == "sombre":
        profil["fond"] = "creme"

    if "q4_police" in reponses:
        profil["police"] = POLICES.get(reponses["q4_police"], reponses["q4_police"])

    if "q5_couleurs" in reponses:
        if reponses["q5_couleurs"] == "systeme":
            profil["couleurs_utilisateur"] = {
                categorie: COULEURS_NOMMEES.get(couleur, couleur.lstrip("#").upper())
                for categorie, couleur in (reponses.get("q5_grille") or {}).items()
            }

    # Branche déchiffrage
    if reponses.get("d1_relire") in ("souvent", "parfois"):
        profil["interligne"] = 1.8 if reponses["d1_relire"] == "souvent" else 1.6
        profil["longueur_ligne"] = 58 if reponses["d1_relire"] == "souvent" else 64
        profil["espacement_lettres_pt"] = 0.6
    if reponses.get("d2_lettres_miroir") in ("oui", "parfois"):
        profil["lettres_miroir"] = {
            "actif": True,
            "teinte": COULEURS_NOMMEES.get(
                reponses.get("d2_teinte", "orange"), "C2410C"
            ),
        }
    if "d3_segmenter_ou_reecrire" in reponses:
        choix = reponses["d3_segmenter_ou_reecrire"]
        profil["segmentation"]["actif"] = True
        profil["reformulation"]["actif"] = choix == "reecrite"
    if reponses.get("d4_mot_complique") == "bloque":
        profil["reformulation"]["actif"] = True

    # Branche attention
    if reponses.get("a1_ecrire_dessus") in ("oui", "un_peu"):
        profil["marge_annotation"] = True
    if reponses.get("a2_listes") == "groupes":
        profil["listes"]["grouper_par"] = 3
        profil["listes"]["compteur"] = True
    if reponses.get("a3_reprise") in ("cherche", "recommence"):
        profil["filet_section"] = True
        profil["listes"]["compteur"] = True

    # Branche chiffres
    if reponses.get("c1_groupes") == "espace":
        profil["chiffres"]["grouper"] = True
    if reponses.get("c2_tableau") in ("doigt", "abandonne"):
        profil["chiffres"]["paires"] = True
        profil["tableaux"]["action"] = (
            "decouper" if reponses["c2_tableau"] == "abandonne" else "signaler"
        )
    if "chiffres" in difficultes:
        profil["chiffres"]["grouper"] = True
        profil["chiffres"]["paires"] = True

    # Branche repérage
    if reponses.get("r1_ou_regarder") in ("pas_vraiment", "perdu"):
        profil["filet_section"] = True
        profil["air_proportionnel"] = True

    # Pour tout le monde, en dernier
    if reponses.get("z1_mnemo") == "oui":
        profil["mnemotechniques"]["actif"] = True
    elif reponses.get("z1_mnemo") == "aimerais":
        profil["mnemotechniques"]["actif"] = True
    elif reponses.get("z1_mnemo") == "embrouille":
        profil["mnemotechniques"]["actif"] = False

    if "fatigue" in difficultes and profil["taille_pt"] < 14:
        profil["taille_pt"] = 14
    if "lettres" in difficultes:
        profil["espacement_lettres_pt"] = max(profil["espacement_lettres_pt"], 0.6)

    profil["interrompu"] = bool(reponses.get("interrompu"))
    if profil["interrompu"]:
        for cle, valeur in COURANTS.items():
            if cle not in reponses_touchees(reponses):
                profil[cle] = valeur
    return profil


def reponses_touchees(reponses):
    """Paramètres réellement décidés par l'utilisateur — à ne pas écraser."""
    touches = set()
    if "q3_fond" in reponses:
        touches.add("fond")
    if "q4_police" in reponses:
        touches.add("police")
    if "d1_relire" in reponses:
        touches.update({"interligne", "longueur_ligne"})
    return touches


def appliquer_definitions(profil, definitions):
    """`--definir police=Arial taille_pt=16 chiffres.grouper=true`"""
    for definition in definitions:
        cle, _, valeur = definition.partition("=")
        cible = profil
        morceaux = cle.split(".")
        for morceau in morceaux[:-1]:
            cible = cible.setdefault(morceau, {})
        cible[morceaux[-1]] = _convertir(valeur)
    return profil


def _convertir(valeur):
    bas = valeur.strip().lower()
    if bas in ("true", "oui", "vrai"):
        return True
    if bas in ("false", "non", "faux"):
        return False
    try:
        if "." in valeur:
            return float(valeur)
        return int(valeur)
    except ValueError:
        return valeur
