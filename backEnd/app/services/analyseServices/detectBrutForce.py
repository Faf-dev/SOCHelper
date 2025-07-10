from collections import defaultdict
from datetime import datetime, timedelta
from ...models.evenement import Evenement
from app import db

# Cache global pour stocker les tentatives récentes par IP
recentAttemptsCache = defaultdict(list)

# Cache pour éviter les alertes répétées (IP -> timestamp de la dernière alerte)
alertCooldownCache = {}

# Cache pour éviter les événements répétés (IP -> timestamp du dernier événement brute force)
eventCooldownCache = {}

# Cache persistant pour compter TOUTES les tentatives par IP (jamais nettoyé automatiquement)
persistentAttemptsCache = defaultdict(list)

def detectBrutForce(parsedLog, windowSeconds=10, threshold=5, cooldownMinutes=5):
    """
    Détecte les tentatives de brut force pour une IP donnée
    Args:
        parsedLog: Log parsé (dict avec 'ip', 'date', 'heure', 'status_code', 'url')
        windowSeconds: Fenêtre de temps en secondes (défaut: 10)
        threshold: Nombre minimum de tentatives pour déclencher une alerte (défaut: 5)
        cooldownMinutes: Temps d'attente avant une nouvelle alerte pour la même IP (défaut: 5)
    Returns:
        bool: True si brute force détecté ET pas d'alerte récente, False sinon
    """
    if not parsedLog:
        return False
    
    ip = parsedLog.get('ip')
    statusCode = str(parsedLog.get('status_code', ''))
    url = parsedLog.get('url', '').lower()
    
    # Vérifie si c'est une tentative de connexion suspecte
    isLoginAttempt = (
        statusCode in ['401', '403', '404'] or 
        any(keyword in url for keyword in ['login', 'admin', 'auth', 'signin'])
    )
    
    if not isLoginAttempt:
        return False
    
    try:
        # Convertit la date et l'heure en datetime
        currentTime = datetime.strptime(
            f"{parsedLog['date']} {parsedLog['heure']}", 
            "%d/%b/%Y %H:%M:%S"
        )
        
        # Nettoie le cache des anciennes tentatives
        cutoffTime = currentTime - timedelta(seconds=windowSeconds)
        recentAttemptsCache[ip] = [
            attempt_time for attempt_time in recentAttemptsCache[ip] 
            if attempt_time > cutoffTime
        ]
        
        # Ajoute la tentative actuelle
        recentAttemptsCache[ip].append(currentTime)
        
        # Ajoute aussi dans le cache persistant (pour le comptage total)
        persistentAttemptsCache[ip].append(currentTime)
        
        # Vérifie si le seuil est atteint
        if len(recentAttemptsCache[ip]) >= threshold:
            # Vérifie si on peut envoyer une alerte (cooldown)
            lastAlert = alertCooldownCache.get(ip)
            if lastAlert is None or currentTime - lastAlert > timedelta(minutes=cooldownMinutes):
                # Enregistre le timestamp de cette alerte
                alertCooldownCache[ip] = currentTime
                return True
        
        return False
        
    except (ValueError, KeyError) as e:
        print(f"Erreur lors du parsing de la date: {e}")
        return False

def getAllBrutForceAttempts():
    """
    Retourne toutes les tentatives de brute force enregistrées dans le cache persistant
    Returns:
        dict: Dictionnaire avec IP comme clé et liste de timestamps comme valeur
    """
    return dict(persistentAttemptsCache)

def getBrutForceAttemptCount(ip):
    """
    Retourne le nombre de tentatives récentes pour une IP (dans la fenêtre de temps)
    Args:
        ip: Adresse IP
    Returns:
        int: Nombre de tentatives récentes
    """
    return len(recentAttemptsCache.get(ip, []))

def getBrutForceTotalAttemptCount(ip):
    """
    Retourne le nombre TOTAL de tentatives pour une IP (depuis le début)
    Args:
        ip: Adresse IP
    Returns:
        int: Nombre total de tentatives
    """
    return len(persistentAttemptsCache.get(ip, []))

def clearBrutForceCache():
    """
    Nettoie le cache des tentatives (utile pour les tests)
    """
    global recentAttemptsCache, alertCooldownCache, eventCooldownCache, persistentAttemptsCache
    recentAttemptsCache.clear()
    alertCooldownCache.clear()
    eventCooldownCache.clear()
    persistentAttemptsCache.clear()

def getLastAlertTime(ip):
    """
    Retourne le timestamp de la dernière alerte pour une IP
    Args:
        ip: Adresse IP
    Returns:
        datetime ou None: Timestamp de la dernière alerte
    """
    return alertCooldownCache.get(ip)

def shouldCreateBrutForceEvent(parsedLog, windowSeconds=10, threshold=1, cooldownMinutes=5):
    """
    Détermine si on doit créer un événement pour cette tentative de brute force
    Args:
        parsedLog: Log parsé (dict avec 'ip', 'date', 'heure', 'status_code', 'url')
        windowSeconds: Fenêtre de temps en secondes (défaut: 10)
        threshold: Nombre minimum de tentatives pour déclencher un événement (défaut: 1)
        cooldownMinutes: Temps d'attente avant un nouvel événement pour la même IP (défaut: 5)
    Returns:
        bool: True si on doit créer un événement, False sinon
    """
    if not parsedLog:
        return True
    
    ip = parsedLog.get('ip')
    statusCode = str(parsedLog.get('status_code', ''))
    url = parsedLog.get('url', '').lower()
    
    # Vérifie si c'est une tentative de connexion suspecte
    isLoginAttempt = (
        statusCode in ['401', '403', '404'] or 
        any(keyword in url for keyword in ['login', 'admin', 'auth', 'signin'])
    )
    
    if not isLoginAttempt:
        return True  # Créer l'événement normal (pas une tentative de brute force)
    
    # Pour les tentatives de brute force, vérifier le cooldown
    try:
        currentTime = datetime.strptime(
            f"{parsedLog['date']} {parsedLog['heure']}", 
            "%d/%b/%Y %H:%M:%S"
        )
        
        # Vérifier si cette IP a déjà un événement récent
        lastEvent = eventCooldownCache.get(ip)
        
        if lastEvent is None:
            # Première tentative pour cette IP, enregistrer et créer l'événement
            eventCooldownCache[ip] = currentTime
            return True
        
        # Vérifier si le cooldown est expiré
        if currentTime - lastEvent > timedelta(minutes=cooldownMinutes):
            # Cooldown expiré, permettre un nouvel événement
            eventCooldownCache[ip] = currentTime
            return True
        
        # Cooldown actif, pas d'événement
        return False
        
    except (ValueError, KeyError):
        return True  # En cas d'erreur, créer l'événement par défaut
