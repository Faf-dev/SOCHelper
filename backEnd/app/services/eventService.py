from app.models.evenement import Evenement
from app.models.user import Utilisateur
from app.db import db
from datetime import datetime


class EventService:
    @staticmethod
    def getAllEvents(user_id):
        """Récupère tous les événements pour un utilisateur donné"""
        user = Utilisateur.query.get(user_id)
        if not user:
            return None
        
        events = Evenement.query.order_by(Evenement.created_at.desc()).all()
        return [event.to_dict() for event in events]

    @staticmethod
    def getEventsSince(user_id, since_datetime):
        """Récupère les événements depuis une date donnée"""
        user = Utilisateur.query.get(user_id)
        if not user:
            return None
        
        events = Evenement.query.filter(
            Evenement.created_at > since_datetime
        ).order_by(Evenement.created_at.desc()).all()
        
        return [event.to_dict() for event in events]

    @staticmethod
    def deleteEvent(event_id):
        """Supprime un événement par son ID"""
        event = Evenement.query.get(event_id)
        if not event:
            return False
        
        db.session.delete(event)
        db.session.commit()
        return True

    @staticmethod
    def createEvent(ip_source, type_evenement, fichier_log_id, url_cible=None):
        """Crée un nouvel événement"""
        event = Evenement(
            ip_source=ip_source,
            type_evenement=type_evenement,
            fichier_log_id=fichier_log_id,
            url_cible=url_cible,
            created_at=datetime.utcnow()
        )
        db.session.add(event)
        db.session.commit()
        return event.to_dict()
    
    @staticmethod
    def getEventsPaginated(user_id, page=1, per_page=10):
        """Récupère les événements paginés"""
        user = Utilisateur.query.get(user_id)
        if not user:
           return None
    
        pagination = Evenement.query.order_by(Evenement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            "events": [event.to_dict() for event in pagination.items],
            "page": page,
            "limit": per_page,
            "total_events": pagination.total
    }
