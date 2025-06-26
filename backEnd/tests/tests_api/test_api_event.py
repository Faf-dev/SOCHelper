import pytest
from app import create_app, db
from app.models.user import Utilisateur
from app.models.evenement import Evenement
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = Utilisateur(email="eventapi@example.com", mot_de_passe="Abcdefg1!")
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
        user = Utilisateur.query.filter_by(email="eventapi@example.com").first()
        return create_access_token(identity=user.utilisateur_id)

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def test_get_events_empty(client, token):
    response = client.get("/api/event/", headers=auth_headers(token))
    assert response.status_code == 200
    assert isinstance(response.get_json(), list) or "events" in response.get_json()

def test_get_events_since_invalid_date(client, token):
    response = client.get("/api/event/?since=notadate", headers=auth_headers(token))
    assert response.status_code == 400
    assert "Format de date invalide" in response.get_json().get("msg", "")

def test_delete_event_not_found(client, token):
    response = client.delete("/api/event/doesnotexist", headers=auth_headers(token))
    assert response.status_code == 404
    assert "Événement non trouvé" in response.get_json().get("msg", "")

def test_get_events_pagination(client, token):
    response = client.get("/api/event/?page=1&per_page=2", headers=auth_headers(token))
    assert response.status_code == 200
