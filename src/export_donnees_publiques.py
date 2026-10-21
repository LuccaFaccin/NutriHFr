# -*- coding: utf-8 -*-

"""
Exportation de statistiques agrégées pour le tableau de bord public.

Les données individuelles et les consommations détaillées
ne sont pas exportées.
"""

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


RACINE = Path(__file__).resolve().parent.parent
BASE_SOURCE = RACINE / "data/processed/nutrihfr_web.db"
DESTINATION = RACINE / "data/public"

CODES_SEXE = {1: "Homme", 2: "Femme"}

CODES_AGE = {
    1: "0-11 mois",
    2: "1-3 ans",
    3: "4-6 ans",
    4: "7-10 ans",
    5: "11-14 ans",
    6: "15-17 ans",
    7: "18-44 ans",
    8: "45-64 ans",
    9: "65-79 ans",
}

NUTRIMENTS_Q5 = [
    "proteines", "calcium", "fer", "fibres", "vitamine_c"
]


def statistiques_par_groupe(df, groupes, variables):
    """Calcule les statistiques descriptives par groupe."""

    resultats = []

    for variable in variables:
        tableau = (
            df.groupby(groupes, dropna=False)[variable]
            .agg(["count", "mean", "median", "std"])
            .reset_index()
        )
        tableau["nutriment"] = variable
        resultats.append(tableau)

    return pd.concat(resultats, ignore_index=True)


def exporter():

    if not BASE_SOURCE.is_file():
        raise FileNotFoundError(
            f"Base source introuvable : {BASE_SOURCE}"
        )

    DESTINATION.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(BASE_SOURCE) as connexion:
        df = pd.read_sql_query(
            """
            SELECT
                i.NOIND,
                i.sex_PS,
                i.tage_PS,
                a.nutriment1 AS energie,
                a.nutriment3 AS proteines,
                a.nutriment8 AS fibres
            FROM individus i
            INNER JOIN apports a ON i.NOIND = a.NOIND
            """,
            connexion,
        )

        consommations = pd.read_sql_query(
            """
            SELECT
                aliment_code_INCA3,
                aliment_libelle_INCA3,
                qte_conso_pond,
                proteines,
                calcium,
                fer,
                fibres,
                vitamine_c
            FROM consommations
            """,
            connexion,
        )

    df["sexe"] = df["sex_PS"].map(CODES_SEXE)
    df["classe_age"] = df["tage_PS"].map(CODES_AGE)

    # Vue d'ensemble
    vue = {
        "effectif": int(len(df)),
        "energie_moyenne": float(df["energie"].mean()),
        "proteines_moyennes": float(df["proteines"].mean()),
        "repartition_sexe": (
            df["sexe"].value_counts().to_dict()
        ),
        "repartition_age": (
            df.groupby(["tage_PS", "classe_age"])
            .size()
            .reset_index(name="effectif")
            .sort_values("tage_PS")
            .to_dict(orient="records")
        ),
    }

    with open(
        DESTINATION / "vue_ensemble.json",
        "w",
        encoding="utf-8",
    ) as fichier:
        json.dump(vue, fichier, ensure_ascii=False, indent=2)

    # Q1 : statistiques et fréquences de l'histogramme
    energie = df["energie"].dropna()

    statistiques_q1 = (
        energie.describe().to_dict()
    )

    with open(
        DESTINATION / "q1_statistiques.json",
        "w",
        encoding="utf-8",
    ) as fichier:
        json.dump(
            statistiques_q1,
            fichier,
            ensure_ascii=False,
            indent=2,
        )

    frequences, bornes = np.histogram(energie, bins=35)

    pd.DataFrame({
        "borne_inf": bornes[:-1],
        "borne_sup": bornes[1:],
        "effectif": frequences,
    }).to_csv(
        DESTINATION / "q1_histogramme.csv",
        index=False,
    )

    # Q2 : statistiques selon le sexe
    statistiques_par_groupe(
        df,
        ["sexe"],
        ["energie", "proteines", "fibres"],
    ).to_csv(
        DESTINATION / "q2_sexe.csv",
        index=False,
    )

    # Q3 : statistiques selon l'âge
    statistiques_par_groupe(
        df,
        ["tage_PS", "classe_age"],
        ["energie", "proteines", "fibres"],
    ).to_csv(
        DESTINATION / "q3_age.csv",
        index=False,
    )

    # Q4 : densité protéique
    densite = df[df["energie"] > 0].copy()
    densite["densite_proteique"] = (
        densite["proteines"] / densite["energie"] * 1000
    )

    statistiques_par_groupe(
        densite,
        ["sexe"],
        ["densite_proteique"],
    ).to_csv(
        DESTINATION / "q4_densite.csv",
        index=False,
    )

    # Q5 : contributions par aliment
    for nutriment in NUTRIMENTS_Q5:
        consommations[f"apport_pond_{nutriment}"] = (
            consommations["qte_conso_pond"]
            * consommations[nutriment]
            / 100
        )

    colonnes_apports = [
        f"apport_pond_{nutriment}"
        for nutriment in NUTRIMENTS_Q5
    ]

    contributions = (
        consommations.groupby(
            ["aliment_code_INCA3", "aliment_libelle_INCA3"],
            as_index=False,
        )[colonnes_apports]
        .sum()
    )

    for nutriment in NUTRIMENTS_Q5:
        colonne = f"apport_pond_{nutriment}"
        total = contributions[colonne].sum()

        contributions[f"pct_{nutriment}"] = (
            contributions[colonne] / total * 100
            if total > 0
            else 0.0
        )

    # Seuls les dix principaux aliments sont publiés
    # pour chaque nutriment.
    top10 = []

    for nutriment in NUTRIMENTS_Q5:
        colonne = f"pct_{nutriment}"

        tableau = contributions.nlargest(10, colonne)[
            ["aliment_libelle_INCA3", colonne]
        ].copy()

        tableau["nutriment"] = nutriment
        tableau = tableau.rename(
            columns={colonne: "contribution_pct"}
        )

        top10.append(tableau)

    pd.concat(top10, ignore_index=True).to_csv(
        DESTINATION / "q5_top10.csv",
        index=False,
    )

    # Q6 : femmes de 18 à 44 ans
    groupe = df[
        (df["sex_PS"] == 2)
        & (df["tage_PS"] == 7)
    ]

    statistiques_q6 = []
    histogrammes_q6 = []

    for variable in ["energie", "proteines"]:
        serie = groupe[variable].dropna()

        stats = serie.describe().to_dict()
        stats["nutriment"] = variable
        stats["cv"] = (
            float(serie.std() / serie.mean() * 100)
            if serie.mean() != 0
            else 0.0
        )
        statistiques_q6.append(stats)

        frequences, bornes = np.histogram(serie, bins=30)

        histogrammes_q6.append(
            pd.DataFrame({
                "nutriment": variable,
                "borne_inf": bornes[:-1],
                "borne_sup": bornes[1:],
                "effectif": frequences,
            })
        )

    pd.DataFrame(statistiques_q6).to_csv(
        DESTINATION / "q6_statistiques.csv",
        index=False,
    )

    pd.concat(histogrammes_q6, ignore_index=True).to_csv(
        DESTINATION / "q6_histogrammes.csv",
        index=False,
    )

    print("Exportation terminée.")
    print(f"Dossier : {DESTINATION}")

    for fichier in sorted(DESTINATION.iterdir()):
        print(
            f"{fichier.name} : "
            f"{fichier.stat().st_size / 1024:.1f} Ko"
        )


if __name__ == "__main__":
    exporter()
