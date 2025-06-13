from ..models.fichier_log import FichierLog
from ..models.user import Utilisateur
from ..db import db

allowedExtensions = {"log"}

class SettingsService:
    @staticmethod
    def allowedFile(fileName):
        """Vérifie si le fichier est valide (nom et extension)."""
        return fileName == "access.log"

    @staticmethod
    def createLogEntry(filePath, server, userId):
        """Crée une entrée en BDD pour le fichier log."""
        user = Utilisateur.query.get(userId)
        if not user:
            raise Exception("Utilisateur non trouvé")
        try :
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
