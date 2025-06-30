from app import db
import uuid
from datetime import datetime


class FichierLog(db.Model):
    __tablename__ = 'fichier_log'

    fichier_log_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chemin = db.Column(db.Text, nullable=False)
    type_log = db.Column(db.String(50), nullable=False)
    analyse_en_temps_reel = db.Column(db.Boolean, default=False)
    current_position = db.Column(db.Integer, default=0)
    add_at = db.Column(db.Date, default=datetime.now)
    user_id = db.Column(db.String(36), db.ForeignKey('utilisateur.utilisateur_id'), nullable=False)

    evenements = db.relationship("Evenement", backref="fichier_log", lazy=True)
