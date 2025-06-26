import pytest
from app import create_app, db
from app.models.evenement import Evenement

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

def test_create_evenement(session):
    evenement = Evenement(ip_source="1.2.3.4", type_evenement="SCAN")
    session.add(evenement)
    session.commit()
    assert evenement.evenement_id is not None
    assert evenement.ip_source == "1.2.3.4"
    assert evenement.type_evenement == "SCAN"
    assert evenement.created_at is not None

def test_to_dict(session):
    evenement = Evenement(ip_source="5.5.5.5", type_evenement="DOS", url_cible="http://target.com")
    session.add(evenement)
    session.commit()
    d = evenement.to_dict()
    assert d["evenement_id"] == str(evenement.evenement_id)
    assert d["ip_source"] == "5.5.5.5"
    assert d["type_evenement"] == "DOS"
    assert d["url_cible"] == "http://target.com"
    assert d["created_at"] == evenement.created_at.isoformat()

def test_missing_ip_source(session):
    with pytest.raises(Exception):
        evenement = Evenement(type_evenement="SCAN")
        session.add(evenement)
        session.commit()

def test_missing_type_evenement(session):
    with pytest.raises(Exception):
        evenement = Evenement(ip_source="1.2.3.4")
        session.add(evenement)
        session.commit()

def test_delete_evenement(session):
    evenement = Evenement(ip_source="9.9.9.9", type_evenement="SUPPRESSION")
    session.add(evenement)
    session.commit()
    evenement_id = evenement.evenement_id
    session.delete(evenement)
    session.commit()
    deleted = session.get(Evenement, evenement_id)
    assert deleted is None
