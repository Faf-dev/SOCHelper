import pytest
from app import create_app, db
from app.models.user import Utilisateur

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_success(client):
    data = {"email": "testauth@example.com", "password": "Abcdefg1!"}
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 201
    assert response.get_json().get("msg", "") == "Utilisateur créé avec succès"

def test_register_duplicate(client):
    data = {"email": "dup@example.com", "password": "Abcdefg1!"}
    client.post("/api/auth/register", json=data)
    response = client.post("/api/auth/register", json=data)
    assert response.status_code in (401, 409, 400)  # selon ta gestion d'erreur

def test_login_success(client):
    data = {"email": "login@example.com", "password": "Abcdefg1!"}
    client.post("/api/auth/register", json=data)
    response = client.post("/api/auth/login", json=data)
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_wrong_password(client):
    data = {"email": "wrongpw@example.com", "password": "Abcdefg1!"}
    client.post("/api/auth/register", json=data)
    response = client.post("/api/auth/login", json={"email": "wrongpw@example.com", "password": "badpass"})
    assert response.status_code == 401

def test_get_user(client):
    # Register and login to get token
    data = {"email": "getuser@example.com", "password": "Abcdefg1!"}
    client.post("/api/auth/register", json=data)
    login = client.post("/api/auth/login", json=data)
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/user", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["email"] == "getuser@example.com"

def test_logout(client):
    data = {"email": "logout@example.com", "password": "Abcdefg1!"}
    client.post("/api/auth/register", json=data)
    login = client.post("/api/auth/login", json=data)
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200

def test_refresh_token(client):
    data = {"email": "refresh@example.com", "password": "Abcdefg1!"}
    client.post("/api/auth/register", json=data)
    login = client.post("/api/auth/login", json=data)
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/auth/refreshToken", headers=headers)
    assert response.status_code in (200, 404)
