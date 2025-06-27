from app.models.alerte import Alerte
from app.models.user import Utilisateur
from app.models.evenement import Evenement
from app import db
from datetime import datetime
from sqlalchemy.orm import joinedload


class AlertService:
    @staticmethod
    def getAllAlertes(user_id):
        """Récupère tous les événements pour un utilisateur donné"""
        user = Utilisateur.query.get(user_id)
        if not user:
            return None
        
        alerts = Alerte.query.order_by(Alerte.created_at.desc()).all()
        return [alert.to_dict() for alert in alerts]
    
    @staticmethod
    def getAlertesSince(user_id, since_datetime):
        """Récupère les alertes depuis une date donnée"""
        user = Utilisateur.query.get(user_id)
        if not user:
            return None
        alerts = Alerte.query.options(
            joinedload(Alerte.evenement)
        ).filter(
            Alerte.created_at > since_datetime
        ).order_by(Alerte.created_at.desc()).all()
        
        return [alert.to_dict() for alert in alerts]

    @staticmethod
    def saveAlerte(type_evenement, evenement_id, ip_source):
        """Enregistre une nouvelle alerte dans la base de données"""
        alerte = Alerte(
            type_evenement=type_evenement,
            evenement_id=evenement_id,
            ip_source=ip_source,
            created_at=datetime.now()
        )
        db.session.add(alerte)
        db.session.commit()
        return alerte.to_dict()
    
    @staticmethod
    def deleteAlerte(alert_id):
        """Supprime une alerte par son ID"""
        alert = Alerte.query.get(alert_id)
        if not alert:
            return False
        db.session.delete(alert)
        db.session.commit()
        return True

    @staticmethod
    def createAlerte(ip_source, type_evenement, fichier_log_id, status_code, url_cible=None, evenement_id=None):
        """Crée une nouvelle alerte"""
        alert = Alerte(
            ip_source=ip_source,
            type_evenement=type_evenement,
            status_code=status_code,
            evenement_id=evenement_id,
            created_at=datetime.now()
        )
        db.session.add(alert)
        db.session.commit()
        return alert.to_dict()

    @staticmethod
    def getAlertesPaginated(user_id, page=1, per_page=5):
        """Récupère les alertes paginés"""
        user = Utilisateur.query.get(user_id)
        if not user:
           return None
    
        pagination = Alerte.query.options(
            joinedload(Alerte.evenement)  # Charger l'événement lié
        ).order_by(Alerte.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            "alerts": [alert.to_dict() for alert in pagination.items],
            "page": page,
            "limit": per_page,
            "total_alerts": pagination.total
    }
