import pytest
from app import create_app, db
from app.models.user import Utilisateur
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = Utilisateur(email="settingsapi@example.com", mot_de_passe="Abcdefg1!")
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token(app):
    with app.app_context():
        user = Utilisateur.query.filter_by(email="settingsapi@example.com").first()
        return create_access_token(identity=user.utilisateur_id)

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def test_post_settings_success(client, token):
    data = {
        "server": "linux",
        "chemin": "/tmp/test.log"
    }
    response = client.post(
        "/api/settings/",
        data=data,
        headers=auth_headers(token)
    )
    assert response.status_code == 200
    assert "Fichier reçu" in response.get_json().get("msg", "")

def test_post_settings_missing_path(client, token):
    data = {
        "server": "linux"
        # "chemin" manquant
    }
    response = client.post(
        "/api/settings/",
        data=data,
        headers=auth_headers(token)
    )
    assert response.status_code == 400
    assert "Chemin du fichier non fourni" in response.get_json().get("msg", "")

def test_post_settings_missing_server(client, token):
    data = {
        "chemin": "/tmp/test.log"
        # "server" manquant
    }
    response = client.post(
        "/api/settings/",
        data=data,
        headers=auth_headers(token)
    )
    assert response.status_code == 400
    assert "Type de serveur non fourni" in response.get_json().get("msg", "")

def test_post_settings_unauthorized(client):
    data = {
        "server": "linux",
        "chemin": "/tmp/test.log"
    }
    response = client.post("/api/settings/", data=data)
    assert response.status_code == 401
