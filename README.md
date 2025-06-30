# 🛡️ SOC Helper - Outil d'analyse de logs

---

## 🚨 Problèmes connus

- Certain url raccourci n'affiche pas l'url complet au survol
- Les nouvelles entrée ne sont pas prise en compte par l'analyse
- Erreur 500 si tentative de suppression d'un evenement liée à une alerte (fonctionnel dans l'autre sens)
- Position qui change aléatoire lors de l'arret/reprise de l'analyse en temp réel.
- Doublon d'analyse
- deconnexion meme si actif
- changer de page désactive l'analyse
- Formulaire html Email/MDP bloqué ~1min après deconnexion
- Un token est toujours stocké dans localStorage (normalement SessionStorage)

---

## ✅ Ce qui est implémenté

- Ajout automatique du fichier sélectionné + le type de serveur dans l'en tête de l'application
- Limite de 5 tentative de connexion par minute et par IP
- Securité du mot de passe (8 caractères minimum, 1 majuscule, 1 minuscule, 1 chiffre, 1 caractère spécial)
- Securité de l'email (vérification de la syntaxe, pas d'espace, pas de caractère spécial)
- Logo
- image pour le login
- image pour le register
- redirection entre la page login/register
- redirection entre la page login/dashboard si connexion réussi
- Gestion de la création de l'utilisateur sur la page register (création en BDD, vérification d'existance)
- Gestion de la connexion de l'utilisateur sur la page login (recherche en BDD, vérification d'input correct pour l'email)
- Hachage du mot de passe
- HTML/CSS pour login et register
- Script JS pour login et register
- Route API pour login et register
- Message d'erreur, de réussite pour la connexion et l'inscription
- HTML/CSS pour le dashboard (hors éléments dynamique)
- les models de classes sont fait (version simplifié)
- Token JWT
- Déconnexion automatique si innactivité prolongé
- fonction du bouton "Déconnexion" du dashboard (pas de réel déconnexion en revanche)
- Menu de navigation du dashboard (sans les éléments dynamique)
- Email de l'utilisateur affiché dans l'en-tête
- import du fichier log (drag & drop ou chemin manuel)
- Choix du serveur (Nginx/Apache)
- Implémentation des éléments dynamique en HTML/CSS :
    - Pagination
    - Evenements
    - Alertes :
        - Toutes les alertes dans /alerts
    - Bouton vert ou rouge (analysé : oui/non)
    - Bouton start/stop du dashboard
    - Page "Paramètre" (gestion du fichiers log) et tout ce qui va avec : API, HTML/CSS ...
    - Ajouter des méthodes pour sécuriser la création/connexion de l'utilisateur

---

## 📝 Reste a faire

### ⚠️ IMPORTANT ⚠️
**Filtrer la récupération d'evenement et d'alerte en fonction des clés (actuellement : Récupère tout les evenements/alertes de la BDD)**
**Les nouvelles entrée ne sont pas prise en compte par l'analyse**
**Position à corriger (analyse)**

### Autres tâches
- Retirer Postgresql et mettre SQLite dans la doc
- Ajouter "alerte.status_code" dans le MPD
- Mettre les api.response dans settings.py (api)
- Fix la page settings.html (drag & drop et selection de fichier log)
- Changer la methode de stockage du limiter (actuel = ram, a faire : Redis, memcached, etc..)
- Implémentation des éléments dynamique en HTML/CSS :
    - Alertes :
        - Dernière alerte détecté dans /dashboard
- Détecter les brute force
- Ajouter un pop up lors d'attaque réussi ou dangereuses
- Ajouter "evenement.url_cible" dans le MPD

---

## 📅 Fait la semaine du 23/06

### 🔧 Général
#### ⚠️ Important ⚠️
**Changement de BDD : PostgreSQL -> SQLite (Justification du choix en bas du README.md)**

- Amélioration de la lisibilité du README.md
- Creation d'index en BDD pour retrouver des elements + rapidement (ex : `events = Evenement.query.filter_by(ip_source='203.0.113.45').all()` Sans index = 2 à 3 secondes, Avec index = 0,1 seconde)
- Modification du modele Alert :
  - Ajout d'une colonne "status_code" pour savoir si l'attaquant a échoué ou non.
