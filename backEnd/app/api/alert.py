from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.alerte import Alerte
from app import limiter
from app.services.alertService import AlertService

alert_ns = Namespace("alert", description="Opérations sur les alertes du dashboard")

alerte_model = alert_ns.model('Alerte', {
    "alerte_id": fields.String(required=True, description="ID de l'alerte"),
    "ip_source": fields.String(required=True, description="Adresse IP source de l'alerte"),
    "type_evenement": fields.String(required=True, description="Type d'événement de l'alerte"),
    "status_code": fields.Integer(required=False, description="Code de statut HTTP associé à l'alerte"),
    "evenement_id": fields.String(required=True, description="ID de l'événement associé à l'alerte"),
    "created_at": fields.String(required=True, description="Date de création de l'alerte"),
})


@alert_ns.route('/', methods=['GET'])
class Alert(Resource):
    @jwt_required()
    @limiter.exempt
    @alert_ns.response(200, "Événements récupérés avec succès")
    @alert_ns.response(404, "Utilisateur non trouvé")
    @alert_ns.param('page', 'Numéro de page', type='int', required=False)
    @alert_ns.param('per_page', 'Événements par page', type='int', required=False)
    @alert_ns.param('since', 'Timestamp ISO pour récupérer seulement les nouveaux événements', type='string', required=False)
    def get(self):
        user_id = get_jwt_identity()
        since = request.args.get('since')
        
        if since:
            try:
                since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
                alerts = AlertService.getAlertesSince(user_id, since_datetime)
            except ValueError:
                return {"msg": "Format de date invalide. Utilisez le format ISO"}, 400
        else:
            # Pagination normale
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            result = AlertService.getAlertesPaginated(user_id, page=page, per_page=per_page)
            if result is None:
                return {"msg": "Utilisateur non trouvé"}, 404
            return result["alerts"], 200
        
        if alerts is None:
            return {"msg": "Utilisateur non trouvé"}, 404
        
        return alerts, 200
    
    
    @alert_ns.expect(alerte_model, validate=True)
    @alert_ns.response(201, "Alerte créée")
    @alert_ns.response(500, "Erreur lors de la création de l'alerte")
    @jwt_required()
    def post(self):
        """Crée une nouvelle alerte depuis le dashboard"""
        data = request.get_json()
        try:
            AlertService.saveAlerte(
                type_evenement=data.get("type_evenement"),
                evenement_id=data.get("evenement_id"),
                ip_source=data.get("ip_source")
            )
            return {"msg": "Alerte créée"}, 201
        except Exception as e:
            return {"msg": "Erreur lors de la création", "error": str(e)}, 500

@alert_ns.route('/<string:alert_id>', methods=['DELETE'])
class AlertById(Resource):
    @jwt_required()
    @limiter.exempt
    @alert_ns.response(200, "Alerte supprimé avec succès")
    @alert_ns.response(404, "Alerte non trouvé")
    def delete(self, alert_id):
        alerte = Alerte.query.get(alert_id)
        if not alerte:
            return {"msg": "Alerte non trouvé"}, 404
        try:
            AlertService.deleteAlerte(alert_id)
        except Exception as e:
            return {"msg": f"Erreur lors de la suppression de l'alerte: {str(e)}"}, 500
        return {"msg": "Alerte supprimé avec succès"}, 200
