# -*- coding: utf-8 -*-

"""
Construction d'une base SQLite allégée pour le tableau de bord NutriHFr.

La base originale n'est jamais modifiée.
"""

import sqlite3
from pathlib import Path


RACINE = Path(__file__).resolve().parent.parent

BASE_SOURCE = RACINE / "data/processed/nutrihfr.db"
BASE_WEB = RACINE / "data/processed/nutrihfr_web.db"


def construire_base_web():

    if not BASE_SOURCE.is_file():
        raise FileNotFoundError(
            f"Base source introuvable : {BASE_SOURCE}"
        )

    if BASE_WEB.exists():
        raise FileExistsError(
            f"La base web existe déjà : {BASE_WEB}"
        )

    try:
        with sqlite3.connect(BASE_SOURCE) as connexion_source:
            with sqlite3.connect(BASE_WEB) as connexion_web:

                tables = {
                    "individus": """
                        SELECT NOIND, sex_PS, tage_PS
                        FROM individus
                    """,
                    "apports": """
                        SELECT NOIND, nutriment1, nutriment3, nutriment8
                        FROM apports
                    """,
                    "consommations": """
                        SELECT
                            aliment_code_INCA3,
                            aliment_libelle_INCA3,
                            qte_conso,
                            qte_conso_pond,
                            proteines,
                            calcium,
                            fer,
                            fibres,
                            vitamine_c
                        FROM consommations
                    """,
                }

                for nom_table, requete in tables.items():
                    curseur = connexion_source.execute(requete)
                    colonnes = [
                        description[0]
                        for description in curseur.description
                    ]

                    definitions = ", ".join(
                        f'"{colonne}"'
                        for colonne in colonnes
                    )

                    connexion_web.execute(
                        f'CREATE TABLE "{nom_table}" '
                        f'({definitions})'
                    )

                    marqueurs = ", ".join(
                        "?" for _ in colonnes
                    )

                    total = 0

                    while True:
                        lignes = curseur.fetchmany(10000)

                        if not lignes:
                            break

                        connexion_web.executemany(
                            f'INSERT INTO "{nom_table}" '
                            f'VALUES ({marqueurs})',
                            lignes
                        )

                        total += len(lignes)

                    print(f"{nom_table} : {total} lignes")

                connexion_web.commit()

    except Exception:
        # Suppression de la base partielle en cas d'échec
        if BASE_WEB.exists():
            BASE_WEB.unlink()
        raise

    print(f"\nBase web créée : {BASE_WEB}")
    print(
        f"Taille : {BASE_WEB.stat().st_size / 1024**2:.2f} Mo"
    )


if __name__ == "__main__":
    construire_base_web()