- Suppression du fichier db.py (problème d'import et fichier inutile.)
- Fix des imports dans les tout les fichiers necessitant un accès a la db. (anciennement: `from .. import db`, maintenant: `from app import db`)

### 🎨 FrontEnd
- Adaptation de dashboard.html pour ajouter la colonne "METHODE HTTP"
- Adaptation de alert.html pour ajouter la colonne "CODE HTTP"

#### Script js

**getLogPath.js :**
- Récupère le chemin du fichier log et le type de serveur pour l'afficher dynamiquement à coté de l'utilisateur connecté dans l'en-tête.

**settings.js :**
- Stock l'ID du fichier dans le localStorage pour le récupérer dans dashboard.html (pas encore fait)
- Ajout de l'affichage des fichier log lié à l'utilisateur connecté
- Ajout d'un système de suppression des fichiers logs (les infos contenue en BDD)
- Ajout d'un systeme de sélection de fichier à analyser

**realtimeButton.js :**
- Ajout de la fonction triggerLogAnalysis qui lance l'analyse du fichier log en même temps que l'analyse de la BDD.

### ⚙️ BackEnd

**model/evenement.py :**
- Modification -> type_evenement stock désormais le code HTTP et non la tentative d'attaque effectuée.

**services/analyseServices :**
- Repertorie tout les fichiers lié à l'analyse du fichier access.log (parser, detecteur d'attaque, ...)

**services/analyseServices.py :**
- Logique métier pour la lecture du fichier log et la création d'événement et la création d'alertes a partir des résultats obtenues.

**services/settingsServices.py :**
- Ajout d'une méthode pour récuperer qu'un fichier log spécifique via son id
- Ajout de méthodes pour retrouver les fichier log lié a un utilisateur et une méthode pour la suppréssion.

**api/event.py :**
- Ajout de la route event/analyze pour lancer l'analyse et la création d'evenements.

**api/settings.py :**
- Ajout d'appel vers settingsService pour pouvoir supprimer un fichier log, et les retrouver pour eviter de devoir drag & drop a chaque fois

---


## 📅 Fait la semaine du 16/06

### 🎨 FrontEnd

#### Script js

**Général :**
- Récupère désormais le token dans sessionStorage (anciennement localStorage). Pourquoi sessionStorage ? : Les données stockées dans sessionStorage sont automatiquement supprimées lorsque l'onglet ou la fenêtre du navigateur est fermée, ce qui réduit les risques d'accès non autorisé
- Fix de la vérification du token : Redirige l'utilisateur vers login.html si le token n'est pas trouvé

**settings :**
- Modification du systeme de drag & drop : Utilisation de { dialog } (API d'Electron), permettant ainsi de récupérer le chemin absolu du fichier log fournis.

**main :**
- Ajout de ipcMain pour la gestion du drag & drop via { dialog }

**preload :**
- Sers d'intermediaire entre Electron et le backend pour le drag & drop (sinon Drag & Drop inutilisable)

**tokenManager :**
- Gère le renouvellement automatique du token si l'utilisateur est actif. Sinon, ne le renouvelle pas, supprime le token et redirige l'utilisateur vers login.html au bout de 30 minutes d'inactivité.

### ⚙️ BackEnd

**settingsService :**
- Vérifie si le fichier existe sur le système, vérifie l'extension `.log` et créer le modèle fichier_log en BDD (+ séparation des responsabilité des fonctions)

---


## 📅 Fait la semaine du 09/06

### 🎨 FrontEnd

#### Script js

**getAlertes :**
- Intègre les alertes de la BDD dans alertes.html

**getEvents :**
- Le bouton start/stop lance et stop l'analyse des évenements en BDD.
- Analyse toutes les 1 seconde pour récuperer les nouveaux evenements et les affiche.

**deleteHandler :**
- Implémenter dans dashboard.html et alertes.html : Gère l'envoie de donnée pour la suppression des evenements/alertes

**getEmail :**
- Affiche l'email de l'utilisateur connecté

**login :**
- Transmet les données vers l'API et redirige l'utlisateur vers dashboard.html

**logout :**
- Affiche un pop up lors du clic sur le boutton "Déconnexion" et demande a l'API de supprimer le token

**main :**
- Point d'entré pour electron

**pagination :**
- Pagination simple pour parcourir les evenements et les alertes

**realtimeButton :**
- Gestion du boutton Start/Stop -> Change dynamiquements les id du boutton et lance l'analyse des nouveaux evenements dans la BDD. (code potentiellement a déplacer dans ServiceAnalyse.py au futur)

**register :**
- Recupere et transmet les données a l'API pour la création d'un utilisateur puis redirige vers login.html

### ⚙️ BackEnd

#### API

**alert.py :**
- Route /api/alert:
  - Retourne les codes HTTP et les alertes retrouver par le back pour la pagination
- Route /api/alert/'<\alertId>':
  - Retrouve une alerte via son ID et gère les retour HTTP suivant la suppression de celle-ci

**auth.py :**
- Route /api/register:
  - Gère les retour HTTP suivant la réussite ou non de la création de l'utilisateur
- Route /api/login:
  - Gère les retour HTTP suivant la réussite ou non de la connexion d'un utlisateur
- Route /api/user:
  - Gère le retour HTTP suivant la réussite de la déconnexion (A fix peut etre)

**event.py :**
- Route /api/event:
  - Retourne les codes HTTP et les evenements retrouver par le back pour la pagination
- Route /api/event/'<\eventId>':
  - Retrouve un evenement via son ID et gère les retour HTTP suivant la suppression de celle-ci

**settings.py :**
- Route /api/settings:
  - Envoie les données au back et renvoie les code HTTP en fonction des infos récupéré

#### Services

**alertServices :**
- Contient toute la logique metier liés aux alertes

**authServices :**
- Contient toute la logique metier liés à la connexion et a la création d'un utilisateur

**eventServices :**
- Contient toute la logique metier liés aux evenements

**settingsServices :**
- Contient toute la logique metier liés au fichier log (import, recuperation du path etc...)

#### Général
- Recuperation des bons elements a afficher.
- Limite de 5 tentatives de connexion par minute et par IP
- Limite de 10 créations d'utilisateurs par minute et par IP
- Securité du mot de passe (8 caractères minimum, 1 majuscule, 1 minuscule, 1 chiffre, 1 caractère spécial)
- Securité de l'email (vérification de la syntaxe, pas d'espace, pas de caractère spécial)
- Créer un modèle fichier_log dans la base de donnée en transmettant son fichier access.log via drag & drop (A fix)

