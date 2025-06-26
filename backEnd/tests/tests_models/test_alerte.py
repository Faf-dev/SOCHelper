import pytest
from app import create_app, db
from app.models.alerte import Alerte
from app.models.evenement import Evenement

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

def test_create_alerte(session):
    alerte = Alerte(ip_source="192.168.1.1", type_evenement="INTRUSION")
    session.add(alerte)
    session.commit()
    assert alerte.alerte_id is not None
    assert alerte.ip_source == "192.168.1.1"
    assert alerte.type_evenement == "INTRUSION"
    assert alerte.created_at is not None

def test_alerte_with_evenement(session):
    evenement = Evenement(url_cible="http://test.com", ip_source="1.2.3.4", type_evenement="SCAN")
    session.add(evenement)
    session.commit()
    alerte = Alerte(ip_source="10.0.0.1", type_evenement="SCAN", evenement_id=evenement.evenement_id)
    session.add(alerte)
    session.commit()
    assert alerte.evenement_id == evenement.evenement_id
    assert alerte.evenement.url_cible == "http://test.com"

def test_to_dict(session):
    alerte = Alerte(ip_source="8.8.8.8", type_evenement="DOS")
    session.add(alerte)
    session.commit()
    d = alerte.to_dict()
    assert d["alerte_id"] == str(alerte.alerte_id)
    assert d["ip_source"] == "8.8.8.8"
    assert d["type_evenement"] == "DOS"
    assert d["created_at"] == alerte.created_at.isoformat()
    
def test_delete_alerte(session):
    # Création et ajout d'une alerte
    alerte = Alerte(ip_source="5.5.5.5", type_evenement="SUPPRESSION")
    session.add(alerte)
    session.commit()
    alerte_id = alerte.alerte_id

    # Suppression de l'alerte
    session.delete(alerte)
    session.commit()

    # Vérifie que l'alerte n'existe plus dans la base
    deleted = session.get(Alerte, alerte_id)
    assert deleted is None
