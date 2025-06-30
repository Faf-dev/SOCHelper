-- Table utilisateur
CREATE TABLE "utilisateur" (
    "utilisateur_id" VARCHAR(36) PRIMARY KEY,
    "email" VARCHAR(254) NOT NULL UNIQUE,
    "mot_de_passe" VARCHAR(255) NOT NULL,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME
);

-- Table fichier_log
CREATE TABLE "fichier_log" (
    "fichier_log_id" VARCHAR(36) PRIMARY KEY,
    "chemin" TEXT NOT NULL,
    "type_log" VARCHAR(50) NOT NULL,
    "analyse_en_temps_reel" BOOLEAN NOT NULL DEFAULT 0,
    "add_at" DATE DEFAULT CURRENT_DATE,
    "user_id" VARCHAR(36) NOT NULL,
    FOREIGN KEY("user_id") REFERENCES "utilisateur"("utilisateur_id") ON DELETE CASCADE
);

-- Table evenements
CREATE TABLE "evenements" (
    "evenement_id" VARCHAR(36) PRIMARY KEY,
    "ip_source" VARCHAR(45) NOT NULL, -- Support IPv6
    "type_evenement" VARCHAR(255) NOT NULL,
    "fichier_log_id" VARCHAR(36),
    "url_cible" TEXT,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY("fichier_log_id") REFERENCES "fichier_log"("fichier_log_id") ON DELETE SET NULL
);

-- Table alertes
CREATE TABLE "alertes" (
    "alerte_id" VARCHAR(36) PRIMARY KEY,
    "ip_source" VARCHAR(45) NOT NULL, -- Support IPv6
    "type_evenement" VARCHAR(255) NOT NULL,
    "status_code" INTEGER,
    "evenement_id" VARCHAR(36) NOT NULL,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY("evenement_id") REFERENCES "evenements"("evenement_id")
);

-- Index pour les performances
CREATE INDEX idx_evenements_ip_source ON evenements(ip_source);
CREATE INDEX idx_evenements_type ON evenements(type_evenement);
CREATE INDEX idx_evenements_created_at ON evenements(created_at);
CREATE INDEX idx_alertes_ip_source ON alertes(ip_source);
CREATE INDEX idx_alertes_created_at ON alertes(created_at);

-- Données de test
INSERT INTO "utilisateur" (utilisateur_id, email, mot_de_passe, created_at)
VALUES (
    lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))),
    'user@test.com',
    'pbkdf2:sha256:260000$JsP7Y6YOM0h6Ff8m$8c2ee374eeaf7b51d0187e22ceebc36130711e70172c5f75e03563d0b9c2d939',
    datetime('now')
);

-- Insertion dans fichier_log
INSERT INTO "fichier_log" (fichier_log_id, chemin, type_log, analyse_en_temps_reel, add_at, user_id)
VALUES (
    lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))),
    '/var/log/apache2/access.log',
    'apache',
    0,
    date('now'),
    (SELECT utilisateur_id FROM "utilisateur" WHERE email = 'user@test.com')
);

-- Insertion d'événements de test
INSERT INTO "evenements" (evenement_id, ip_source, type_evenement, fichier_log_id, url_cible, created_at)
VALUES 
    (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))),
    '192.168.1.100',
    'SQLi',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/login',
    datetime('now')
    ),
    (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))),
    '192.168.1.101',
    'Brut force',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/admin',
    datetime('now')
    ),
    (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))),
    '10.0.0.5',
    'SQLi',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/api/users',
    datetime('now')
    );

-- Insertion d'alertes de test
INSERT INTO "alertes" (alerte_id, ip_source, type_evenement, status_code, evenement_id, created_at)
SELECT 
    lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))),
    e.ip_source,
    e.type_evenement,
    CASE 
        WHEN e.ip_source = '192.168.1.100' THEN 401
        WHEN e.ip_source = '192.168.1.101' THEN 403
        ELSE 200
    END,
    e.evenement_id,
    datetime('now')
FROM evenements e;
