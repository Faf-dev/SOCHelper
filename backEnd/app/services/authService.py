from ..models.user import Utilisateur
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app import db


class AuthService:
    @staticmethod
    def createUser(email, password):
        user = Utilisateur(email=email, mot_de_passe=password)
        db.session.add(user)
        db.session.commit()
        return True, "Utilisateur créé avec succès"

    @staticmethod
    def login(email, password):
        user = Utilisateur.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.mot_de_passe, password):
            return False, "Email ou mot de passe incorrect"
        token = create_access_token(identity=user.utilisateur_id, expires_delta=timedelta(seconds=3600))
        return True, token

    @staticmethod
    def refreshToken():
        user_id = get_jwt_identity()
        user = Utilisateur.query.get(user_id)
        
        if not user:
            return False, "Utilisateur non trouvé"
        
        # Créer un nouveau token
        new_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(seconds=3600)  # Expire dans 1 heure
        )
        return True, new_token
