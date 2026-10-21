
# -*- coding: utf-8 -*-

"""
Construction reproductible de la base SQLite NutriHFr.

Les fichiers CSV originaux sont conservés sans modification.
La base est créée dans un nouveau fichier pour protéger
la base utilisée par le tableau de bord Streamlit.
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


RACINE_PROJET = Path(__file__).resolve().parent.parent
DOSSIER_SOURCE = RACINE_PROJET / "data" / "raw" / "inca3"
DOSSIER_DESTINATION = RACINE_PROJET / "data" / "processed"

FICHIERS = {
    "individus": "description-indiv.csv",
    "apports": "apports-nut-alim.csv",
    "consommations": "conso-compo-alim-vf-mad-datagouv2021.csv",
}

CLES_PRIMAIRES = {
    "individus": "NOIND",
    "apports": "NOIND",
    "consommations": "NUM_LIGNE",
}


def citer_identifiant(nom):
    """Protège un identifiant SQL."""
    return '"' + nom.replace('"', '""') + '"'


def verifier_fichiers():
    """Vérifie la présence des fichiers CSV nécessaires."""

    for nom_table, nom_fichier in FICHIERS.items():
        chemin = DOSSIER_SOURCE / nom_fichier

        if not chemin.is_file():
            raise FileNotFoundError(
                f"Fichier manquant pour {nom_table} : {chemin}"
            )


def importer_csv(connexion, nom_table, nom_fichier):
    """
    Importe un CSV par blocs pour limiter la mémoire utilisée.
    """

    chemin = DOSSIER_SOURCE / nom_fichier
    nom_temporaire = f"temp_{nom_table}"
    total = 0

    print(f"\nImportation de {nom_table}...")

    lecteur = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False,
        chunksize=10000,
    )

    for bloc in lecteur:
        bloc.to_sql(
            nom_temporaire,
            connexion,
            if_exists="append",
            index=False,
        )

        total += len(bloc)

    print(f"  {total:,} lignes importées.")

    return nom_temporaire


def creer_table_finale(connexion, nom_table, nom_temporaire):
    """
    Reproduit les colonnes importées en ajoutant les contraintes
    de clé primaire et de clé étrangère.
    """

    informations = connexion.execute(
        f"PRAGMA table_info({citer_identifiant(nom_temporaire)})"
    ).fetchall()

    colonnes = [ligne[1] for ligne in informations]
    cle_primaire = CLES_PRIMAIRES[nom_table]

    if cle_primaire not in colonnes:
        raise ValueError(
            f"Clé primaire absente dans {nom_table} : {cle_primaire}"
        )

    definitions = []

    for information in informations:
        nom_colonne = information[1]
        type_sql = information[2] or "TEXT"

        definition = f"{citer_identifiant(nom_colonne)} {type_sql}"

        if nom_colonne == cle_primaire:
            definition += " PRIMARY KEY"

        definitions.append(definition)

    if nom_table in ("apports", "consommations"):
        definitions.append(
            'FOREIGN KEY ("NOIND") REFERENCES individus("NOIND")'
        )

    sql_creation = (
        f"CREATE TABLE {citer_identifiant(nom_table)} "
        f"({', '.join(definitions)})"
    )

    connexion.execute(sql_creation)

    colonnes_sql = ", ".join(
        citer_identifiant(colonne) for colonne in colonnes
    )

    connexion.execute(
        f"INSERT INTO {citer_identifiant(nom_table)} "
        f"({colonnes_sql}) "
        f"SELECT {colonnes_sql} "
        f"FROM {citer_identifiant(nom_temporaire)}"
    )

    connexion.execute(
        f"DROP TABLE {citer_identifiant(nom_temporaire)}"
    )


def verifier_integrite(connexion):
    """Contrôle les effectifs et les clés étrangères."""

    print("\nVérification des tables :")

    for nom_table in FICHIERS:
        nombre = connexion.execute(
            f"SELECT COUNT(*) FROM {citer_identifiant(nom_table)}"
        ).fetchone()[0]

        print(f"  {nom_table} : {nombre:,} lignes")

    erreurs = connexion.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if erreurs:
        raise ValueError(
            f"Erreurs de clés étrangères : {len(erreurs)}"
        )

    print("  Intégrité référentielle : OK")

    # Vérification des colonnes nécessaires aux analyses.
    colonnes_attendues = {
        "individus": {"NOIND", "sex_PS", "tage_PS"},
        "apports": {"NOIND", "nutriment1", "nutriment3", "nutriment8"},
        "consommations": {
            "NUM_LIGNE",
            "NOIND",
            "aliment_code_INCA3",
            "aliment_libelle_INCA3",
            "qte_conso",
            "R24_pond",
            "proteines",
            "calcium",
            "fer",
            "fibres",
            "vitamine_c",
        },
    }

    for nom_table, attendues in colonnes_attendues.items():
        informations = connexion.execute(
            f"PRAGMA table_info({citer_identifiant(nom_table)})"
        ).fetchall()

        presentes = {ligne[1] for ligne in informations}
        manquantes = attendues - presentes

        if manquantes:
            raise ValueError(
                f"Colonnes manquantes dans {nom_table} : "
                f"{sorted(manquantes)}"
            )

    print("  Colonnes nécessaires aux analyses : OK")


def construire_base(destination):
    """
    Construit une nouvelle base sans modifier la base existante.
    """

    verifier_fichiers()

    destination = Path(destination).resolve()
    base_actuelle = (
        DOSSIER_DESTINATION / "nutrihfr.db"
    ).resolve()

    if destination == base_actuelle:
        raise ValueError(
            "La base principale nutrihfr.db est protégée."
        )

    if destination.exists():
        raise FileExistsError(
            f"Le fichier existe déjà : {destination}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)

    print("Construction de la base NutriHFr")
    print(f"Destination : {destination}")

    try:
        with sqlite3.connect(destination) as connexion:
            # Les contraintes sont contrôlées pendant la création.
            connexion.execute("PRAGMA foreign_keys = ON")

            # L'ordre garantit la présence des individus avant
            # l'insertion des apports et des consommations.
            for nom_table, nom_fichier in FICHIERS.items():
                nom_temporaire = importer_csv(
                    connexion,
                    nom_table,
                    nom_fichier,
                )

                creer_table_finale(
                    connexion,
                    nom_table,
                    nom_temporaire,
                )

            connexion.execute(
                "CREATE INDEX idx_consommations_noind "
                "ON consommations(NOIND)"
            )

            verifier_integrite(connexion)

            connexion.commit()

    except Exception:
        # Une base incomplète ne doit pas être conservée.
        destination.unlink(missing_ok=True)
        raise

    print("\nBase SQLite construite avec succès !")


if __name__ == "__main__":
    analyseur = argparse.ArgumentParser(
        description="Construction de la base SQLite NutriHFr."
    )

    analyseur.add_argument(
        "--output",
        type=Path,
        default=DOSSIER_DESTINATION / "nutrihfr_test.db",
        help="Chemin de la nouvelle base SQLite.",
    )

    arguments = analyseur.parse_args()

    construire_base(arguments.output)
