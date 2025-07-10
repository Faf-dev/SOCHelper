from collections import defaultdict
from datetime import datetime, timedelta

def detectBrutForce(events, windowSeconds=60, threshold=5):
    """
    Détecte les tentatives de brut force et retourne les IPs suspectes avec le nombre de tentatives
    Args:
        events: Liste des événements parsés (avec 'ip', 'date', 'heure', 'status_code', 'url')
        windowSeconds: Fenêtre de temps en secondes (défaut: 60)
        threshold: Nombre minimum de tentatives pour déclencher une alerte (défaut: 5)
    Returns:
        Liste de tuples (ip, nombre_tentatives)
    """
    # Groupe les tentatives par IP
    attemptsByIp = defaultdict(list)
    
    for event in events:
        # Vérifie si c'est une tentative de connexion échouée
        statusCode = str(event.get('status_code', ''))
        url = event.get('url', '').lower()
        
        if (statusCode in ['401', '403'] or 'login' in url):
            try:
                # Convertit la date et l'heure en datetime
                dt = datetime.strptime(
                    f"{event['date']} {event['heure']}", 
                    "%d/%b/%Y %H:%M:%S"
                )
                attemptsByIp[event['ip']].append((dt, statusCode))
            except (ValueError, KeyError):
                continue

    # Détecte les brut forces
    suspiciousIps = []
    
    for ip, attempts in attemptsByIp.items():
        if len(attempts) >= threshold:
            # Trie par timestamp
            attempts.sort(key=lambda x: x[0])
            
            # Vérifie s'il y a 'threshold' tentatives dans la fenêtre de temps
            for i in range(len(attempts) - threshold + 1):
                timeDiff = attempts[i + threshold - 1][0] - attempts[i][0]
                if timeDiff <= timedelta(seconds=windowSeconds):
                    # Brut force détecté - ajoute une seule fois cette IP
                    suspiciousIps.append((ip, len(attempts)))
                    break
    
    return suspiciousIps
