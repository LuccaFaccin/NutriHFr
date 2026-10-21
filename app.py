# -*- coding: utf-8 -*-
"""
NutriHFr - Tableau de bord interactif
Analyse des consommations et des apports nutritionnels INCA 3
Projet académique - AgroParisTech | IODAA
"""

from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# ============================================================
# 1. CONFIGURATION GÉNÉRALE
# ============================================================

st.set_page_config(
    page_title="NutriHFr",
    page_icon="🥗",
    layout="wide"
)

# Répertoire principal du projet
BASE_DIR = Path(__file__).resolve().parent

# Sélection de la base destinée au tableau de bord
BASE_WEB = BASE_DIR / "data" / "processed" / "nutrihfr_web.db"
BASE_ORIGINALE = BASE_DIR / "data" / "processed" / "nutrihfr.db"

DB_PATH = BASE_WEB if BASE_WEB.is_file() else BASE_ORIGINALE

CODES_SEXE = {
    1: "Homme",
    2: "Femme"
}

CODES_AGE = {
    1: "0-11 mois",
    2: "1-3 ans",
    3: "4-6 ans",
    4: "7-10 ans",
    5: "11-14 ans",
    6: "15-17 ans",
    7: "18-44 ans",
    8: "45-64 ans",
    9: "65-79 ans"
}

NUTRIMENTS = {
    "Énergie (kcal/j)": "energie",
    "Protéines (g/j)": "proteines",
    "Fibres (g/j)": "fibres"
}

NUTRIMENTS_Q5 = {
    "Protéines": "proteines",
    "Calcium": "calcium",
    "Fer": "fer",
    "Fibres": "fibres",
    "Vitamine C": "vitamine_c"
}


# ============================================================
# 2. CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def charger_donnees_nutritionnelles():

    requete = """
        SELECT
            i.NOIND,
            i.sex_PS,
            i.tage_PS,
            a.nutriment1 AS energie,
            a.nutriment3 AS proteines,
            a.nutriment8 AS fibres
        FROM individus AS i
        INNER JOIN apports AS a
            ON i.NOIND = a.NOIND
    """

    with sqlite3.connect(DB_PATH) as connexion:
        donnees = pd.read_sql_query(requete, connexion)

    donnees["sexe"] = donnees["sex_PS"].map(CODES_SEXE)
    donnees["classe_age"] = donnees["tage_PS"].map(CODES_AGE)

    return donnees


@st.cache_data
def charger_consommations():

    requete = """
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
    """

    with sqlite3.connect(DB_PATH) as connexion:
        return pd.read_sql_query(requete, connexion)


@st.cache_data
def calculer_contributions_alimentaires():
    donnees = charger_consommations().copy()

    # Calcul des apports nutritionnels à partir des quantités pondérées
    for nutriment in NUTRIMENTS_Q5.values():
        donnees[f"apport_pond_{nutriment}"] = (
            donnees["qte_conso_pond"]
            * donnees[nutriment]
            / 100
        )

    colonnes_apports = [
        f"apport_pond_{nutriment}"
        for nutriment in NUTRIMENTS_Q5.values()
    ]

    colonnes_apports = [
        f"apport_pond_{nutriment}"
        for nutriment in NUTRIMENTS_Q5.values()
    ]

    contributions = (
        donnees.groupby(
            ["aliment_code_INCA3", "aliment_libelle_INCA3"],
            as_index=False
        )[colonnes_apports]
        .sum()
    )

    # Calcul des contributions relatives
    for nutriment in NUTRIMENTS_Q5.values():

        colonne = f"apport_pond_{nutriment}"
        total = contributions[colonne].sum()

        if total > 0:
            contributions[f"pct_{nutriment}"] = (
                contributions[colonne] / total * 100
            )
        else:
            contributions[f"pct_{nutriment}"] = 0.0

    return contributions


# ============================================================
# 3. VÉRIFICATION DE LA BASE DE DONNÉES
# ============================================================

if not DB_PATH.exists():

    st.error(
        "Base de données introuvable : "
        "data/processed/nutrihfr.db"
    )

    st.stop()


try:
    df = charger_donnees_nutritionnelles()

except (sqlite3.Error, pd.errors.DatabaseError) as erreur:

    st.error(f"Erreur de chargement des données : {erreur}")
    st.stop()


# ============================================================
# 4. EN-TÊTE DE L'APPLICATION
# ============================================================

st.title("🥗 NutriHFr")

st.write(
    "Analyse des consommations et apports nutritionnels - INCA 3"
)

