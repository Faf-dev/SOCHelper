from app import db
import uuid
from datetime import datetime


class Alerte(db.Model):
    tablename = 'alertes'

    alerte_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_source = db.Column(db.String(45), nullable=False)  # 45 chars pour IPv6
    type_evenement = db.Column(db.String(255), nullable=False)
    status_code = db.Column(db.Integer, nullable=True)
    evenement_id = db.Column(db.String(36), db.ForeignKey('evenements.evenement_id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "alerte_id": str(self.alerte_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ip_source": self.ip_source,
            "type_evenement": self.type_evenement,
            "status_code": self.status_code,
            "url_cible": self.evenement.url_cible if self.evenement else None
        }
