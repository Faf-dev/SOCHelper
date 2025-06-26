import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import Utilisateur
from app.models.evenement import Evenement
from app.services.eventService import EventService

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

@pytest.fixture
def user(session):
    user = Utilisateur(email="eventuser@example.com", mot_de_passe="Abcdefg1!")
    db.session.add(user)
    db.session.commit()
    return user

def test_create_event(session, user):
    event_dict = EventService.createEvent(
        ip_source="1.2.3.4",
        type_evenement="ALERT",
        fichier_log_id=1,
        url_cible="/test"
    )
    assert event_dict["ip_source"] == "1.2.3.4"
    assert event_dict["type_evenement"] == "ALERT"
    assert event_dict["url_cible"] == "/test"

def test_get_all_events(session, user):
    # Ajoute deux événements
    EventService.createEvent("1.1.1.1", "ALERT", 1)
    EventService.createEvent("2.2.2.2", "INFO", 1)
    events = EventService.getAllEvents(user.utilisateur_id)
    assert len(events) == 2
    assert events[0]["ip_source"] in ["1.1.1.1", "2.2.2.2"]

def test_get_events_since(session, user):
    old_event = EventService.createEvent("3.3.3.3", "ALERT", 1)
    since = datetime.utcnow()  # Prendre la date juste avant le nouvel event
    new_event = EventService.createEvent("4.4.4.4", "INFO", 1)
    events = EventService.getEventsSince(user.utilisateur_id, since)
    assert any(e["ip_source"] == "4.4.4.4" for e in events)
    assert all(e["ip_source"] != "3.3.3.3" for e in events)

def test_delete_event(session, user):
    event_dict = EventService.createEvent("5.5.5.5", "ALERT", 1)
    event_id = event_dict["evenement_id"]
    assert EventService.deleteEvent(event_id) is True
    assert EventService.deleteEvent(event_id) is False  # déjà supprimé

def test_get_events_paginated(session, user):
    # Ajoute 15 événements
    for i in range(15):
        EventService.createEvent(f"10.0.0.{i}", "ALERT", 1)
    page1 = EventService.getEventsPaginated(user.utilisateur_id, page=1, per_page=10)
    page2 = EventService.getEventsPaginated(user.utilisateur_id, page=2, per_page=10)
    assert len(page1["events"]) == 10
    assert len(page2["events"]) == 5
    assert page1["total_events"] == 15
