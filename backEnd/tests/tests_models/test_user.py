import pytest
from app import create_app, db
from app.models.user import Utilisateur

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

def test_create_user(session):
    user = Utilisateur(email="test@example.com", mot_de_passe="Abcdefg1!")
    session.add(user)
    session.commit()
    assert user.utilisateur_id is not None
    assert user.verifyPassword("Abcdefg1!") is True
    assert user.email == "test@example.com"
    assert user.mot_de_passe != "Abcdefg1!" # mot de passe hashé


def test_invalid_email(session):
    with pytest.raises(ValueError):
        user = Utilisateur(email="invalidemail", mot_de_passe="Abcdefg1!")
        session.add(user)
        session.commit()
        

def test_short_password(session):
    with pytest.raises(ValueError):
        user = Utilisateur(email="test2@example.com", mot_de_passe="Abc1!")
        session.add(user)
        session.commit()
        

def test_duplicate_email(session):
    user1 = Utilisateur(email="dup@example.com", mot_de_passe="Abcdefg1!")
    session.add(user1)
    session.commit()
    with pytest.raises(ValueError):
        user2 = Utilisateur(email="dup@example.com", mot_de_passe="Abcdefg1!")
        session.add(user2)
        session.commit()
