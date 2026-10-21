
# -*- coding: utf-8 -*-

"""
Tests automatisés des classes NutriHFr.

Les tests utilisent une base SQLite temporaire afin
de ne pas modifier les données INCA 3 du projet.
"""

import sqlite3

import pandas as pd
import pytest

from src.base_donnees import BaseDonnees
from src.analyse_nutritionnelle import AnalyseNutritionnelle


@pytest.fixture
def base_test(tmp_path):
    """Crée une petite base SQLite pour les tests."""

    chemin = tmp_path / "test_nutrihfr.db"

    with sqlite3.connect(chemin) as connexion:
        connexion.executescript(
            """
            CREATE TABLE individus (
                NOIND INTEGER PRIMARY KEY,
                sex_PS INTEGER,
                tage_PS INTEGER
            );

            CREATE TABLE apports (
                NOIND INTEGER PRIMARY KEY,
                nutriment1 REAL,
                nutriment3 REAL,
                nutriment8 REAL,
                FOREIGN KEY (NOIND) REFERENCES individus(NOIND)
            );

            INSERT INTO individus VALUES
                (1, 1, 7),
                (2, 2, 7),
                (3, 2, 8);

            INSERT INTO apports VALUES
                (1, 2000, 80, 20),
                (2, 1500, 60, 15),
                (3, 2500, 100, 25);
            """
        )

    return chemin


def test_connexion(base_test):
    """Vérifie la connexion à SQLite."""

    base = BaseDonnees(base_test)

    with base.connecter() as connexion:
        resultat = connexion.execute(
            "SELECT COUNT(*) FROM individus"
        ).fetchone()[0]

    assert resultat == 3


def test_compter_individus(base_test):
    """Vérifie le comptage des apports disponibles."""

    base = BaseDonnees(base_test)
    resultat = base.compter_individus()

    assert resultat.iloc[0]["nombre_individus"] == 3


def test_statistiques_energie(base_test):
    """Vérifie les statistiques énergétiques globales."""

    analyse = AnalyseNutritionnelle(base_test)
    statistiques = analyse.statistiques_energie()

    assert statistiques["count"] == 3
    assert statistiques["mean"] == pytest.approx(2000)
    assert statistiques["min"] == 1500
    assert statistiques["max"] == 2500


def test_energie_par_sexe(base_test):
    """Vérifie les moyennes énergétiques selon le sexe."""

    analyse = AnalyseNutritionnelle(base_test)
    resultat = analyse.energie_par_sexe()

    assert resultat.loc[1, "mean"] == 2000
    assert resultat.loc[2, "mean"] == 2000
    assert resultat.loc[2, "count"] == 2


def test_energie_par_age(base_test):
    """Vérifie les moyennes énergétiques selon l'âge."""

    analyse = AnalyseNutritionnelle(base_test)
    resultat = analyse.energie_par_age()

    assert resultat.loc[7, "mean"] == 1750
    assert resultat.loc[8, "mean"] == 2500


def test_densite_nutritionnelle(base_test):
    """Vérifie le calcul des protéines pour 1 000 kcal."""

    analyse = AnalyseNutritionnelle(base_test)
    resultat = analyse.densite_nutritionnelle("nutriment3")

    assert len(resultat) == 3
    assert resultat["densite_pour_1000_kcal"].tolist() == pytest.approx(
        [40, 40, 40]
    )


def test_nutriment_invalide(base_test):
    """Vérifie le rejet d'un nom de nutriment invalide."""

    analyse = AnalyseNutritionnelle(base_test)

    with pytest.raises(ValueError):
        analyse.densite_nutritionnelle("colonne_inconnue")


def test_nutriments_par_sexe(base_test):
    """Vérifie les moyennes énergétiques et protéiques."""

    analyse = AnalyseNutritionnelle(base_test)
    resultat = analyse.nutriments_par_sexe()

    femme = resultat.loc[resultat["sexe"] == 2].iloc[0]

    assert femme["nombre_individus"] == 2
    assert femme["energie_moyenne_kcal"] == 2000
    assert femme["proteines_moyennes_g"] == 80


def test_resultat_dataframe(base_test):
    """Vérifie le format des résultats SQL."""

    base = BaseDonnees(base_test)

    resultat = base.executer_requete(
        "SELECT NOIND FROM individus ORDER BY NOIND"
    )

    assert isinstance(resultat, pd.DataFrame)
    assert resultat["NOIND"].tolist() == [1, 2, 3]
