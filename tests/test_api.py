import os
from datetime import date, timedelta

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
import pytest

from backend.database import Base, SessionLocal, engine
from backend.domain import seed_defaults
from backend.main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_defaults(db)
    with TestClient(app) as test_client:
        yield test_client


def registration_payload():
    return {
        "mother": {
            "name": "Test Mother", "age": 24, "phone": "9825076143",
            "village": "bakrol", "blood_group": "O+", "asha_id": "u1",
        },
        "lmp": "2026-07-01", "gravida": 1, "parity": 0,
    }


def test_health_and_default_rules(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert len(client.get("/api/risk-rules").json()) == 6


def test_frontend_is_served_by_backend(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "Maternal Care Coordinator" in page.text
    assert client.get("/js/data.js").status_code == 200
    assert client.get("/css/style.css").status_code == 200


def test_villages_and_synthetic_demo_records_are_seeded(client):
    villages = client.get("/api/villages").json()
    assert {village["id"] for village in villages} >= {
        "bakrol", "vadod", "gana", "vallabh_vidyanagar", "umreth", "petlad",
    }
    pregnancies = client.get("/api/pregnancies").json()
    assert len(pregnancies) == 3
    assert all(pregnancy["mother"]["name"]["en"].startswith("DEMO ") for pregnancy in pregnancies)


def test_registration_schedules_visits_and_rejects_duplicate(client):
    response = client.post("/api/pregnancies", json=registration_payload())
    assert response.status_code == 201
    record = response.json()
    assert record["edd"] == "2027-04-07"
    assert record["mother"]["name"] == {"en": "Test Mother", "gu": "Test Mother"}
    assert len(record["visits"]) == 4
    assert client.post("/api/pregnancies", json=registration_payload()).status_code == 409


def test_registration_rejects_unsupported_village(client):
    payload = registration_payload()
    payload["mother"]["village"] = "unknown-village"
    assert client.post("/api/pregnancies", json=payload).status_code == 422


def test_visit_recording_assesses_risk_and_is_idempotency_guarded(client):
    pregnancy = client.post("/api/pregnancies", json=registration_payload()).json()
    visit = pregnancy["visits"][0]
    response = client.post(f"/api/visits/{visit['id']}/record", json={
        "bp_sys": 146, "bp_dia": 94, "hb": 10.9, "weight": 59, "notes": "Raised BP",
    })
    assert response.status_code == 200
    assert response.json()["risk"]["level"] == "high"
    assert client.post(f"/api/visits/{visit['id']}/record", json={
        "bp_sys": 118, "bp_dia": 76, "hb": 11, "weight": 59,
    }).status_code == 409


def test_doctor_review_and_rule_update(client):
    pregnancy = client.post("/api/pregnancies", json=registration_payload()).json()
    response = client.post(f"/api/pregnancies/{pregnancy['id']}/reviews", json={
        "by_id": "u3", "decision": "dRefer", "text": "Refer for evaluation",
    })
    assert response.status_code == 201
    assert client.patch("/api/risk-rules/r1", json={"value": 145}).json()["value"] == 145


def test_reminder_job_logs_messages_and_is_idempotent(client):
    pregnancy = client.post("/api/pregnancies", json=registration_payload()).json()
    with SessionLocal() as db:
        from backend.models import ANCVisit

        visit = db.get(ANCVisit, pregnancy["visits"][1]["id"])
        visit.scheduled_date = date.today() + timedelta(days=2)
        db.commit()

    first_run = client.post("/api/reminders/run").json()
    assert first_run["reminders_sent"] >= 1
    assert client.post("/api/reminders/run").json() == {
        "reminders_sent": 0, "missed_notices_sent": 0,
    }
    messages = client.get("/api/sms").json()
    assert any(message["message_key"] == "m_reg" for message in messages)
    assert any(message["message_key"] == "m_reminder" for message in messages)