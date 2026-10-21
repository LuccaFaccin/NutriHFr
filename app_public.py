# -*- coding: utf-8 -*-

"""
NutriHFr - Tableau de bord public
Analyses descriptives agrégées des données INCA 3
Projet académique - AgroParisTech | Parcours IODAA
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NutriHFr",
    page_icon="🥗",
    layout="wide",
)

RACINE = Path(__file__).resolve().parent
DOSSIER = RACINE / "data" / "public"

NUTRIMENTS = {
    "Énergie (kcal/j)": "energie",
    "Protéines (g/j)": "proteines",
    "Fibres (g/j)": "fibres",
}

NUTRIMENTS_Q5 = {
    "Protéines": "proteines",
    "Calcium": "calcium",
    "Fer": "fer",
    "Fibres": "fibres",
    "Vitamine C": "vitamine_c",
}


@st.cache_data
def charger_json(nom):
    with open(DOSSIER / nom, encoding="utf-8") as fichier:
        return json.load(fichier)


@st.cache_data
def charger_csv(nom):
    return pd.read_csv(DOSSIER / nom)


def afficher_histogramme(tableau, moyenne, mediane, titre, axe_x):
    """Affiche un histogramme à partir de fréquences agrégées."""

    fig, ax = plt.subplots(figsize=(10, 5))

    largeur = tableau["borne_sup"] - tableau["borne_inf"]

    ax.bar(
        tableau["borne_inf"],
        tableau["effectif"],
        width=largeur,
        align="edge",
        edgecolor="white",
    )

    ax.axvline(
        moyenne,
        color="red",
        linestyle="--",
        label="Moyenne",
    )

    ax.axvline(
        mediane,
        color="green",
        linestyle=":",
        label="Médiane",
    )

    ax.set_title(titre)
    ax.set_xlabel(axe_x)
    ax.set_ylabel("Nombre d'individus")
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# 2. CHARGEMENT ET NAVIGATION
# ============================================================

if not DOSSIER.is_dir():
    st.error("Dossier des données agrégées introuvable.")
    st.stop()

st.title("🥗 NutriHFr")
st.write("Analyse des consommations et apports nutritionnels - INCA 3")
st.caption("Projet académique - AgroParisTech | Parcours IODAA")

st.info(
    "Version publique fondée sur des statistiques agrégées. "
    "Les résultats sont descriptifs et ne constituent pas des "
    "estimations représentatives de la population française."
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Vue d'ensemble",
        "Q1 - Apports énergétiques",
        "Q2 - Comparaison par sexe",
        "Q3 - Comparaison par âge",
        "Q4 - Densité nutritionnelle",
        "Q5 - Aliments contributeurs",
        "Q6 - Variabilité des apports",
    ],
)


# ============================================================
# 3. VUE D'ENSEMBLE
# ============================================================

if page == "Vue d'ensemble":

    st.header("Vue d'ensemble")

    vue = charger_json("vue_ensemble.json")

    col1, col2, col3 = st.columns(3)

    col1.metric("Nombre d'individus", f"{vue['effectif']:,}".replace(",", " "))
    col2.metric("Énergie moyenne", f"{vue['energie_moyenne']:.1f} kcal/j")
    col3.metric("Protéines moyennes", f"{vue['proteines_moyennes']:.1f} g/j")

    st.subheader("Répartition selon le sexe")
    st.bar_chart(pd.Series(vue["repartition_sexe"]))

    st.subheader("Répartition selon les classes d'âge")

    ages = pd.DataFrame(vue["repartition_age"])
    ages = ages.sort_values("tage_PS")

    st.bar_chart(ages.set_index("classe_age")["effectif"])


# ============================================================
# 4. Q1 - APPORTS ÉNERGÉTIQUES
# ============================================================

elif page == "Q1 - Apports énergétiques":

    st.header("Q1 - Distribution des apports énergétiques")

    stats = charger_json("q1_statistiques.json")
    hist = charger_csv("q1_histogramme.csv")

    col1, col2, col3 = st.columns(3)

    col1.metric("Effectif", int(stats["count"]))
    col2.metric("Moyenne", f"{stats['mean']:.2f} kcal/j")
    col3.metric("Médiane", f"{stats['50%']:.2f} kcal/j")

    afficher_histogramme(
        hist,
        stats["mean"],
        stats["50%"],
        "Distribution des apports énergétiques",
        "Énergie (kcal/j)",
    )

    st.subheader("Statistiques descriptives")
    st.dataframe(
        pd.DataFrame.from_dict(
            stats,
            orient="index",
            columns=["Énergie (kcal/j)"],
        )
    )


# ============================================================
# 5. Q2 - COMPARAISON PAR SEXE
# ============================================================

elif page == "Q2 - Comparaison par sexe":

    st.header("Q2 - Comparaison des apports selon le sexe")

    choix = st.selectbox("Choisir un nutriment", list(NUTRIMENTS))
    nutriment = NUTRIMENTS[choix]

    donnees = charger_csv("q2_sexe.csv")
    resultat = donnees[donnees["nutriment"] == nutriment].copy()
    resultat = resultat.set_index("sexe")[["count", "mean", "median", "std"]]

    st.subheader(f"Apports moyens : {choix}")
    st.bar_chart(resultat["mean"])

    st.subheader("Statistiques descriptives")
    st.dataframe(resultat.round(2))

    st.caption(
        "Les différences observées sont descriptives "
        "et ne constituent pas un test statistique."
    )


# ============================================================
# 6. Q3 - COMPARAISON PAR ÂGE
# ============================================================

elif page == "Q3 - Comparaison par âge":

    st.header("Q3 - Comparaison des apports selon l'âge")

    choix = st.selectbox("Choisir un nutriment", list(NUTRIMENTS))
    nutriment = NUTRIMENTS[choix]

    donnees = charger_csv("q3_age.csv")
    resultat = donnees[donnees["nutriment"] == nutriment].copy()
    resultat = resultat.sort_values("tage_PS")

    st.subheader(f"Apports moyens : {choix}")
    st.bar_chart(resultat.set_index("classe_age")["mean"])

    st.subheader("Statistiques descriptives")
    st.dataframe(
        resultat[
            ["classe_age", "count", "mean", "median", "std"]
        ].round(2),
        hide_index=True,
    )


# ============================================================
# 7. Q4 - DENSITÉ PROTÉIQUE
# ============================================================

elif page == "Q4 - Densité nutritionnelle":

    st.header("Q4 - Densité nutritionnelle")

    st.write(
        "Comparaison des apports en protéines "
        "pour 1 000 kcal consommées."
    )

    donnees = charger_csv("q4_densite.csv")
    resultat = donnees.set_index("sexe")[
        ["count", "mean", "median", "std"]
    ]

    st.subheader("Densité protéique moyenne selon le sexe")
    st.bar_chart(resultat["mean"])
    st.dataframe(resultat.round(2))

    st.latex(
        r"\text{Densité protéique} = "
        r"\frac{\text{Protéines (g/j)}}"
        r"{\text{Énergie (kcal/j)}} \times 1000"
    )

    st.caption(
        "Les individus présentant un apport énergétique nul "
        "sont exclus de ce calcul."
    )


# ============================================================
# 8. Q5 - ALIMENTS CONTRIBUTEURS
# ============================================================

elif page == "Q5 - Aliments contributeurs":

    st.header("Q5 - Principaux aliments contributeurs")

    choix = st.selectbox("Choisir un nutriment", list(NUTRIMENTS_Q5))
    nutriment = NUTRIMENTS_Q5[choix]

    donnees = charger_csv("q5_top10.csv")
    resultat = donnees[donnees["nutriment"] == nutriment].copy()

    tableau = resultat[
        ["aliment_libelle_INCA3", "contribution_pct"]
    ].copy()

    tableau.columns = ["Aliment", "Contribution (%)"]

    st.subheader(f"Top 10 des aliments - {choix}")
    st.dataframe(tableau.round(2), hide_index=True)

    graphique = tableau.sort_values("Contribution (%)")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(graphique["Aliment"], graphique["Contribution (%)"])
    ax.set_title(f"Principaux aliments contributeurs - {choix}")
    ax.set_xlabel("Contribution aux apports (%)")
    ax.set_ylabel("Aliment")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Contributions estimées à partir des quantités consommées "
        "pondérées (qte_conso_pond) et des teneurs nutritionnelles "
        "pour 100 g. Les résultats ne sont pas représentatifs "
        "de la population française."
    )


# ============================================================
# 9. Q6 - VARIABILITÉ DES APPORTS
# ============================================================

elif page == "Q6 - Variabilité des apports":

    st.header("Q6 - Variabilité des apports nutritionnels")

    st.write("Sous-groupe étudié : femmes âgées de 18 à 44 ans.")

    indicateurs = {
        "Énergie (kcal/j)": "energie",
        "Protéines (g/j)": "proteines",
    }

    choix = st.selectbox("Choisir un indicateur", list(indicateurs))
    nutriment = indicateurs[choix]

    donnees = charger_csv("q6_statistiques.csv")
    stats = donnees[donnees["nutriment"] == nutriment].iloc[0]

    histogrammes = charger_csv("q6_histogrammes.csv")
    hist = histogrammes[
        histogrammes["nutriment"] == nutriment
    ].copy()

    col1, col2, col3 = st.columns(3)

    col1.metric("Effectif", int(stats["count"]))
    col2.metric("Moyenne", f"{stats['mean']:.2f}")
    col3.metric("Coefficient de variation", f"{stats['cv']:.2f} %")

    afficher_histogramme(
        hist,
        stats["mean"],
        stats["50%"],
        "Variabilité des apports - Femmes de 18 à 44 ans",
        choix,
    )
