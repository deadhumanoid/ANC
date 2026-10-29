"""Integration tests: real HTTP requests through FastAPI, validation, domain logic and the database.

Fixtures from tests/conftest.py:
  client   - fake browser on a fresh database (staff, 6 rules, 6 villages, 3 DEMO mothers)
  payload  - builds a registration body; payload(weeks_pregnant=9, phone=...) overrides fields
  register - registers through the API, checks 201, returns the pregnancy JSON
All dates are relative to today, so the suite passes on any day it is run.
"""
from datetime import date, timedelta

import pytest

from backend.database import SessionLocal
from backend.models import ANCVisit

pytestmark = pytest.mark.integration

NORMAL = {"bp_sys": 118, "bp_dia": 76, "hb": 11.5, "weight": 58}
PHONE = "9825076143"   # the default phone used by the payload fixture


def record(client, visit_id, **readings):
    return client.post(f"/api/visits/{visit_id}/record", json={**NORMAL, **readings})


def sms_to(client, recipient):
    return [message for message in client.get("/api/sms").json() if message["recipient"] == recipient]


def set_scheduled_date(visit_id, new_date):
    # Move a visit's date directly in the database to create due / missed situations.
    with SessionLocal() as db:
        db.get(ANCVisit, visit_id).scheduled_date = new_date
        db.commit()


# ------------------------------------------------------------- basics & seeds

