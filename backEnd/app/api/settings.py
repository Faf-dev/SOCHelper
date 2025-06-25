from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.settingsService import SettingsService
from ..models.user import Utilisateur
from ..models.fichier_log import FichierLog

settings_ns = Namespace("settings", description="Upload de fichiers et analyse")

@settings_ns.route('/')
class Upload(Resource):
    @jwt_required()
    def post(self):
        userId = get_jwt_identity()
        user = Utilisateur.query.get(userId)
        if not user:
            return {"msg": "Utilisateur non trouvé"}, 404

        server = request.form.get("server")
        path = request.form.get("chemin")

        if not path:
            return {"msg": "Chemin du fichier non fourni"}, 400
        if not server:
            return {"msg": "Type de serveur non fourni"}, 400

        try:
            # Crée une entrée en BDD
            fichier_log = SettingsService.createLogEntry(path, server, userId)
            return {
               "msg": "Fichier reçu et analyse lancée", 
               "id": str(fichier_log.fichier_log_id),
               "server": server, 
               "filePath": path
            }, 200
        except Exception as e:
            return {"msg": f"Erreur lors du traitement : {str(e)}"}, 500
        
@settings_ns.route('/logs/<string:log_id>/activate')
class LogActivate(Resource):
    @jwt_required()
    def post(self, log_id):
        """Active un fichier log pour l'analyse"""
        user_id = get_jwt_identity()
        log = FichierLog.query.filter_by(fichier_log_id=log_id, user_id=user_id).first()
        if not log:
            return {"msg": "Fichier log non trouvé"}, 404
        
        return {"msg": "Fichier log activé", "id": str(log.fichier_log_id)}, 200

@settings_ns.route('/logs')
class LogList(Resource):
    @jwt_required()
    def get(self):
        """Récupère tous les fichiers logs de l'utilisateur"""
        try:
            user_id = get_jwt_identity()
            logs = SettingsService.getAllLogs(user_id)
            if logs is None:
                return [], 200
        
            return logs, 200
        except Exception as e:
            return {"msg": f"Erreur : {str(e)}"}, 500

@settings_ns.route('/logs/<string:log_id>')
class LogDelete(Resource):
    @jwt_required()
    def delete(self, log_id):
        """Supprime un fichier log par son ID"""
        try:
            user_id = get_jwt_identity()
        
            success = SettingsService.deleteLog(log_id, user_id)
            if not success:
                return {"msg": "Fichier log non trouvé ou erreur lors de la suppression"}, 404
        
            return {"msg": "Fichier log supprimé"}, 200
        except Exception as e:
            return {"msg": f"Erreur lors de la suppression du fichier log : {str(e)}"}, 500
