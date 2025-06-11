from app import db
import uuid
import re
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy.orm import validates
from datetime import datetime


class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'

    utilisateur_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(254), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    fichiers = db.relationship("FichierLog", backref="utilisateur", lazy=True)

    @validates('email')
    def validateEmail(self, key, value):
        """Valide l'email selon les critères spécifiés."""
        if not isinstance(value, str):
            raise TypeError("L'email doit être une chaîne de caractères")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Format d'email invalide")
        if Utilisateur.query.filter_by(email=value).first():
            raise ValueError("L'Email existe déjà")
        return value

    @validates('mot_de_passe')
    def validatePassword(self, key, value):
        """Valide le mot de passe selon les critères spécifiés."""
        if not isinstance(value, str):
            raise TypeError("Le mot de passe doit être une chaîne de caractères")
        if len(value) < 8:
            raise ValueError("Le mot de passe doit comporter au moins 8 caractères")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not re.search(r"[a-z]", value):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not re.search(r"[0-9]", value):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Le mot de passe doit contenir au moins un caractère spécial")
        return self.hashPassword(value)

    @staticmethod
    def hashPassword(mot_de_passe):
        """Hash le mot de passe avant de le stocker."""
        return generate_password_hash(mot_de_passe)

    def verifyPassword(self, mot_de_passe):
        """Vérifie si le mot de passe fourni correspond au mot de passe haché stocké."""
        return check_password_hash(self.mot_de_passe, mot_de_passe)