def test_health_check_and_default_rules(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert len(client.get("/api/risk-rules").json()) == 6


def test_frontend_is_served_by_backend(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "Maternal Care Coordinator" in page.text
    for path in ("/js/app.js", "/js/data.js", "/js/i18n.js", "/css/style.css"):
        assert client.get(path).status_code == 200, path


def test_seeded_villages_and_demo_records(client):
    villages = {village["id"] for village in client.get("/api/villages").json()}
    assert villages == {"bakrol", "vadod", "gana", "vallabh_vidyanagar", "umreth", "petlad"}
    pregnancies = client.get("/api/pregnancies").json()
    assert len(pregnancies) == 3
    assert all(p["mother"]["name"]["en"].startswith("DEMO ") for p in pregnancies)


# --------------------------------------------------------------- registration

def test_registration_creates_record_schedule_and_sms(client, register):
    record_ = register(weeks_pregnant=9)
    lmp = date.fromisoformat(record_["lmp"])

    assert record_["edd"] == (lmp + timedelta(days=280)).isoformat()
    assert record_["gestational_week"] == 9
    assert record_["mother"]["name"] == {"en": "Test Mother", "gu": "Test Mother"}
    assert [v["no"] for v in record_["visits"]] == [1, 2, 3, 4]
    assert record_["visits"][0]["scheduled_date"] == (lmp + timedelta(weeks=12)).isoformat()
    assert record_["risk"]["level"] == "normal"
    assert [m["message_key"] for m in sms_to(client, PHONE)] == ["m_reg"]


def test_registration_persists(client, register):
    created = register()
    fetched = client.get(f"/api/pregnancies/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["mother"]["phone"] == PHONE
    assert len(client.get("/api/pregnancies").json()) == 4   # 3 DEMO + this one


def test_very_late_registration_gets_one_visit_today(register):
    record_ = register(weeks_pregnant=40)                    # exactly 280 days: last allowed day
    assert [v["scheduled_date"] for v in record_["visits"]] == [date.today().isoformat()]


@pytest.mark.parametrize("weeks_pregnant, mother_overrides, expected", [
    (0, {}, 201),                           # registered on the LMP day
    (40, {}, 201),                          # exactly 280 days ago: allowed
    (281 / 7, {}, 422),                     # 281 days ago: too old
    (-1 / 7, {}, 422),                      # LMP tomorrow: in the future
    (9, {"village": "unknown-village"}, 422),
    (9, {"asha_id": "u3"}, 422),            # u3 is a doctor, not an ASHA worker
    (9, {"asha_id": "nobody"}, 422),
    (9, {"phone": "5825076143"}, 422),
    (9, {"age": 11}, 422),
    (9, {"age": 56}, 422),
], ids=[
    "lmp-today", "lmp-280-days", "lmp-281-days", "lmp-future",
    "bad-village", "asha-is-doctor", "asha-unknown", "bad-phone", "age-11", "age-56",
])
def test_registration_validation(client, payload, weeks_pregnant, mother_overrides, expected):
    response = client.post("/api/pregnancies", json=payload(weeks_pregnant, **mother_overrides))
    assert response.status_code == expected, response.text


def test_duplicate_active_phone_is_rejected(client, payload, register):
    first = register()
    duplicate = client.post("/api/pregnancies", json=payload())
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["mother_id"] == first["mother"]["id"]


def test_demo_mothers_phone_counts_as_duplicate(client, payload):
    assert client.post("/api/pregnancies", json=payload(phone="9000000001")).status_code == 409


def test_different_phone_registers_fine(register):
    register()
    register(phone="9876543210")


# ----------------------------------------------------------- recording visits

def test_high_risk_visit_is_flagged_and_doctor_alerted(client, register):
    pregnancy = register()
    first, second = pregnancy["visits"][0], pregnancy["visits"][1]

    response = record(client, first["id"], bp_sys=146, bp_dia=94, hb=10.9)
    assert response.status_code == 200
    body = response.json()
    assert body["risk"]["level"] == "high"
    assert body["risk"]["reasons"] == ["r_highbp"]
    assert body["visit"]["actual_date"] == date.today().isoformat()

    [alert] = sms_to(client, "u3")
    assert alert["message_key"] == "m_alert" and alert["alert"] is True
    assert alert["variables"]["reasons"] == ["r_highbp"]

    visit_sms = [m for m in sms_to(client, PHONE) if m["message_key"] == "m_visit"]
    assert visit_sms[0]["variables"]["date"] == second["scheduled_date"]


def test_normal_visit_sends_no_alert(client, register):
    pregnancy = register()
    body = record(client, pregnancy["visits"][0]["id"]).json()
    assert body["risk"]["level"] == "normal"
    assert sms_to(client, "u3") == []


def test_moderate_visit_goes_on_watch_list_without_alert(client, register):
    pregnancy = register()
    body = record(client, pregnancy["visits"][0]["id"], hb=9.5).json()
    assert body["risk"]["level"] == "moderate"
    assert body["risk"]["reasons"] == ["r_an"]
    assert sms_to(client, "u3") == []


def test_same_visit_cannot_be_recorded_twice(client, register):
    visit_id = register()["visits"][0]["id"]
    assert record(client, visit_id).status_code == 200
    assert record(client, visit_id, bp_sys=160).status_code == 409


def test_last_visit_sends_the_last_visit_message(client, register):
    pregnancy = register()
    record(client, pregnancy["visits"][-1]["id"])
    keys = [m["message_key"] for m in sms_to(client, PHONE)]
    assert "m_visitLast" in keys and "m_visit" not in keys


def test_unknown_visit_is_404(client):
    assert record(client, "no-such-visit").status_code == 404


@pytest.mark.parametrize("bad_body", [
    {**NORMAL, "bp_sys": 300},
    {**NORMAL, "hb": 0},
    {**NORMAL, "weight": None},
    {k: v for k, v in NORMAL.items() if k != "weight"},
], ids=["bp-300", "hb-0", "weight-null", "weight-missing"])
def test_invalid_readings_are_rejected(client, register, bad_body):
    visit_id = register()["visits"][0]["id"]
    assert client.post(f"/api/visits/{visit_id}/record", json=bad_body).status_code == 422


def test_new_high_reading_reopens_a_reviewed_case(client, register):
    pregnancy = register()
    url = f"/api/pregnancies/{pregnancy['id']}"
    client.post(f"{url}/reviews", json={"by_id": "u3", "decision": "dRoutine", "text": "Looks fine"})
    assert client.get(url).json()["reviewed"] is True

    record(client, pregnancy["visits"][0]["id"], bp_sys=150)
    assert client.get(url).json()["reviewed"] is False


# ------------------------------------------------------------- doctor reviews

@pytest.mark.parametrize("decision, mother_message", [
    ("dRoutine", None),             # routine care: mother is not texted
    ("dPhc", "m_docvisit"),
    ("dRefer", "m_referral"),
])
def test_review_decision_notifies_the_right_people(client, register, decision, mother_message):
    pregnancy = register()
    response = client.post(f"/api/pregnancies/{pregnancy['id']}/reviews",
                           json={"by_id": "u3", "decision": decision, "text": "  Checked  "})
    assert response.status_code == 201
    assert response.json()["text"] == "Checked"                     # surrounding spaces trimmed

    mother_keys = {m["message_key"] for m in sms_to(client, PHONE)}
    assert mother_keys == {"m_reg"} | ({mother_message} if mother_message else set())
    assert [m["message_key"] for m in sms_to(client, "u1")] == ["m_docnote"]   # ASHA always told

    saved = client.get(f"/api/pregnancies/{pregnancy['id']}").json()
    assert saved["reviewed"] is True
    assert saved["reviews"][0]["decision"] == decision


@pytest.mark.parametrize("body", [
    {"by_id": "u1", "decision": "dRefer", "text": "x"},       # u1 is an ASHA worker, not a doctor
    {"by_id": "nobody", "decision": "dRefer", "text": "x"},
    {"by_id": "u3", "decision": "dMaybe", "text": "x"},
    {"by_id": "u3", "decision": "dRefer", "text": ""},
], ids=["not-a-doctor", "unknown-user", "bad-decision", "empty-note"])
def test_invalid_reviews_are_rejected(client, register, body):
    pregnancy = register()
    assert client.post(f"/api/pregnancies/{pregnancy['id']}/reviews", json=body).status_code == 422


def test_review_for_unknown_pregnancy_is_404(client):
    body = {"by_id": "u3", "decision": "dRefer", "text": "x"}
    assert client.post("/api/pregnancies/no-such-id/reviews", json=body).status_code == 404


@pytest.mark.xfail(reason="Known gap: a note of only spaces passes the schema and is saved as empty text")
def test_whitespace_only_note_is_rejected(client, register):
    pregnancy = register()
    body = {"by_id": "u3", "decision": "dRefer", "text": "   "}
    assert client.post(f"/api/pregnancies/{pregnancy['id']}/reviews", json=body).status_code == 422


# ----------------------------------------------------------------- risk rules

def test_changing_a_threshold_changes_the_next_assessment(client, register):
    pregnancy = register()
    first, second = pregnancy["visits"][0]["id"], pregnancy["visits"][1]["id"]

    assert record(client, first, bp_sys=142).json()["risk"]["level"] == "high"      # 142 >= 140
    assert client.patch("/api/risk-rules/r1", json={"value": 145}).json()["value"] == 145
    assert record(client, second, bp_sys=142).json()["risk"]["level"] == "normal"   # 142 < 145


def test_unknown_rule_is_404(client):
    assert client.patch("/api/risk-rules/r99", json={"value": 100}).status_code == 404


@pytest.mark.parametrize("value", [-5, 301])
def test_rule_value_out_of_range_is_rejected(client, value):
    assert client.patch("/api/risk-rules/r1", json={"value": value}).status_code == 422


# ----------------------------------------------------- listing & PHC summary

def test_pregnancy_list_filters(client, register):
    register()
    assert len(client.get("/api/pregnancies", params={"asha_id": "u1"}).json()) == 3   # 2 DEMO + new
    assert len(client.get("/api/pregnancies", params={"asha_id": "u2"}).json()) == 1
    assert client.get("/api/pregnancies", params={"status": "completed"}).json() == []
    assert client.get("/api/pregnancies", params={"status": "bogus"}).status_code == 422
    assert client.get("/api/pregnancies/no-such-id").status_code == 404


def test_summary_counts(client, register):
    pregnancy = register()
    record(client, pregnancy["visits"][0]["id"], bp_sys=150)
    summary = client.get("/api/summary").json()

    assert summary["active_pregnancies"] == 4
    assert summary["completed_visits"] == 4          # 3 DEMO first visits + the one just recorded
    assert summary["missed_visits"] == 0
    assert [row["visit_no"] for row in summary["by_visit"]] == [1, 2, 3, 4]
    by_asha = {row["asha_id"]: row for row in summary["by_asha"]}
    assert by_asha["u1"]["pregnancies"] == 3 and by_asha["u1"]["high_risk"] == 1
    assert by_asha["u2"]["pregnancies"] == 1


# ---------------------------------------------------------- daily reminder job

@pytest.mark.parametrize("days_away, expect_reminder", [
    (0, True),        # visit today
    (3, True),        # last day of the 3-day reminder window
    (4, False),       # one day too far
])
def test_reminder_window(client, register, days_away, expect_reminder):
    visit_id = register()["visits"][1]["id"]
    set_scheduled_date(visit_id, date.today() + timedelta(days=days_away))

    result = client.post("/api/reminders/run").json()
    assert result == {"reminders_sent": int(expect_reminder), "missed_notices_sent": 0}
    assert any(m["message_key"] == "m_reminder" for m in sms_to(client, PHONE)) is expect_reminder


def test_reminder_job_is_idempotent(client, register):
    visit_id = register()["visits"][1]["id"]
    set_scheduled_date(visit_id, date.today() + timedelta(days=2))

    assert client.post("/api/reminders/run").json()["reminders_sent"] == 1
    assert client.post("/api/reminders/run").json() == {"reminders_sent": 0, "missed_notices_sent": 0}
    assert sum(m["message_key"] == "m_reminder" for m in sms_to(client, PHONE)) == 1


def test_missed_visit_notifies_mother_and_asha_once(client, register):
    visit_id = register()["visits"][0]["id"]
    set_scheduled_date(visit_id, date.today() - timedelta(days=1))

    assert client.post("/api/reminders/run").json() == {"reminders_sent": 0, "missed_notices_sent": 1}
    assert client.post("/api/reminders/run").json() == {"reminders_sent": 0, "missed_notices_sent": 0}
    assert [m["message_key"] for m in sms_to(client, PHONE) if m["message_key"] == "m_missed"] == ["m_missed"]
    assert [m["message_key"] for m in sms_to(client, "u1")] == ["m_missedAsha"]


def test_recorded_visit_gets_no_reminder(client, register):
    visit_id = register()["visits"][1]["id"]
    set_scheduled_date(visit_id, date.today() + timedelta(days=1))
    record(client, visit_id)
    assert client.post("/api/reminders/run").json()["reminders_sent"] == 0
