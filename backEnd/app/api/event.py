from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from ..models.evenement import Evenement
from ..services.analyseServices.analyseService import analyzeLogsForAttacks
from ..services.eventService import EventService
from .. import limiter



event_ns = Namespace("event", description="Opérations sur les événements")

event_model = event_ns.model('Event', {
    "ip_source": fields.String(required=True, description="Adresse IP source"),
    "type_evenement": fields.String(required=True, description="Type d'événement"),
    "fichier_log_id": fields.String(required=True, description="ID du fichier log"),
    "url_cible": fields.String(required=False, description="URL cible"),
})


@event_ns.route('/', methods=['GET'])
class Event(Resource):
    @jwt_required()
    @limiter.exempt
    @event_ns.response(200, "Événements récupérés avec succès")
    @event_ns.response(404, "Utilisateur non trouvé")
    @event_ns.param('page', 'Numéro de page', type='int', required=False)
    @event_ns.param('per_page', 'Événements par page', type='int', required=False)
    @event_ns.param('since', 'Timestamp ISO pour récupérer seulement les nouveaux événements', type='string', required=False)
    def get(self):
        user_id = get_jwt_identity()
        since = request.args.get('since')
        
        if since:
            try:
                since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
                events = EventService.getEventsSince(user_id, since_datetime)
            except ValueError:
                return {"msg": "Format de date invalide. Utilisez le format ISO"}, 400
        else:
            # Pagination normale
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            result = EventService.getEventsPaginated(user_id, page=page, per_page=per_page)
            if result is None:
                return {"msg": "Utilisateur non trouvé"}, 404
            return result["events"], 200
        
        if events is None:
            return {"msg": "Utilisateur non trouvé"}, 404
        
        return events, 200

@event_ns.route('/<string:event_id>', methods=['DELETE'])
class EventById(Resource):
    @jwt_required()
    @event_ns.response(200, "Événement supprimé avec succès")
    @event_ns.response(404, "Événement non trouvé")
    def delete(self, event_id):
        event = Evenement.query.get(event_id)
        if not event:
            return {"msg": "Événement non trouvé"}, 404
        try:
            EventService.deleteEvent(event_id)
        except Exception as e:
            return {"msg": f"Erreur lors de la suppression de l'événement: {str(e)}"}, 500
        return {"msg": "Événement supprimé avec succès"}, 200

@event_ns.route('/analyze', methods=['POST'])
class EventAnalyze(Resource):
    @jwt_required()
    @event_ns.response(200, "Analyse des événements lancée")
    @event_ns.response(400, "Requête invalide")
    def post(self):
        """
        Lance l'analyse des logs pour le fichier donné.
        Body attendu: { "fichier_log_id": "<UUID>" }
        """
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        fichier_log_id = data.get('fichier_log_id')
        if not fichier_log_id:
            return {"msg": "fichier_log_id manquant"}, 400

        events, new_position, alerts = analyzeLogsForAttacks(fichier_log_id)
        return {
            "events_detected": len(events),
            "events_created": events,
            "new_position": new_position
            }, 200
