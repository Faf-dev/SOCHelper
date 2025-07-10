from .logParser import parseSingleLine
from .detectSQLInjection import detectSQLInjection
from .detectBrutForce import detectBrutForce, getBrutForceTotalAttemptCount, shouldCreateBrutForceEvent
from ..eventService import EventService
from ..alertService import AlertService
from ...models.fichier_log import FichierLog
from app import db
import json
import os

def analyzeLogsForAttacks(fichierLogId, startPosition=None):
    """
    Analyse tous les logs, détecte les attaques et crée
    un Evenement pour chaque attaque associée à fichier_log_id.
    """
    fichier = FichierLog.query.get(fichierLogId)
    if not fichier:
        return [], 0, []

    # Si aucune position n'est spécifiée, utiliser la position sauvegardée
    if startPosition is None:
        startPosition = fichier.current_position or 0

    analyzedLines = []
    attackDetected = []
    
    # Vérifier que le fichier existe
    if not os.path.exists(fichier.chemin):
        print(f"Fichier non trouvé: {fichier.chemin}")
        return [], startPosition, []

    try:
        with open(fichier.chemin, 'r', encoding='utf-8') as f:
            # Aller à la position actuelle
            f.seek(startPosition)
            newContent = f.read()
            newPosition = f.tell()
            
            if not newContent.strip():
                # Pas de nouveau contenu
                return [], startPosition, []
            
            # Normaliser les fins de ligne pour être compatible Windows/Linux
            # et traiter seulement les nouvelles lignes
            normalizedContent = newContent.replace('\r\n', '\n').replace('\r', '\n')
            lines = [line.strip() for line in normalizedContent.strip().split('\n') if line.strip()]
            
            print(f"Analyse de {len(lines)} nouvelles lignes depuis position {startPosition}")
            
            for line_num, line in enumerate(lines, 1):
                    
                parsedLog = parseSingleLine(line)
                if parsedLog:
                    print(f"Parsing OK: {parsedLog['ip']} {parsedLog['method']} {parsedLog['url']}")
                    
                    if shouldCreateBrutForceEvent(parsedLog) | detectSQLInjection(parsedLog['url']):
                        event = EventService.createEvent(
                            ip_source=parsedLog['ip'],
                            type_evenement=parsedLog['method'],
                            fichier_log_id=fichierLogId,
                            url_cible=parsedLog['url'],
                        )
                        analyzedLines.append(event)
                    
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
                    if detectBrutForce(parsedLog):
                        attemptCount = getBrutForceTotalAttemptCount(parsedLog['ip'])
                        alert = AlertService.createAlerte(
                            ip_source=event['ip_source'],
                            type_evenement=f'Brute Force ({attemptCount} tentatives)',
                            fichier_log_id=fichierLogId,
                            status_code=parsedLog['status_code'],
                            evenement_id=event['evenement_id'],
                        )
                        attackDetected.append(alert)
                        print(json.dumps({
                            "type": "brutForce",
                            "data": {
                                "ip": event['ip_source'],
                                "date": parsedLog['date'],
                                "heure": parsedLog['heure'],
                                "attempts": attemptCount
                            }
                            }), flush=True)
                else:
                    print(f"Parsing ÉCHEC pour la ligne: {line}")  # Debug
    
        # Mettre à jour la position seulement après succès
        fichier.current_position = newPosition
        db.session.commit()
        
        print(f"Position mise à jour: {startPosition} → {newPosition}")
        return analyzedLines, newPosition, attackDetected
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")
        return [], startPosition, []
