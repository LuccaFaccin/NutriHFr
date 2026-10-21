-- Création de la table des individus
CREATE TABLE IF NOT EXISTS individus (
    NOIND INTEGER PRIMARY KEY,
    sex_PS INTEGER,
    tage_PS INTEGER,
    pop3 INTEGER,
    pond_indiv_adu_pop3 REAL,
    pond_indiv_enf_pop3 REAL,
    bmr_kcal REAL,
    sousest0 REAL
);

-- Création de la table des apports nutritionnels
CREATE TABLE IF NOT EXISTS apports (
    NOIND INTEGER PRIMARY KEY,
    POPULATION TEXT,
    nutriment1 REAL,
    nutriment2 REAL,
    nutriment3 REAL,
    FOREIGN KEY (NOIND) REFERENCES individus(NOIND)
);

-- Création de la table des consommations alimentaires
CREATE TABLE IF NOT EXISTS consommations (
    NUM_LIGNE INTEGER PRIMARY KEY,
    NOIND INTEGER NOT NULL,
    FOREIGN KEY (NOIND) REFERENCES individus(NOIND)
);

-- Index pour accélérer les jointures
CREATE INDEX IF NOT EXISTS idx_consommations_noind
ON consommations(NOIND);