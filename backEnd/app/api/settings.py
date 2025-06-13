from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.settingsService import SettingsService
from ..models.user import Utilisateur

settings_ns = Namespace("settings", description="Upload de fichiers et analyse")

@settings_ns.route('/')
class Upload(Resource):
    @jwt_required()
    def post(self):
        userId = get_jwt_identity()
        user = Utilisateur.query.get(userId)
        if not user:
            return {"msg": "Utilisateur non trouvé"}, 404

        file = request.files.get("file")
        server = request.form.get("server")
        path = request.form.get("chemin")

        if not file or not SettingsService.allowedFile(file.filename):
            return {"msg": "Fichier invalide ou non fourni"}, 400
        if not server:
            return {"msg": "Type de serveur non fourni"}, 400

        try:
            # Crée une entrée en BDD
            SettingsService.createLogEntry(path, server, userId)

            return {"msg": "Fichier reçu et analyse lancée", "server": server, "fileName": file.filename}, 200
        except Exception as e:
            return {"msg": f"Erreur lors du traitement : {str(e)}"}, 500
