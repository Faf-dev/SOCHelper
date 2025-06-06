CREATE TABLE "evenements" (
    "evenement_id" UUID NOT NULL UNIQUE,
    "ip_source" VARCHAR(15) NOT NULL,
    "type_evenement" VARCHAR(255) NOT NULL,
    "fichier_log_id" UUID,
    "created_at" TIMESTAMP NOT NULL,
    PRIMARY KEY("evenement_id")
);

CREATE TABLE "fichier_log" (
    "fichier_log_id" UUID NOT NULL UNIQUE,
    "chemin" TEXT NOT NULL,
    "type_log" VARCHAR NOT NULL,
    "analyse_en_temps_reel" BOOLEAN NOT NULL DEFAULT false,
    "add_at" DATE NOT NULL,
    "user_id" UUID NOT NULL,
    PRIMARY KEY("fichier_log_id")
);

CREATE TABLE "utilisateur" (
    "utilisateur_id" UUID NOT NULL UNIQUE,
    "email" VARCHAR(254) NOT NULL UNIQUE,
    "mot_de_passe" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP,
    PRIMARY KEY("utilisateur_id")
);

CREATE TABLE "alertes" (
    "alerte_id" UUID NOT NULL UNIQUE,
    "ip_source" VARCHAR(15) NOT NULL,
    "type_evenement" VARCHAR(255) NOT NULL,
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