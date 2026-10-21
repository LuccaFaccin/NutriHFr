# -*- coding: utf-8 -*-

"""Analyse de sensibilité des apports selon la pondération INCA 3 POP3."""

from pathlib import Path
import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
DOSSIER = RACINE / "data" / "raw" / "inca3"

ind = pd.read_csv(
    DOSSIER / "description-indiv.csv",
    sep=";",
    encoding="latin-1",
    low_memory=False,
)

ap = pd.read_csv(
    DOSSIER / "apports-nut-alim.csv",
    sep=";",
    encoding="latin-1",
    low_memory=False,
)

donnees = ap.merge(
    ind[
        [
            "NOIND",
            "pond_indiv_adu_pop3",
            "pond_indiv_enf_pop3",
        ]
    ],
    on="NOIND",
    how="inner",
    validate="one_to_one",
)

nutriments = {
    "Énergie (kcal/j)": "nutriment1",
    "Protéines (g/j)": "nutriment3",
}

groupes = {
    "Adultes": "pond_indiv_adu_pop3",
    "Enfants": "pond_indiv_enf_pop3",
}

resultats = []

for groupe, colonne_poids in groupes.items():
    for libelle, colonne_nutriment in nutriments.items():

        valeurs = pd.to_numeric(
            donnees[colonne_nutriment], errors="coerce"
        )
        poids = pd.to_numeric(
            donnees[colonne_poids], errors="coerce"
        )

        valide = (
            valeurs.notna()
            & poids.notna()
            & (poids > 0)
        )

        x = valeurs[valide].to_numpy()
        w = poids[valide].to_numpy()

        moyenne_simple = float(np.mean(x))
        moyenne_ponderee = float(np.average(x, weights=w))

        resultats.append(
            {
                "Population": groupe,
                "Nutriment": libelle,
                "Effectif": len(x),
                "Moyenne non pondérée": moyenne_simple,
                "Moyenne pondérée POP3": moyenne_ponderee,
                "Écart (%)": (
                    (moyenne_ponderee / moyenne_simple - 1) * 100
                    if moyenne_simple != 0 else np.nan
                ),
                "Somme des poids": float(np.sum(w)),
            }
        )

tableau = pd.DataFrame(resultats)

print("\nComparaison des moyennes :")
print(tableau.round(2).to_string(index=False))

sortie = RACINE / "reports" / "comparaison_ponderations.csv"
tableau.to_csv(sortie, index=False)

print(f"\nRésultats enregistrés : {sortie}")

