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
        # Création d'un utilisateur pour les tests
        user = Utilisateur(email="alertapi@example.com", mot_de_passe="Abcdefg1!")
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
        user = Utilisateur.query.filter_by(email="alertapi@example.com").first()
        return create_access_token(identity=user.utilisateur_id)

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def test_get_alerts_empty(client, token):
    response = client.get("/api/alert/", headers=auth_headers(token))
    assert response.status_code == 200
    assert isinstance(response.get_json(), list) or "alerts" in response.get_json()

def test_post_alert(client, token):
    
    data = {
        "ip_source": "1.2.3.4",
        "type_evenement": "INTRUSION",
        "evenement_id": "dummy-event-id"
    }
    response = client.post("/api/alert/", json=data, headers=auth_headers(token))
    print("POST /api/alert/ response:", response.status_code, response.get_json())
    assert response.status_code == 201
    assert "Alerte créée" in response.get_json().get("msg", "")

def test_delete_alert_not_found(client, token):
    response = client.delete("/api/alert/doesnotexist", headers=auth_headers(token))
    assert response.status_code == 404
    assert "Alerte non trouvé" in response.get_json().get("msg", "")

def test_post_alert_unauthorized(client):
    data = {
        "ip_source": "9.9.9.9",
        "type_evenement": "INTRUSION",
        "evenement_id": "dummy-event-id"
    }
    response = client.post("/api/alert/", json=data)
    assert response.status_code == 401 or response.status_code == 422
