import pytest
import os
from app.services import analyseServices
import builtins

def test_analyze_logs_for_attacks(monkeypatch, tmp_path):
    log_content = (
        '10.0.0.2 - - [10/Jul/2024:13:56:00 +0000] "POST /login.php?id=1%20OR%201=1 HTTP/1.1" 403 567\n'
        '192.168.1.1 - - [10/Jul/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234\n'
    )
    log_path = tmp_path / "access.log"
    log_path.write_text(log_content)
    real_open = builtins.open
    monkeypatch.setattr(
        "builtins.open",
        lambda path, mode='r': real_open(str(log_path), mode)
    )
    # NE PATCH PAS detectSQLInjection ici, teste la vraie fonction
    attacks = analyseServices.analyzeLogsForAttacks()
    assert len(attacks) == 1
    assert attacks[0]['ip'] == "10.0.0.2"
    assert attacks[0]['attack_type'] == "SQL_INJECTION"
    assert "or 1=1" in attacks[0]['url'].lower()

def test_detect_sql_injection(): # En attente de la fonction detectSQLInjection fonctionnelle
    assert analyseServices.detectSQLInjection("/index.php?id=1 UNION SELECT") is True
    assert analyseServices.detectSQLInjection("/index.php?id=1") is False
    assert analyseServices.detectSQLInjection("/login.php?id=1%20or%201=1") is True
    assert analyseServices.detectSQLInjection("/test.php?foo=bar") is False
    assert analyseServices.detectSQLInjection("/test.php?foo=UNION") is True
    assert analyseServices.detectSQLInjection("/test.php?foo=select") is True

def test_log_parser(monkeypatch, tmp_path):
    log_content = (
        '192.168.1.1 - - [10/Jul/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234\n'
        '10.0.0.2 - - [10/Jul/2024:13:56:00 +0000] "POST /login.php?id=1%20OR%201=1 HTTP/1.1" 403 567\n'
        'bad line without enough parts\n'
    )
    log_path = tmp_path / "access.log"
    log_path.write_text(log_content)

    # Monkeypatch open pour toujours ouvrir le fichier temporaire, peu importe le chemin demandé
    real_open = builtins.open
    monkeypatch.setattr(
        "builtins.open",
        lambda path, mode='r': real_open(str(log_path), mode)
    )

    logs = analyseServices.logParser()
    assert len(logs) == 2
    assert logs[0]['ip'] == "192.168.1.1"
    assert logs[1]['ip'] == "10.0.0.2"
    assert logs[0]['method'] == "GET"
    assert logs[1]['method'] == "POST"
