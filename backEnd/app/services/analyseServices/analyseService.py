from .logParser import parseSingleLine
from .detectSQLInjection import detectSQLInjection
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
        
        if newContent.strip():
            # Traiter seulement les nouvelles lignes
            for line in newContent.strip().split('\n'):
                parsedLog = parseSingleLine(line)  # Fonction helper
                if parsedLog:
                    event = EventService.createEvent(
                        ip_source=parsedLog['ip'],
                        type_evenement=parsedLog['method'],
                        fichier_log_id=fichierLogId,
                        url_cible=parsedLog['url'],
                    )
                    if detectSQLInjection(parsedLog['url']):
                        alert = AlertService.createAlerte(
                            ip_source=event['ip_source'],
                            type_evenement='Injection SQL',
                            fichier_log_id=fichierLogId,
                            status_code=parsedLog['status_code'],
                            evenement_id=event['evenement_id'],
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
                        print(f"DEBUG: IP envoyée = '{event['ip_source']}'", flush=True)
                    time.sleep(1)

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
