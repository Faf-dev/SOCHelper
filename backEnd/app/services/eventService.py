from app.models.evenement import Evenement
from app.models.user import Utilisateur
from app import db
from datetime import datetime, timedelta


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
    def createEvent(ipSource, typeEvenement, fichierLogId, urlCible=None):
        """Crée un nouvel événement"""
        event = Evenement(
            ip_source=ipSource,
            type_evenement=typeEvenement,
            fichier_log_id=fichierLogId,
            url_cible=urlCible,
            created_at=datetime.now()
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
    @staticmethod
    def createEventIfNotExists(ipSource, typeEvenement, fichierLogId, urlCible=None, createdAt=None):
        """Crée un nouvel événement s'il n'existe pas déjà pour cette ligne de log"""
        if createdAt is None:
            createdAt = datetime.now()

        # On cherche un événement créé dans la même seconde avec les mêmes données
        existing = Evenement.query.filter(
            Evenement.ip_source == ipSource,
            Evenement.type_evenement == typeEvenement,
            Evenement.fichier_log_id == fichierLogId,
            Evenement.url_cible == urlCible,
            # On regarde seulement les événements créés dans la même seconde
            Evenement.created_at >= createdAt - timedelta(seconds=1),
            Evenement.created_at <= createdAt + timedelta(seconds=1)
        ).first()

        if existing:
            return existing.to_dict()

        event = Evenement(
            ip_source=ipSource,
            type_evenement=typeEvenement,
            fichier_log_id=fichierLogId,
            url_cible=urlCible,
            created_at=createdAt
        )
        db.session.add(event)
        db.session.commit()
        return event.to_dict()
