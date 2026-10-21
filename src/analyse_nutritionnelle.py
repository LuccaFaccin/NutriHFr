# -*- coding: utf-8 -*-

"""
Analyses nutritionnelles des données INCA 3.

Cette classe utilise la base SQLite pour calculer
des indicateurs nutritionnels descriptifs.
"""

import pandas as pd

from src.base_donnees import BaseDonnees


class AnalyseNutritionnelle:
    """Classe dédiée aux analyses nutritionnelles."""

    def __init__(self, chemin_base):
        # Composition : utilisation d'un objet BaseDonnees
        self.base = BaseDonnees(chemin_base)

    def donnees_energie(self):
        """Récupère les apports énergétiques individuels."""

        requete = """
        SELECT
            i.NOIND,
            i.sex_PS,
            i.tage_PS,
            a.nutriment1 AS energie_kcal
        FROM individus AS i
        INNER JOIN apports AS a
            ON i.NOIND = a.NOIND
        """

        return self.base.executer_requete(requete)

    def statistiques_energie(self):
        """Calcule les statistiques descriptives de l'énergie."""

        df = self.donnees_energie()

        return df["energie_kcal"].describe()

    def energie_par_sexe(self):
        """Calcule les statistiques énergétiques selon le sexe."""

        df = self.donnees_energie()

        return (
            df.groupby("sex_PS")["energie_kcal"]
            .agg(["count", "mean", "median", "std", "min", "max"])
            .round(2)
        )

    def energie_par_age(self):
        """Calcule les statistiques énergétiques par classe d'âge."""

        df = self.donnees_energie()

        return (
            df.groupby("tage_PS")["energie_kcal"]
            .agg(["count", "mean", "median", "std"])
            .round(2)
        )

    def densite_nutritionnelle(self, colonne_nutriment):
        """
        Calcule un apport nutritionnel pour 1 000 kcal.

        Seuls les individus ayant une énergie positive
        sont retenus pour éviter une division par zéro.
        """

        # Validation du nom de colonne
        if not colonne_nutriment.startswith("nutriment"):
            raise ValueError("Nom de nutriment invalide.")

        if not colonne_nutriment[9:].isdigit():
            raise ValueError("Code de nutriment invalide.")

        # Récupération des données nutritionnelles
        requete = f"""
        SELECT
            NOIND,
            nutriment1 AS energie_kcal,
            "{colonne_nutriment}" AS apport_nutriment
        FROM apports
        WHERE nutriment1 > 0
        """

        df = self.base.executer_requete(requete)

        # Calcul de la densité nutritionnelle
        df["densite_pour_1000_kcal"] = (
            df["apport_nutriment"] / df["energie_kcal"] * 1000
        )

        return df


    def nutriments_par_sexe(self):
        """
        Compare les apports énergétiques et protéiques
        selon les modalités de sexe.
        """

        requete = """
        SELECT
            i.sex_PS AS sexe,
            COUNT(*) AS nombre_individus,
            ROUND(AVG(a.nutriment1), 2) AS energie_moyenne_kcal,
            ROUND(AVG(a.nutriment3), 2) AS proteines_moyennes_g
        FROM individus AS i
        INNER JOIN apports AS a
            ON i.NOIND = a.NOIND
        GROUP BY i.sex_PS
        ORDER BY i.sex_PS
        """

        return self.base.executer_requete(requete)