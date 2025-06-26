import os
import tempfile
import pytest
from app import create_app, db
from app.models.user import Utilisateur
from app.services.settingsService import SettingsService

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
    user = Utilisateur(email="settingsuser@example.com", mot_de_passe="Abcdefg1!")
    db.session.add(user)
    db.session.commit()
    return user

def test_verify_file_extension_ok():
    assert SettingsService.verifyFileExtension("access.log") is True

def test_verify_file_extension_fail():
    with pytest.raises(ValueError):
        SettingsService.verifyFileExtension("access.txt")

def test_verify_file_exists_ok(tmp_path):
    file_path = tmp_path / "access.log"
    file_path.write_text("test")
    assert SettingsService.verifyFileExists(str(file_path)) is True

def test_verify_file_exists_fail():
    with pytest.raises(FileNotFoundError):
        SettingsService.verifyFileExists("/tmp/fakefile.log")

def test_create_log_entry(session, user, tmp_path):
    file_path = tmp_path / "access.log"
    file_path.write_text("test")
    log_entry = SettingsService.createLogEntry(str(file_path), "nginx", user.utilisateur_id)
    assert log_entry.chemin == str(file_path)
    assert log_entry.type_log == "nginx"
    assert log_entry.user_id == user.utilisateur_id

def test_create_log_entry_user_not_found(tmp_path):
    file_path = tmp_path / "access.log"
    file_path.write_text("test")
    with pytest.raises(Exception):
        SettingsService.createLogEntry(str(file_path), "nginx", "fake-user-id")

def test_process_log_file(session, user, tmp_path):
    file_path = tmp_path / "access.log"
    file_path.write_text("test")
    log_entry = SettingsService.processLogFile(str(file_path), "nginx", user.utilisateur_id)
    assert log_entry.chemin == str(file_path)
    assert log_entry.type_log == "nginx"
    assert log_entry.user_id == user.utilisateur_id

def test_process_log_file_bad_extension(session, user, tmp_path):
    file_path = tmp_path / "access.txt"
    file_path.write_text("test")
    with pytest.raises(ValueError):
        SettingsService.processLogFile(str(file_path), "nginx", user.utilisateur_id)

def test_process_log_file_not_found(session, user):
    with pytest.raises(FileNotFoundError):
        SettingsService.processLogFile("/tmp/fakefile.log", "nginx", user.utilisateur_id)
