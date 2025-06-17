from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_access_token
from .. import limiter
from app.services.authService import AuthService
from ..models.user import Utilisateur
from .. import db

# Création du namespace
auth_ns = Namespace("auth", description="Opérations d'authentification")

# Modèle pour la validation d'entrée (Swagger + vérification auto)
auth_model = auth_ns.model('Auth', {
    "email": fields.String(required=True,
                           description="Adresse email de l'utilisateur"),
    "password": fields.String(required=True,
                              description="Mot de passe de l'utilisateur"),
})


@auth_ns.route('/register', methods=['POST'])
class Register(Resource):
    @auth_ns.expect(auth_model)
    @auth_ns.response(201, "Inscription réussie")
    @auth_ns.response(409, "Utilisateur déjà enregistré")
    @auth_ns.response(400, "Données d'entrée invalides")
    @auth_ns.response(500, "Erreur lors de l'inscription")
    def post(self):
        """Inscription d'un nouvel utilisateur"""
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        try:
            success, result = AuthService.createUser(email, password)
            if success:
                return {"msg": result}, 201
            else:
                return {"msg": result}, 401
        except ValueError as ve:
            db.session.rollback()
            return {"msg": str(ve)}, 400
        except Exception as e:
            db.session.rollback()
            return {"msg": str(e)}, 400


@auth_ns.route('/login', methods=['POST'])
class Login(Resource):
    @limiter.limit("5 per minute")
    # Limite de 5 tentatives de connexion par minute.
    @auth_ns.expect(auth_model)
    @auth_ns.response(400, "Données d'entrée invalides")
    @auth_ns.response(429, "Trop de tentatives de connexion")
    @auth_ns.response(200, "Connexion réussie")
    @auth_ns.response(401, "Email ou mot de passe incorrect")
    @auth_ns.response(500, "Erreur lors de la connexion")
    def post(self):
        """Connexion et génération d'un token JWT"""
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        success, result = AuthService.login(email, password)
        if success:
            return {"access_token": result}, 200
        else:
            return {"msg": result}, 401


@auth_ns.route('/user', methods=['GET'])
class User(Resource):
    @limiter.limit("10 per minute")
    @jwt_required()
    @auth_ns.response(200, "Utilisateur récupéré avec succès")
    @auth_ns.response(404, "Utilisateur non trouvé")
    def get(self):
        user_id = get_jwt_identity()
        user = Utilisateur.query.get(user_id)
        if not user:
            return {"msg": "Utilisateur non trouvé"}, 404
        return {"email": user.email}, 200

@auth_ns.route('/logout', methods=['POST'])
class Logout(Resource):
    @jwt_required()
    @auth_ns.response(200, "Déconnexion réussie")
    @auth_ns.response(404, "Utilisateur non trouvé")
    @auth_ns.response(401, "Token invalide ou expiré")
    def post(self):
        """Déconnexion de l'utilisateur"""
        user = get_jwt_identity()
        if user:
            return {"msg": "Déconnexion réussie"}, 200
        return {"msg": "Utilisateur non trouvé"}, 404

@auth_ns.route('/refreshToken')
class RefreshToken(Resource):
    @jwt_required()
    @auth_ns.response(200, "Token renouvelé avec succès")
    @auth_ns.response(404, "Utilisateur non trouvé") 
    @auth_ns.response(401, "Token invalide ou expiré")
    def post(self):
        """Renouvellement du token JWT"""
        success, result = AuthService.refreshToken()
        if success:
            return {"token": result}, 200
        else:
            return {"msg": result}, 404
