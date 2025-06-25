import os
from ..models.fichier_log import FichierLog
from ..models.user import Utilisateur
from app import db


class SettingsService:
    @staticmethod
    def verifyFileExtension(filePath, allowedExtensions={"log"}):
        """Vérifie si le fichier a une extension autorisée."""
        extension = os.path.splitext(filePath)[1][1:]  # Récupère l'extension sans le point
        if extension not in allowedExtensions:
            raise ValueError(f"L'extension '{extension}' n'est pas autorisée. Seuls les fichiers {allowedExtensions} sont acceptés.")
        return True

    @staticmethod
    def verifyFileExists(filePath):
        """Vérifie si le fichier existe sur le système."""
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"Le fichier {filePath} n'existe pas.")
        return True

    @staticmethod
    def createLogEntry(filePath, server, userId):
        """Crée une entrée en BDD pour le fichier log."""
        # Vérifier si l'utilisateur existe
        user = Utilisateur.query.get(userId)
        if not user:
            raise Exception("Utilisateur non trouvé")

        # Vérifier si le fichier existe déjà
        existing_log = FichierLog.query.filter_by(chemin=filePath, user_id=userId).first()
        if existing_log:
            raise ValueError("Ce fichier log existe déjà")

        # Créer une entrée en BDD
        try:
            fichier_log = FichierLog(
                chemin=filePath,
                type_log=server,
                user_id=user.utilisateur_id,
            )
            db.session.add(fichier_log)
            db.session.commit()
            return fichier_log
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Erreur lors de la création de l'entrée de log : {str(e)}")

    @staticmethod
    def processLogFile(filePath, server, userId):
        """Processus complet pour vérifier et enregistrer un fichier log."""
        # Vérifier l'existence du fichier
        SettingsService.verifyFileExists(filePath)

        # Vérifier l'extension du fichier
        SettingsService.verifyFileExtension(filePath)

        # Créer une entrée en BDD
        return SettingsService.createLogEntry(filePath, server, userId)
    
    @staticmethod
    def getLog(userId, log_id):
        """Récupère un fichier log de l'utilisateur"""
        user = Utilisateur.query.get(userId)
        if not user:
            return None
        
        log = FichierLog.query.filter_by(fichier_log_id=log_id, user_id=userId).first()
        return {
            "id": str(log.fichier_log_id),
            "chemin": log.chemin,
            "type_log": log.type_log,
            "add_at": log.add_at.isoformat() if log.add_at else None,
            "analyse_en_temps_reel": log.analyse_en_temps_reel
        } if log else None
    
    @staticmethod
    def getAllLogs(userId):
        """Récupère tous les fichiers logs de l'utilisateur"""
        user = Utilisateur.query.get(userId)
        if not user:
            return None
        
        logs = FichierLog.query.filter_by(user_id=userId).order_by(FichierLog.add_at.desc()).all()
        return [{
            "id": str(log.fichier_log_id),
            "chemin": log.chemin,
            "type_log": log.type_log,
            "add_at": log.add_at.isoformat() if log.add_at else None,
            "analyse_en_temps_reel": log.analyse_en_temps_reel
        } for log in logs] if logs else []
    
    @staticmethod
    def deleteLog(log_id, user_id):
        """Supprime un fichier log"""
        try:
            log = FichierLog.query.filter_by(fichier_log_id=log_id, user_id=user_id).first()
            if not log:
                return False
        
            db.session.delete(log)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