st.caption(
    "Projet académique - AgroParisTech | Parcours IODAA"
)


# ============================================================
# 5. NAVIGATION - MENU UNIQUE
# ============================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Vue d'ensemble",
        "Q1 - Apports énergétiques",
        "Q2 - Comparaison par sexe",
        "Q3 - Comparaison par âge",
        "Q4 - Densité nutritionnelle",
        "Q5 - Aliments contributeurs",
        "Q6 - Variabilité des apports"
    ]
)


# ============================================================
# 6. VUE D'ENSEMBLE
# ============================================================

if page == "Vue d'ensemble":

    st.header("Vue d'ensemble")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Nombre d'individus",
        f"{len(df):,}".replace(",", " ")
    )

    col2.metric(
        "Énergie moyenne",
        f"{df['energie'].mean():.1f} kcal/j"
    )

    col3.metric(
        "Protéines moyennes",
        f"{df['proteines'].mean():.1f} g/j"
    )

    st.subheader("Répartition selon le sexe")

    repartition = df["sexe"].value_counts()

    st.bar_chart(repartition)

    st.subheader("Répartition selon les classes d'âge")

    repartition_age = (
        df.groupby(["tage_PS", "classe_age"])
        .size()
        .reset_index(name="Effectif")
        .sort_values("tage_PS")
    )

    st.bar_chart(
        repartition_age.set_index("classe_age")["Effectif"]
    )

    st.info(
        "Les résultats sont descriptifs et non pondérés "
        "par les poids d'enquête individuels."
    )


# ============================================================
# 7. Q1 - DISTRIBUTION DES APPORTS ÉNERGÉTIQUES
# ============================================================

elif page == "Q1 - Apports énergétiques":

    st.header("Q1 - Distribution des apports énergétiques")

    serie = df["energie"].dropna()

    col1, col2, col3 = st.columns(3)

    col1.metric("Effectif", len(serie))
    col2.metric("Moyenne", f"{serie.mean():.2f} kcal/j")
    col3.metric("Médiane", f"{serie.median():.2f} kcal/j")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        serie,
        bins=35,
        edgecolor="white"
    )

    ax.axvline(
        serie.mean(),
        color="red",
        linestyle="--",
        label="Moyenne"
    )

    ax.axvline(
        serie.median(),
        color="green",
        linestyle=":",
        label="Médiane"
    )

    ax.set_title("Distribution des apports énergétiques")
    ax.set_xlabel("Énergie (kcal/j)")
    ax.set_ylabel("Nombre d'individus")
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Statistiques descriptives")

    st.dataframe(
        serie.describe().to_frame("Énergie (kcal/j)")
    )


# ============================================================
# 8. Q2 - COMPARAISON SELON LE SEXE
# ============================================================

elif page == "Q2 - Comparaison par sexe":

    st.header("Q2 - Comparaison des apports selon le sexe")

    choix = st.selectbox(
        "Choisir un nutriment",
        list(NUTRIMENTS.keys())
    )

    colonne = NUTRIMENTS[choix]

    resultat = (
        df.groupby("sexe")[colonne]
        .agg(["count", "mean", "median", "std"])
    )

    st.subheader(f"Apports moyens : {choix}")

    st.bar_chart(resultat["mean"])

    st.subheader("Statistiques descriptives")

    st.dataframe(resultat.round(2))

    st.caption(
        "Les différences observées sont descriptives "
        "et ne constituent pas un test statistique."
    )


# ============================================================
# 9. Q3 - COMPARAISON SELON L'ÂGE
# ============================================================

elif page == "Q3 - Comparaison par âge":

    st.header("Q3 - Comparaison des apports selon l'âge")

    choix = st.selectbox(
        "Choisir un nutriment",
        list(NUTRIMENTS.keys())
    )

    colonne = NUTRIMENTS[choix]

    resultat = (
        df.groupby(["tage_PS", "classe_age"])[colonne]
        .agg(["count", "mean", "median", "std"])
        .reset_index()
        .sort_values("tage_PS")
    )

    st.subheader(f"Apports moyens : {choix}")

    st.bar_chart(
        resultat.set_index("classe_age")["mean"]
    )

    st.subheader("Statistiques descriptives")

    st.dataframe(
        resultat.round(2),
        hide_index=True
    )


# ============================================================
# 10. Q4 - DENSITÉ NUTRITIONNELLE
# ============================================================

