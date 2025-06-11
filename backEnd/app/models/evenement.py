from .. import db
import uuid
from datetime import datetime


class Evenement(db.Model):
    __tablename__ = 'evenements'

    evenement_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_source = db.Column(db.String(15), nullable=False)
    type_evenement = db.Column(db.String(255), nullable=False)
    fichier_log_id = db.Column(db.String(36), db.ForeignKey('fichier_log.fichier_log_id'))
    url_cible = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    alertes = db.relationship("Alerte", backref="evenement", lazy=True)

    def delete(self):
        """Supprime l'événement de la base de données."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Convertit l'événement en dictionnaire."""
        return {
            'evenement_id': str(self.evenement_id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ip_source': self.ip_source,
            'type_evenement': self.type_evenement,
            'url_cible': self.url_cible
        }
