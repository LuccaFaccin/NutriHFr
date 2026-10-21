# Dictionnaire des données — NutriHFr

## 1. Présentation

Ce document décrit la structure de la base relationnelle SQLite utilisée dans le projet NutriHFr.

Les données proviennent de l'étude INCA 3 de l'Anses. La base contient trois tables principales : `individus`, `apports` et `consommations`.

Les colonnes originales des fichiers CSV sont conservées lors de la construction de la base. Ce dictionnaire présente les variables principales utilisées dans les analyses et ne constitue pas une description exhaustive de toutes les colonnes disponibles.

## 2. Structure relationnelle

| Table | Clé primaire | Nombre de lignes | Description |
|---|---|---:|---|
| `individus` | `NOIND` | 5 855 | Caractéristiques individuelles |
| `apports` | `NOIND` | 4 114 | Apports nutritionnels individuels |
| `consommations` | `NUM_LIGNE` | 256 301 | Enregistrements de consommation alimentaire |

### Relations entre les tables

- `individus.NOIND` → `apports.NOIND` : relation un-à-zéro-ou-un.
- `individus.NOIND` → `consommations.NOIND` : relation un-à-plusieurs.
- Chaque enregistrement de consommation est associé à un individu identifié par `NOIND`.

## 3. Table `individus`

| Variable | Description | Utilisation |
|---|---|---|
| `NOIND` | Identifiant unique de l'individu | Clé primaire et jointures |
| `sex_PS` | Sexe codé de l'individu : 1 = homme ; 2 = femme | Analyse Q2 et Q4 |
| `tage_PS` | Classe d'âge codée de 1 à 9 | Analyses Q3 et Q6 |
| `pop3` | Variable de population issue du fichier source | Caractérisation de l'échantillon |
| `pond_indiv_adu_pop3` | Pondération individuelle associée à la population adulte | Analyse méthodologique |
| `pond_indiv_enf_pop3` | Pondération individuelle associée à la population enfant | Analyse méthodologique |

### Classes d'âge `tage_PS`

| Code | Classe d'âge |
|---|---|
| 1 | 0 à 11 mois |
| 2 | 1 à 3 ans |
| 3 | 4 à 6 ans |
| 4 | 7 à 10 ans |
| 5 | 11 à 14 ans |
| 6 | 15 à 17 ans |
| 7 | 18 à 44 ans |
| 8 | 45 à 64 ans |
| 9 | 65 à 79 ans |

## 4. Table `apports`

| Variable | Description | Unité ou utilisation |
|---|---|---|
| `NOIND` | Identifiant de l'individu | Clé primaire et clé étrangère |
| `nutriment1` | Apport énergétique | kcal/jour |
| `nutriment3` | Apport protéique | g/jour |

Les apports nutritionnels sont utilisés pour calculer les statistiques descriptives, les comparaisons entre groupes et les indicateurs de variabilité.

La densité protéique est calculée comme suit :

**Densité protéique (g/1 000 kcal) = apport protéique (g/j) / apport énergétique (kcal/j) × 1 000**

Les observations dont l'apport énergétique est nul sont exclues de ce calcul afin d'éviter une division par zéro.

## 5. Table `consommations`

| Variable | Description | Utilisation |
|---|---|---|
| `NUM_LIGNE` | Identifiant unique de l'enregistrement alimentaire | Clé primaire |
| `NOIND` | Identifiant de l'individu | Clé étrangère |
| `aliment_code_INCA3` | Code de l'aliment selon la nomenclature INCA 3 | Regroupement des aliments |
| `aliment_libelle_INCA3` | Libellé de l'aliment | Affichage des résultats |
| `qte_conso` | Quantité consommée avant pondération des jours de rappel | Données de consommation |
| `qte_conso_pond` | Quantité consommée intégrant la pondération des jours de rappel | Analyse Q5 |
| `R24_pond` | Coefficient de pondération associé au type de jour de rappel de 24 heures | Documentation méthodologique |
| `proteines` | Teneur en protéines de l'aliment | Analyse Q5 |
| `calcium` | Teneur en calcium de l'aliment | Analyse Q5 |
| `fer` | Teneur en fer de l'aliment | Analyse Q5 |
| `fibres` | Teneur en fibres de l'aliment | Analyse Q5 |
| `vitamine_c` | Teneur en vitamine C de l'aliment | Analyse Q5 |

Les teneurs nutritionnelles utilisées dans Q5 sont rapportées à 100 g d'aliment.

### Calcul des contributions nutritionnelles

Pour chaque enregistrement alimentaire :

**Apport estimé = qte_conso_pond × teneur nutritionnelle / 100**

Les apports estimés sont ensuite additionnés par aliment.

La contribution relative d'un aliment est calculée selon :

**Contribution (%) = apport estimé de l'aliment / somme des apports estimés de tous les aliments × 100**

## 6. Contrôles de cohérence

Les contrôles réalisés lors de la construction de la base comprennent :

- Vérification de la présence des fichiers sources.
- Contrôle des clés primaires.
- Vérification des relations entre les tables.
- Comparaison des effectifs attendus et obtenus.
- Vérification de l'intégrité référentielle SQLite.

La reconstruction a été comparée à la base initiale pour les effectifs et certains indicateurs nutritionnels.

## 7. Limites et précautions

Les statistiques individuelles du projet sont principalement descriptives et ne tiennent pas systématiquement compte des poids individuels ni du plan de sondage complexe INCA 3.

La pondération `R24_pond` corrige la répartition des jours de rappel alimentaire, mais ne suffit pas à garantir la représentativité nationale des résultats.

Les populations enfant et adulte doivent être distinguées pour toute interprétation à l'échelle de la population française.

## 8. Références

- Anses — Étude INCA 3.
- Anses — Notice d'utilisation des données INCA 3.
- Documentation de la nomenclature INCA 3, conservée dans le répertoire `docs/`.