elif page == "Q4 - Densité nutritionnelle":

    st.header("Q4 - Densité nutritionnelle")

    st.write(
        "Comparaison des apports en protéines "
        "pour 1 000 kcal consommées."
    )

    df_densite = df[df["energie"] > 0].copy()

    df_densite["densite_proteique"] = (
        df_densite["proteines"]
        / df_densite["energie"]
        * 1000
    )

    resultat = (
        df_densite.groupby("sexe")["densite_proteique"]
        .agg(["count", "mean", "median", "std"])
    )

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
# 11. Q5 - ALIMENTS CONTRIBUTEURS
# ============================================================

elif page == "Q5 - Aliments contributeurs":

    st.header("Q5 - Principaux aliments contributeurs")

    st.write(
        "Identification des aliments contribuant le plus "
        "aux apports nutritionnels."
    )

    choix = st.selectbox(
        "Choisir un nutriment",
        list(NUTRIMENTS_Q5.keys())
    )

    nutriment = NUTRIMENTS_Q5[choix]

    try:
        contributions = calculer_contributions_alimentaires()

    except (sqlite3.Error, pd.errors.DatabaseError) as erreur:
        st.error(f"Erreur lors de l'analyse alimentaire : {erreur}")
        st.stop()

    colonne_pct = f"pct_{nutriment}"

    top10 = (
        contributions.nlargest(10, colonne_pct)
        .copy()
    )

    st.subheader(f"Top 10 des aliments - {choix}")

    tableau = top10[
        ["aliment_libelle_INCA3", colonne_pct]
    ].copy()

    tableau.columns = [
        "Aliment",
        "Contribution (%)"
    ]

    st.dataframe(
        tableau.round(2),
        hide_index=True
    )

    graphique = tableau.sort_values("Contribution (%)")

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(
        graphique["Aliment"],
        graphique["Contribution (%)"]
    )

    ax.set_title(
        f"Principaux aliments contributeurs - {choix}"
    )

    ax.set_xlabel("Contribution aux apports (%)")
    ax.set_ylabel("Aliment")

    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


    st.caption(
        "Contributions estimées à partir des quantités consommées "
        "pondérées (qte_conso_pond) et des teneurs nutritionnelles "
        "pour 100 g. La pondération R24_pond est déjà intégrée "
        "dans qte_conso_pond. Les résultats sont descriptifs et "
        "ne constituent pas des estimations représentatives "
        "de la population française."
    )

# ============================================================
# 12. Q6 - VARIABILITÉ DES APPORTS
# ============================================================

elif page == "Q6 - Variabilité des apports":

    st.header("Q6 - Variabilité des apports nutritionnels")

    st.write(
        "Sous-groupe étudié : femmes âgées de 18 à 44 ans."
    )

    df_groupe = df[
        (df["sex_PS"] == 2)
        & (df["tage_PS"] == 7)
    ].copy()

    indicateurs = {
        "Énergie (kcal/j)": "energie",
        "Protéines (g/j)": "proteines"
    }

    choix = st.selectbox(
        "Choisir un indicateur",
        list(indicateurs.keys())
    )

    colonne = indicateurs[choix]

    serie = df_groupe[colonne].dropna()

    moyenne = serie.mean()
    ecart_type = serie.std()
    mediane = serie.median()
    cv = ecart_type / moyenne * 100 if moyenne != 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Effectif", len(serie))
    col2.metric("Moyenne", f"{moyenne:.2f}")
    col3.metric("Coefficient de variation", f"{cv:.2f} %")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        serie,
        bins=30,
        edgecolor="white"
    )

    ax.axvline(
        moyenne,
        color="red",
        linestyle="--",
        label="Moyenne"
    )

    ax.axvline(
        mediane,
        color="green",
        linestyle=":",
        label="Médiane"
    )

    ax.set_title(
        f"Variabilité des apports - Femmes de 18 à 44 ans\n{choix}"
    )

    ax.set_xlabel(choix)
    ax.set_ylabel("Nombre d'individus")
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Statistiques descriptives")

    statistiques = serie.describe(
        percentiles=[0.10, 0.25, 0.5, 0.75, 0.90]
    )

    st.dataframe(
        statistiques.to_frame("Valeur").round(2)
    )

    st.write(
        f"Coefficient de variation : **{cv:.2f} %**"
    )


# ============================================================
# 13. PIED DE PAGE
# ============================================================

st.divider()

st.caption(
    "NutriHFr - Projet académique AgroParisTech | "
    "Données INCA 3 | Analyses descriptives"
)
