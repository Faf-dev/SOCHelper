CREATE TABLE "evenements" (
    "evenement_id" UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    "ip_source" INET NOT NULL,
    "type_evenement" VARCHAR(255) NOT NULL,
    "fichier_log_id" UUID,
    "url_cible" TEXT,
    "created_at" TIMESTAMP NOT NULL,
    PRIMARY KEY("evenement_id")
);

CREATE TABLE "fichier_log" (
    "fichier_log_id" UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    "chemin" TEXT NOT NULL,
    "type_log" VARCHAR NOT NULL,
    "analyse_en_temps_reel" BOOLEAN NOT NULL DEFAULT false,
    "add_at" DATE NOT NULL,
    "user_id" UUID NOT NULL,
    PRIMARY KEY("fichier_log_id")
);

CREATE TABLE "utilisateur" (
    "utilisateur_id" UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    "email" VARCHAR(254) NOT NULL UNIQUE,
    "mot_de_passe" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP,
    PRIMARY KEY("utilisateur_id")
);

CREATE TABLE "alertes" (
    "alerte_id" UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    "ip_source" INET NOT NULL,
    "type_evenement" VARCHAR(255) NOT NULL,
    "status_code" INTEGER,
    "evenement_id" UUID NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    PRIMARY KEY("alerte_id")
);

ALTER TABLE "evenements"
ADD FOREIGN KEY("fichier_log_id") REFERENCES "fichier_log"("fichier_log_id")
ON UPDATE NO ACTION ON DELETE SET NULL;

ALTER TABLE "fichier_log"
ADD FOREIGN KEY("user_id") REFERENCES "utilisateur"("utilisateur_id")
ON UPDATE NO ACTION ON DELETE CASCADE;

ALTER TABLE "alertes"
ADD FOREIGN KEY("evenement_id") REFERENCES "evenements"("evenement_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;


-- Insertion d'un utilisateur
INSERT INTO "utilisateur" (utilisateur_id, email, mot_de_passe, created_at)
VALUES (
    gen_random_uuid(),
    'user@test.com',
    'pbkdf2:sha256:260000$JsP7Y6YOM0h6Ff8m$8c2ee374eeaf7b51d0187e22ceebc36130711e70172c5f75e03563d0b9c2d939', -- équivalent à 'test' en scrypt (werkzeug.security)
    NOW()
);

-- Insertion dans fichier_log en utilisant l'email pour récupérer l'UUID
INSERT INTO "fichier_log" (fichier_log_id, chemin, type_log, analyse_en_temps_reel, add_at, user_id)
VALUES (
    gen_random_uuid(),
    '/var/log/apache2/access.log',
    'apache',
    false,
    NOW(),
    (SELECT utilisateur_id FROM "utilisateur" WHERE email = 'user@test.com')
);

-- Insertion de plusieurs événements
INSERT INTO "evenements" (evenement_id, ip_source, type_evenement, fichier_log_id, url_cible, created_at)
VALUES 
    (gen_random_uuid(),
    '192.168.1.100',
    'SQLi',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/login',
    NOW()
    ),
    (gen_random_uuid(),
    '192.168.1.101',
    'Brut force',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/admin',
    NOW()
    ),
    (gen_random_uuid(),
    '10.0.0.5',
    'SQLi',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/api/users',
    NOW()
    ),
    (gen_random_uuid(),
    '172.16.0.10',
    'SQLi',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/api/delete',
    NOW()
    ),
    (gen_random_uuid(),
    '192.168.1.100',
    'Brut force',
    (SELECT fichier_log_id FROM "fichier_log" WHERE chemin = '/var/log/apache2/access.log'),
    'https://example.com/sensitive',
    NOW()
    );

-- Insertion de plusieurs alertes
INSERT INTO "alertes" (alerte_id, ip_source, type_evenement, status_code, evenement_id, created_at)
VALUES 
    (gen_random_uuid(),
    '192.168.1.100',
    (SELECT type_evenement FROM "evenements"
    WHERE ip_source = '192.168.1.100' AND url_cible = 'https://example.com/login' LIMIT 1),
    401,
    (SELECT evenement_id FROM "evenements"
    WHERE ip_source = '192.168.1.100' AND url_cible = 'https://example.com/login' LIMIT 1),
    NOW()
    ),
    (gen_random_uuid(),
    '192.168.1.101',
    (SELECT type_evenement FROM "evenements" 
    WHERE ip_source = '192.168.1.101' LIMIT 1),
    403,
    (SELECT evenement_id FROM "evenements"
    WHERE ip_source = '192.168.1.101' LIMIT 1),
    NOW()),
    (gen_random_uuid(),
    '10.0.0.5',
    (SELECT type_evenement FROM "evenements"
    WHERE ip_source = '10.0.0.5' LIMIT 1),
    200,
    (SELECT evenement_id FROM "evenements"
    WHERE ip_source = '10.0.0.5' LIMIT 1),
    NOW()
    ),
    (gen_random_uuid(),
    '172.16.0.10',
    (SELECT type_evenement FROM "evenements"
    WHERE ip_source = '172.16.0.10' LIMIT 1),
    500,
    (SELECT evenement_id FROM "evenements"
    WHERE ip_source = '172.16.0.10' LIMIT 1),
    NOW()
    ),
    (gen_random_uuid(),
    '192.168.1.100',
    (SELECT type_evenement FROM "evenements"
    WHERE ip_source = '192.168.1.100' AND url_cible = 'https://example.com/sensitive' LIMIT 1),
    404,
    (SELECT evenement_id FROM "evenements"
    WHERE ip_source = '192.168.1.100' AND url_cible = 'https://example.com/sensitive' LIMIT 1),
    NOW());