#### Modification du script SQL
- Type varchar(15) modifié en INET pour stocker une IP → validation automatique des IPs, support IPv6, et opérations réseau natives (vérification d'IPs pour détecter les attaques depuis un même réseau)
- Creation de quelques modèles en BDD pour travailler sur la recuperation des données.

### ⚠️ Point compliqué semaine du 09/06

**Etienne :**
- Pop-up: "J'arrive a l'afficher, mais je n'arrive pas a l'afficher directement à la création d'une alerte"

**Julien :**
- Résolution de conflit pour la pagination et l'analyse en temps réel.

---


## 📚 Justification des choix

### PostgreSQL vs SQLite

#### 🔐 Gestion des droits d'accès
- **Problème** : Dans une entreprise, tout le monde ne doit pas avoir les mêmes permissions
- **Solution PostgreSQL** : On peut créer des "profils" (admin peut tout faire, analyste peut seulement consulter)
- **Exemple concret** : L'analyste junior ne peut pas supprimer les alertes importantes, mais le chef d'équipe oui

#### 📝 Audit Trail (traçabilité)
- **Problème** : En cas d'incident, on doit savoir qui a fait quoi
- **Solution PostgreSQL** : Enregistrement automatique de toutes les actions
- **Exemple concret** : "john@doe.com a supprimé 5 alertes SQLi le 05/06/2025 à 14h30" → obligation légale en cybersécurité

#### 👥 Connexions simultanées
- **Problème SQLite** : Comme un fichier Word, une seule personne peut modifier à la fois
- **Solution PostgreSQL** : Comme Google Docs, plusieurs personnes peuvent travailler ensemble
- **Exemple concret** : 3 analystes de l'équipe de nuit peuvent utiliser l'outil en même temps

#### ⚡ Connexions persistantes
- **Problème SQLite** : L'application doit "rouvrir le fichier" à chaque action (lent)
- **Solution PostgreSQL** : Connexion maintenue ouverte (rapide)
- **Exemple concret** : Temps de réponse < 100ms pour afficher les alertes vs plusieurs secondes

#### 📈 Performance et évolutivité
- **PostgreSQL** : Conçu pour gérer des millions d'événements de sécurité
- **SQLite** : Limité à quelques milliers d'enregistrements avant ralentissement
- **Exemple concret** : Une entreprise génère 50 000 événements/jour → PostgreSQL reste fluide

### 🔄 Changement PostgreSQL -> SQLite, pourquoi ?

- Simplification du déploiement
- Pas de serveur PostgreSQL à installer chez l'utilisateur
- Compilation en .exe beaucoup plus simple
- Base de données "portable" incluse dans l'app
- Acceptable niveau stockage (Événement typique : ~200 octets, Alerte typique : ~150 octets. Donc pour 1 million d'événements + alertes : (200 + 150) × 1,000,000 = 350 MB)