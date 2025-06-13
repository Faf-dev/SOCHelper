from ..models.user import Utilisateur
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from .. import db


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
        token = create_access_token(identity=user.utilisateur_id)
        return True, token
