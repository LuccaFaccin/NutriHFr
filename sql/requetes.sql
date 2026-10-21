-- Q1/Q2 : Statistiques descriptives de l'énergie par sexe
-- Résultats non pondérés

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
ORDER BY i.sex_PS;