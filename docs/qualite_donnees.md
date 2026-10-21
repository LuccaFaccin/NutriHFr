# Qualité des données et limites méthodologiques — NutriHFr

## 1. Objectif

Ce document présente les contrôles de qualité effectués sur les données INCA 3 utilisées dans le projet NutriHFr, ainsi que les principales précautions nécessaires à l'interprétation des résultats.

## 2. Sources et volumes de données

Trois fichiers CSV sont importés dans la base SQLite.

| Table | Nombre de lignes | Clé primaire |
|---|---:|---|
| `individus` | 5 855 | `NOIND` |
| `apports` | 4 114 | `NOIND` |
| `consommations` | 256 301 | `NUM_LIGNE` |

Les fichiers originaux sont conservés sans modification.

La différence entre les effectifs des tables `individus` et `apports` signifie que tous les individus décrits dans la première table ne disposent pas d'un enregistrement dans la seconde.

## 3. Intégrité de la base relationnelle

Les vérifications réalisées comprennent :

- L'unicité des clés primaires.
- L'existence des colonnes nécessaires.
- La cohérence des relations entre les tables.
- Le contrôle des effectifs après importation.
- La vérification des contraintes de clés étrangères.

Le contrôle `PRAGMA foreign_key_check` n'a signalé aucune violation dans la base reconstruite.

## 4. Validation de la reconstruction

Une seconde base SQLite a été construite à partir des fichiers CSV originaux, indépendamment de la base utilisée par le dashboard.

Les deux bases présentent les mêmes effectifs :

- 5 855 individus.
- 4 114 enregistrements d'apports nutritionnels.
- 256 301 enregistrements de consommation.

Les valeurs moyennes vérifiées sont également identiques :

| Indicateur | Valeur |
|---|---:|
| Apport énergétique moyen | 1 911,88 kcal/j |
| Apport protéique moyen | 73,85 g/j |

Ces comparaisons confirment la cohérence des contrôles effectués. Elles ne constituent toutefois pas une comparaison exhaustive de chaque cellule.

## 5. Valeurs nulles et valeurs manquantes

### Apports énergétiques nuls

Parmi les 4 114 observations d'apports nutritionnels, huit présentent un apport énergétique nul.

Ces observations sont conservées pour les statistiques descriptives générales.

En revanche, elles sont exclues du calcul de la densité protéique, puisqu'une division par zéro n'est pas définie.

### Disponibilité des données

Les analyses utilisent les observations pour lesquelles les variables nécessaires sont disponibles.

Les effectifs peuvent donc varier selon les questions et les indicateurs.

Les valeurs manquantes ne sont pas remplacées automatiquement par des valeurs estimées.

## 6. Vérification de la pondération des consommations

La documentation INCA 3 précise que la variable `qte_conso_pond` intègre la pondération `R24_pond`, destinée à tenir compte de la répartition des jours de rappel alimentaire.

Une vérification numérique a comparé :

`qte_conso_pond`

et

`qte_conso × R24_pond`

Résultats :

| Contrôle | Résultat |
|---|---:|
| Lignes comparables | 256 021 |
| Écart absolu moyen | 0,00000415 |
| Écart absolu maximal | 0,00012316 |

Les écarts observés sont très faibles et compatibles avec des différences d'arrondi.

La comparaison ne porte pas sur les 280 autres enregistrements, car au moins une des variables nécessaires est absente. Ces lignes ne sont donc pas couvertes par cette vérification numérique.

L'analyse Q5 utilise directement `qte_conso_pond` afin d'éviter une multiplication redondante par `R24_pond`.

## 7. Contrôles du code

Les contrôles automatisés sont réalisés avec `pytest`.

Dernier résultat :

`9 passed`

La syntaxe des scripts principaux a également été vérifiée avec `py_compile`.

Le tableau de bord Streamlit a été exécuté localement et les pages d'analyse ont été consultées.

Ces vérifications confirment le fonctionnement des composants testés, mais ne garantissent pas l'absence de toute erreur analytique.

## 8. Limites statistiques

### Statistiques descriptives

Les résultats Q1 à Q4 et Q6 sont principalement calculés à partir des observations disponibles, sans application systématique des pondérations individuelles ni prise en compte complète du plan de sondage.

Ils décrivent donc les données analysées et ne doivent pas être interprétés directement comme des estimations nationales représentatives.

### Échantillons enfants et adultes

L'étude INCA 3 distingue les échantillons d'enfants et d'adultes.

Les comparaisons globales entre classes d'âge doivent être interprétées avec prudence.

### Analyse des contributions alimentaires

La pondération `R24_pond` intervient dans l'analyse Q5 par l'intermédiaire de `qte_conso_pond`.

Cette pondération des jours de rappel ne remplace pas les pondérations individuelles nécessaires à une analyse représentative de la population française.

### Interprétation nutritionnelle

Les analyses présentent des apports observés et des comparaisons descriptives. Elles ne constituent ni un diagnostic nutritionnel individuel ni une évaluation clinique.

## 9. Améliorations possibles

Les prolongements méthodologiques envisageables comprennent :

- L'intégration des pondérations individuelles adaptées aux populations étudiées.
- La prise en compte du plan de sondage complexe.
- Une analyse systématique des valeurs manquantes par variable.
- Des tests automatisés supplémentaires pour le calcul des contributions alimentaires.
- Une validation approfondie des unités et des correspondances entre variables nutritionnelles.

## 10. Références

- Anses — Étude INCA 3.
- Anses — Notice d'utilisation des données INCA 3.
- Documentation des variables et de la nomenclature INCA 3.
