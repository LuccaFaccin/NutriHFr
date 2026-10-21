# NutriHFr — Analyse des consommations alimentaires et des apports nutritionnels

## 1. Présentation

**NutriHFr** est un projet académique de science des données appliquée à la nutrition humaine, réalisé dans le cadre du parcours IODAA d'AgroParisTech.

Le projet exploite les données de l'étude française **INCA 3** (Étude individuelle nationale des consommations alimentaires), publiée par l'Anses, afin d'explorer les consommations alimentaires, les apports nutritionnels et leur variabilité selon différentes caractéristiques individuelles.

L'application repose sur Python, une base de données relationnelle SQLite, des analyses statistiques et un tableau de bord interactif Streamlit.

## 2. Objectifs

Le projet vise à :

- Structurer des données nutritionnelles dans une base relationnelle.
- Exploiter les données avec Python et SQL.
- Mettre en œuvre des classes Python selon les principes de la programmation orientée objet.
- Réaliser six analyses descriptives des apports nutritionnels.
- Visualiser les résultats dans un tableau de bord interactif.
- Vérifier le fonctionnement du code à l'aide de tests automatisés.
- Documenter une procédure de reconstruction reproductible de la base.

## 3. Sources des données

Les données proviennent de l'étude **INCA 3**, réalisée par l'Agence nationale de sécurité sanitaire de l'alimentation, de l'environnement et du travail (Anses).

Trois fichiers CSV sont utilisés :

| Fichier | Contenu | Nombre de lignes |
|---|---|---:|
| `description-indiv.csv` | Caractéristiques des individus | 5 855 |
| `apports-nut-alim.csv` | Apports nutritionnels individuels | 4 114 |
| `conso-compo-alim-vf-mad-datagouv2021.csv` | Consommations alimentaires et composition nutritionnelle | 256 301 |

Les fichiers originaux sont conservés sans modification.

Les documents méthodologiques de l'INCA 3 sont disponibles dans le répertoire `docs/`.

**Important :** les données brutes et la base SQLite ne sont pas versionnées sur GitHub. Leur présence est nécessaire pour reproduire les analyses.

## 4. Technologies utilisées

- Python
- pandas et NumPy
- SQLite et SQL
- Programmation orientée objet
- JupyterLab
- matplotlib
- Streamlit
- pytest
- Git et GitHub

## 5. Organisation du projet

```text
NutriHFr/
├── app.py
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   └── inca3/
│   └── processed/
├── docs/
├── notebooks/
│   └── 01_exploration_inca3.ipynb
├── reports/
│   └── figures/
├── sql/
│   ├── schema.sql
│   └── requetes.sql
├── src/
│   ├── __init__.py
│   ├── base_donnees.py
│   ├── analyse_nutritionnelle.py
│   └── construction_base.py
└── tests/
    └── test_analyses.py
```

## 6. Installation

### 6.1. Récupérer le projet

```bash
git clone https://github.com/LuccaFaccin/NutriHFr.git
cd NutriHFr
```

### 6.2. Créer un environnement Python

