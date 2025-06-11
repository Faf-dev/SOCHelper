from .. import db
import uuid
from datetime import datetime


class Alerte(db.Model):
    __tablename__ = 'alertes'

    alerte_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_source = db.Column(db.String(15), nullable=False)
    type_evenement = db.Column(db.String(255), nullable=False)
    evenement_id = db.Column(db.String(36), db.ForeignKey('evenements.evenement_id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def delete(self) :
        """Supprime l'alerte de la base de données"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """Convertit l'alerte en dictionnaire."""
        return {
            "alerte_id": str(self.alerte_id),
            "ip_source": self.ip_source,
            "type_evenement": self.type_evenement,
            "evenement_id": self.evenement_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
