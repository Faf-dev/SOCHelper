from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from dotenv import load_dotenv
import os
import sys

limiter = Limiter(get_remote_address, default_limits=["10000 per hour", "1000 per minute"])
db = SQLAlchemy()
jwt = JWTManager()


def createApp(configName=None):
    # Détermine le bon chemin du .env selon le contexte (dev ou .exe)
    if getattr(sys, 'frozen', False):
        # Application packagée (.exe)
        env_path = os.path.join(os.path.dirname(sys.executable), '.env')
    else:
        # Dev : .env à la racine du projet
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)

    app = Flask(__name__)
    CORS(app)

    # Configuration SQLite
    if configName == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        # Détermine le dossier de l'application (compatible .exe)
        if getattr(sys, 'frozen', False):
            # Application compilée (.exe)
            appDir = os.path.dirname(sys.executable)
        else:
            # Application en développement
            appDir = os.path.dirname(os.path.dirname(__file__))
        
        db_path = os.path.join(appDir, os.getenv('DB_NAME', 'soc_helper.db'))
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
    jwtExpirationMinutes = int(os.getenv("JWT_EXPIRATION", 120))  # 120 minutes par défaut
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=jwtExpirationMinutes)

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    from app import models

    # Enregistrement des routes API
    from flask_restx import Api
    from .api.auth import auth_ns
    from .api.event import event_ns
    from .api.settings import settings_ns
    from .api.alert import alert_ns

    api = Api(app, doc='/')  # Swagger est accessible sur /

    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(event_ns, path='/api/event')
    api.add_namespace(alert_ns, path='/api/alert')
    api.add_namespace(settings_ns, path='/api/settings')
    

    return app
