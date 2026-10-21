# -*- coding: utf-8 -*-

"""
Gestion de la connexion et des requêtes SQL
pour le projet NutriHFr.
"""

import sqlite3
import pandas as pd


class BaseDonnees:
    """Classe permettant d'interagir avec une base SQLite."""

    def __init__(self, chemin_base):
        # Enregistrement du chemin vers la base de données
        self.chemin_base = chemin_base

    def connecter(self):
        # Création d'une connexion à la base SQLite
        connexion = sqlite3.connect(self.chemin_base)

        # Activation des contraintes de clés étrangères
        connexion.execute("PRAGMA foreign_keys = ON")

        return connexion

    def executer_requete(self, requete, parametres=None):
        # Exécution d'une requête SQL et récupération des résultats
        with self.connecter() as connexion:
            resultat = pd.read_sql_query(
                requete,
                connexion,
                params=parametres
            )

        return resultat

    def compter_individus(self):
        # Comptage des individus disposant d'apports nutritionnels
        requete = """
        SELECT COUNT(*) AS nombre_individus
        FROM apports
        """

        return self.executer_requete(requete)

    def statistiques_energie(self):
        # Calcul des statistiques énergétiques par sexe
        requete = """
        SELECT
            i.sex_PS AS sexe,
            COUNT(*) AS nombre_individus,
            ROUND(AVG(a.nutriment1), 2) AS energie_moyenne_kcal,
            ROUND(MIN(a.nutriment1), 2) AS energie_min_kcal,
            ROUND(MAX(a.nutriment1), 2) AS energie_max_kcal
        FROM individus AS i
        INNER JOIN apports AS a
            ON i.NOIND = a.NOIND
        GROUP BY i.sex_PS
        ORDER BY i.sex_PS
        """

        return self.executer_requete(requete)