Il est recommandé d'utiliser un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate
```

Sous Windows, l'activation peut être réalisée avec :

```powershell
.venv\Scripts\Activate.ps1
```

### 6.3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

## 7. Préparation et reconstruction de la base de données

### 7.1. Ajouter les fichiers CSV

Placer les trois fichiers originaux INCA 3 dans :

```text
data/raw/inca3/
```

Les noms attendus sont :

```text
description-indiv.csv
apports-nut-alim.csv
conso-compo-alim-vf-mad-datagouv2021.csv
```

### 7.2. Construire la base SQLite

Depuis la racine du projet :

```bash
python -m src.construction_base --output data/processed/nutrihfr.db
```

Le script :

1. Vérifie la présence des fichiers sources.
2. Importe les données CSV par blocs.
3. Construit les tables `individus`, `apports` et `consommations`.
4. Conserve les colonnes disponibles dans les fichiers sources.
5. Définit les clés primaires et les relations entre les tables.
6. Vérifie les effectifs et l'intégrité référentielle.

**Sécurité :** le script refuse d'écraser un fichier SQLite existant.

Pour créer une seconde base de vérification sans modifier la base principale :

```bash
python -m src.construction_base --output data/processed/nutrihfr_test.db
```

### 7.3. Schéma relationnel

La base comprend trois tables principales :

- `individus` : une ligne par individu, identifiée par `NOIND`.
- `apports` : apports nutritionnels individuels, reliés à `individus` par `NOIND`.
- `consommations` : enregistrements alimentaires, identifiés par `NUM_LIGNE` et reliés à `individus` par `NOIND`.

Le fichier `sql/schema.sql` présente une **version simplifiée et illustrative** du schéma relationnel. Il ne permet pas, à lui seul, de reconstruire toutes les colonnes nécessaires aux analyses.

**Le script `src/construction_base.py` constitue la référence pour la création de la base complète.**

## 8. Exécuter le tableau de bord

Depuis la racine du projet :

```bash
python -m streamlit run app.py
```

L'application est ensuite accessible dans le navigateur à l'adresse locale indiquée par Streamlit, généralement :

```text
http://localhost:8501
```

Le tableau de bord permet d'explorer les six analyses nutritionnelles.

## 9. Analyses réalisées

### Q1 — Distribution des apports énergétiques

Analyse descriptive des apports énergétiques journaliers : effectifs, moyenne, médiane, dispersion et distribution.

### Q2 — Comparaison selon le sexe

Comparaison des apports énergétiques et protéiques entre les groupes codés « Homme » et « Femme » dans les données.

### Q3 — Énergie selon les classes d'âge

Étude de la variation des apports énergétiques moyens entre les neuf classes d'âge disponibles.

### Q4 — Densité nutritionnelle

Calcul de la densité protéique exprimée en grammes de protéines pour 1 000 kcal, avec exclusion des apports énergétiques nuls pour ce calcul.

### Q5 — Principaux aliments contributeurs

Identification des aliments contribuant le plus aux apports en protéines, calcium, fer, fibres et vitamine C.

Les apports sont estimés à partir des quantités consommées pondérées (`qte_conso_pond`) et des teneurs nutritionnelles pour 100 g :

**Apport estimé = quantité pondérée × teneur nutritionnelle / 100**

La variable `qte_conso_pond` intègre la pondération `R24_pond`, liée au type de jour de rappel alimentaire.

### Q6 — Variabilité dans une sous-population

Étude de la variabilité des apports énergétiques et protéiques chez les femmes âgées de 18 à 44 ans, avec calcul de statistiques descriptives et du coefficient de variation.

## 10. Notebook et figures

Le notebook principal est :

```text
notebooks/01_exploration_inca3.ipynb
```

Pour ouvrir JupyterLab :

```bash
jupyter lab
```

Les visualisations exportées sont enregistrées dans :

```text
reports/figures/
```

## 11. Programmation orientée objet

Le projet contient notamment :

- `BaseDonnees` dans `src/base_donnees.py` : connexion à SQLite, exécution de requêtes et extraction de statistiques.
- `AnalyseNutritionnelle` dans `src/analyse_nutritionnelle.py` : méthodes d'analyse des apports énergétiques, protéiques et de la densité nutritionnelle.

Ces classes séparent l'accès aux données des traitements analytiques.

## 12. Tests automatisés

Pour exécuter les tests :

```bash
python -m pytest -q
```

Les tests existants vérifient plusieurs opérations d'accès à la base et d'analyse nutritionnelle à l'aide d'une base SQLite temporaire.

Le dernier contrôle effectué a donné :

```text
9 passed
```

## 13. Limites méthodologiques

Les résultats présentés sont principalement des **statistiques descriptives exploratoires**.

Les estimations individuelles des analyses Q1 à Q4 et Q6 ne prennent pas systématiquement en compte les poids de sondage individuels ni le plan de sondage complexe de l'étude INCA 3.

Pour Q5, la pondération des jours de rappel alimentaire est intégrée dans les quantités consommées pondérées, mais cela ne remplace pas l'ensemble des ajustements nécessaires à une estimation représentative de la population française.

De plus, les échantillons d'enfants et d'adultes de l'étude INCA 3 ont été constitués séparément. Les comparaisons globales entre classes d'âge doivent donc être interprétées avec prudence.

**Les résultats ne doivent pas être présentés comme des estimations nationales représentatives.**

## 14. Références

- Anses — Étude individuelle nationale des consommations alimentaires 3 (INCA 3).
- Anses — Notice d'utilisation des données INCA 3, version diffusée sur data.gouv.fr.
- Documentation de la nomenclature et des variables INCA 3, disponible dans `docs/`.

## 15. Auteur et cadre académique

Projet académique réalisé dans le cadre du parcours IODAA — AgroParisTech, année universitaire 2026–2027.
