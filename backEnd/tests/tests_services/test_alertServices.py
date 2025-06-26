import pytest
from app import create_app, db
from app.models.user import Utilisateur
from app.models.alerte import Alerte
from app.services.alertService import AlertService
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = Utilisateur(email="alertservice@example.com", mot_de_passe="Abcdefg1!")
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

@pytest.fixture
def user(session):
    return Utilisateur.query.filter_by(email="alertservice@example.com").first()

def test_save_alerte(session, user):
    alerte = AlertService.saveAlerte("INTRUSION", None, "1.2.3.4")
    assert alerte["type_evenement"] == "INTRUSION"
    assert alerte["ip_source"] == "1.2.3.4"
    assert "alerte_id" in alerte

def test_get_all_alertes(session, user):
    AlertService.saveAlerte("INTRUSION", None, "1.2.3.4")
    alertes = AlertService.getAllAlertes(user.utilisateur_id)
    assert isinstance(alertes, list)
    assert len(alertes) >= 1

def test_get_alertes_since(session, user):
    now = datetime.utcnow()
    AlertService.saveAlerte("SCAN", None, "5.5.5.5")
    alertes = AlertService.getAlertesSince(user.utilisateur_id, now - timedelta(minutes=1))
    assert isinstance(alertes, list)
    assert len(alertes) >= 1

def test_delete_alerte(session, user):
    alerte = AlertService.saveAlerte("DOS", None, "8.8.8.8")
    alerte_id = alerte["alerte_id"]
    deleted = AlertService.deleteAlerte(alerte_id)
    assert deleted is True
    # Vérifie que l'alerte n'existe plus
    assert Alerte.query.get(alerte_id) is None

def test_get_alertes_paginated(session, user):
    # Ajoute plusieurs alertes
    for i in range(7):
        AlertService.saveAlerte("TYPE", None, f"10.0.0.{i}")
    result = AlertService.getAlertesPaginated(user.utilisateur_id, page=1, per_page=5)
    assert "alerts" in result
    assert result["page"] == 1
    assert result["limit"] == 5
    assert result["total_alerts"] >= 7
    assert len(result["alerts"]) <= 5
