from .logParser import parseSingleLine
from .detectSQLInjection import detectSQLInjection
from .detectBrutForce import detectBrutForce
from ..eventService import EventService
from ..alertService import AlertService
from ...models.fichier_log import FichierLog
from app import db
import json
import time
import os

def analyzeLogsForAttacks(fichierLogId, startPosition=None):
    """
    Analyse tous les logs, détecte les attaques et crée
    un Evenement pour chaque attaque associée à fichier_log_id.
    """
    fichier = FichierLog.query.get(fichierLogId)
    if not fichier:
        return [], 0

    # Si aucune position n'est spécifiée, utiliser la position sauvegardée
    if startPosition is None:
        startPosition = fichier.current_position or 0

    analyzedLines = []
    attackDetected = []

    
    with open(fichier.chemin, 'r') as f:
        f.seek(startPosition)
        newContent = f.read()
        newPosition = f.tell()
        
        parsedLogs = []
        eventsByIp = {}  # Pour grouper les événements par IP
        
        if newContent.strip():
            # Traiter seulement les nouvelles lignes
            for line in newContent.strip().split('\n'):
                parsedLog = parseSingleLine(line)  # Fonction helper
                if parsedLog:
                    parsedLogs.append(parsedLog)
                    
                    # Vérifie si c'est une tentative de brut force (401/403 ou login)
                    statusCode = str(parsedLog.get('status_code', ''))
                    url = parsedLog.get('url', '').lower()
                    isBruteForceAttempt = (statusCode in ['401', '403'] or 'login' in url)
                    
                    if isBruteForceAttempt:
                        ip = parsedLog['ip']
                        if ip not in eventsByIp:
                            eventsByIp[ip] = {
                                'count': 0,
                                'status_code': statusCode,
                                'url': parsedLog['url'],
                                'method': parsedLog['method']
                            }
                        eventsByIp[ip]['count'] += 1
                    else:
                        # Créer un événement normal pour les non-brute force
                        event = EventService.createEvent(
                            ipSource=parsedLog['ip'],
                            typeEvenement=parsedLog['method'],
                            fichierLogId=fichierLogId,
                            urlCible=parsedLog['url'],
                        )
                        analyzedLines.append(event)
                        
                        # Détection SQL injection
                        if detectSQLInjection(parsedLog['url']):
                            alert = AlertService.createAlerte(
                                ipSource=event['ip_source'],
                                typeEvenement='Injection SQL',
                                fichierLogId=fichierLogId,
                                statusCode=parsedLog['status_code'],
                                evenementId=event['evenement_id'],
                            )
                            attackDetected.append(alert)
                            print(json.dumps({
                                "type": "sqlInjection",
                                "data": {
                                    "ip": event['ip_source'],
                                    "date": parsedLog['date'],
                                    "heure": parsedLog['heure']
                                }
                            }), flush=True)

        # Créer un seul événement par IP pour les tentatives de brute force
        eventsByIpCreated = {}  # Pour stocker les événements créés par IP
        for ip, data in eventsByIp.items():
            event = EventService.createEvent(
                ipSource=ip,
                typeEvenement=f"{data['method']} ({data['count']} tentatives)",
                fichierLogId=fichierLogId,
                urlCible=data['url'],
            )
            analyzedLines.append(event)
            eventsByIpCreated[ip] = event  # Sauvegarder l'événement pour cette IP

        # Détection brut force après la boucle
        suspects = detectBrutForce(parsedLogs)
        for ip, nbAttempts in suspects:
            # Récupère le status code et l'événement de cette IP
            statusCode = eventsByIp.get(ip, {}).get('status_code', '401')
            urlCible = eventsByIp.get(ip, {}).get('url', '/login')
            evenementId = eventsByIpCreated.get(ip, {}).get('evenement_id', None)
            
            alert = AlertService.createAlerte(
                ipSource=ip,
                typeEvenement=f'Brut force ({nbAttempts} tentatives)',
                fichierLogId=fichierLogId,
                statusCode=statusCode,
                urlCible=urlCible,
                evenementId=evenementId,
            )
            attackDetected.append(alert)
            # Récupère la première tentative pour la date/heure
            firstAttempt = next((log for log in parsedLogs if log['ip'] == ip), {})
            print(json.dumps({
                "type": "brutForce",
                "data": {
                    "ip": ip,
                    "attempts": nbAttempts,
                    "date": firstAttempt.get('date', ''),
                    "heure": firstAttempt.get('heure', ''),
                    "statusCode": statusCode
                }
             }), flush=True)

    fichier.current_position = newPosition
    db.session.commit()

    return analyzedLines, newPosition, attackDetected


def analyzeLogsForAttacksSafe(fichierLogId, startPosition=0, forceFullAnalysis=False):
    """
    Analyse sécurisée avec reset automatique
    """
    fichier = FichierLog.query.get(fichierLogId)
    if not fichier:
        return [], 0

    # Force l'analyse complète si demandé
    if forceFullAnalysis:
        startPosition = 0
    
    # Validation basique de la position
    elif startPosition > 0:
        try:
            file_size = os.path.getsize(fichier.chemin)
            if startPosition > file_size:
                print(f"Position invalide. Reset automatique.")
                startPosition = 0
        except:
            startPosition = 0
    
    # Analyse normale
    return analyzeLogsForAttacks(fichierLogId, startPosition)


def continuousAnalysis(fichierLogId):
    """Analyse continue avec gestion des erreurs"""
    position = 0
    
    while True:
        try:
            attacks, newPosition, alerts = analyzeLogsForAttacksSafe(
                fichierLogId, 
                position
            )
            position = newPosition
            
            if attacks:
                print(f"{len(attacks)} nouveaux événements")
                
        except Exception as e:
            position = 0  # Reset en cas d'erreur
            
        time.sleep(5)  # Attendre 5 secondes
