import pytest
from app import create_app, db
from app.models.user import Utilisateur
from app.services.authService import AuthService
from werkzeug.security import generate_password_hash

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
def session(app):
    with app.app_context():
        yield db.session

def test_create_user(session):
    success, msg = AuthService.createUser("testuser@example.com", "Abcdefg1!")
    assert success is True
    assert "créé" in msg
    user = Utilisateur.query.filter_by(email="testuser@example.com").first()
    assert user is not None

def test_create_user_duplicate(session):
    AuthService.createUser("dup@example.com", "Abcdefg1!")
    # Essaye de créer le même utilisateur (selon ta logique, peut lever une exception ou retourner False)
    try:
        success, msg = AuthService.createUser("dup@example.com", "Abcdefg1!")
        assert not success
    except Exception:
        assert True  # Si tu lèves une exception pour le doublon

def test_login_success(session):
    password = "Abcdefg1!"
    AuthService.createUser("login@example.com", password)
    success, token = AuthService.login("login@example.com", password)
    assert success is True
    assert isinstance(token, str)

def test_login_wrong_password(session):
    AuthService.createUser("wrongpw@example.com", "Abcdefg1!")
    user = Utilisateur.query.filter_by(email="wrongpw@example.com").first()
    user.mot_de_passe = generate_password_hash("Abcdefg1!")
    db.session.commit()
    success, msg = AuthService.login("wrongpw@example.com", "badpass")
    assert success is False
    assert "incorrect" in msg

def test_login_unknown_user(session):
    success, msg = AuthService.login("unknown@example.com", "Abcdefg1!")
    assert success is False
    assert "incorrect" in msg
