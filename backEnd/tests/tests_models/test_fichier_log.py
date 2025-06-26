import pytest
from app import create_app, db
from app.models.fichier_log import FichierLog
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
def session(app):
    with app.app_context():
        yield db.session

def test_create_fichier_log(session):
    user = Utilisateur(email="loguser@example.com", mot_de_passe="Abcdefg1!")
    session.add(user)
    session.commit()
    fichier = FichierLog(
        chemin="/var/log/syslog",
        type_log="syslog",
        analyse_en_temps_reel=True,
        user_id=user.utilisateur_id
    )
    session.add(fichier)
    session.commit()
    assert fichier.fichier_log_id is not None
    assert fichier.chemin == "/var/log/syslog"
    assert fichier.type_log == "syslog"
    assert fichier.analyse_en_temps_reel is True
    assert fichier.user_id == user.utilisateur_id

def test_missing_chemin(session):
    user = Utilisateur(email="missingchemin@example.com", mot_de_passe="Abcdefg1!")
    session.add(user)
    session.commit()
    with pytest.raises(Exception):
        fichier = FichierLog(
            type_log="syslog",
            user_id=user.utilisateur_id
        )
        session.add(fichier)
        session.commit()

def test_missing_user_id(session):
    with pytest.raises(Exception):
        fichier = FichierLog(
            chemin="/tmp/test.log",
            type_log="syslog"
        )
        session.add(fichier)
        session.commit()

def test_delete_fichier_log(session):
    user = Utilisateur(email="deletefile@example.com", mot_de_passe="Abcdefg1!")
    session.add(user)
    session.commit()
    fichier = FichierLog(
        chemin="/tmp/delete.log",
        type_log="syslog",
        user_id=user.utilisateur_id
    )
    session.add(fichier)
    session.commit()
    fichier_id = fichier.fichier_log_id
    session.delete(fichier)
    session.commit()
    deleted = session.get(FichierLog, fichier_id)
    assert deleted is None
