from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import ANCVisit, Mother, Pregnancy, RiskRule, SmsLog


ANC_WEEKS = (12, 20, 28, 36)
DEFAULT_RULES = (
    ("r1", "bp_sys", ">=", 140, "u_mmHg", "high", "r_highbp"),
    ("r2", "bp_dia", ">=", 90, "u_mmHg", "high", "r_highbp"),
    ("r3", "hb", "<", 7, "u_gdl", "high", "r_sevan"),
    ("r4", "hb", "<", 10, "u_gdl", "moderate", "r_an"),
    ("r5", "age", "<", 18, "u_yrs", "moderate", "r_teen"),
    ("r6", "age", ">", 35, "u_yrs", "moderate", "r_old"),
)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def seed_defaults(db: Session) -> None:
    if not db.get(RiskRule, "r1"):
        db.add_all([
            RiskRule(id=rule[0], param=rule[1], op=rule[2], value=rule[3], unit=rule[4], sev=rule[5], reason=rule[6])
            for rule in DEFAULT_RULES
        ])
    from backend.models import User

    users = (
        ("u1", "asha", {"en": "Sunita Parmar", "gu": "સુનિતા પરમાર"}, "bakrol"),
        ("u2", "asha", {"en": "Jayshree Macwan", "gu": "જયશ્રી મેકવાન"}, "gana"),
        ("u3", "doctor", {"en": "Dr. Nirav Mehta", "gu": "ડૉ. નિરવ મહેતા"}, None),
        ("u4", "admin", {"en": "Kalpana Desai", "gu": "કલ્પના દેસાઈ"}, None),
    )
    for user_id, role, name, village in users:
        if not db.get(User, user_id):
            db.add(User(id=user_id, role=role, name=name, village=village))
    db.commit()


def send_sms(db: Session, recipient: str, kind: str, message_key: str, variables: dict, alert: bool = False) -> None:
    db.add(SmsLog(
        id=new_id("sms"), created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        recipient=recipient, kind=kind, message_key=message_key, variables=variables, alert=alert,
    ))


def visit_status(visit: ANCVisit, today: date | None = None) -> str:
    today = today or date.today()
    if visit.actual_date:
        return "done"
    if visit.scheduled_date < today:
        return "missed"
    if (visit.scheduled_date - today).days <= 7:
        return "due"
    return "upcoming"


def risk_hits(db: Session, mother: Mother, visit: ANCVisit | None) -> list[dict]:
    readings = {
        "age": mother.age,
        "bp_sys": visit.bp_sys if visit else None,
        "bp_dia": visit.bp_dia if visit else None,
        "hb": visit.hb if visit else None,
    }
    hits = []
    for rule in db.scalars(select(RiskRule)).all():
        value = readings[rule.param]
        if value is None:
            continue
        triggered = value >= rule.value if rule.op == ">=" else value > rule.value if rule.op == ">" else value < rule.value
        if triggered:
            hits.append({"id": rule.id, "param": rule.param, "sev": rule.sev, "reason": rule.reason, "value": value})
    return [
        hit for hit in hits
        if not (hit["sev"] == "moderate" and any(
            other["param"] == hit["param"] and other["sev"] == "high" for other in hits
        ))
    ]


def pregnancy_assessment(db: Session, pregnancy: Pregnancy) -> dict:
    completed = [visit for visit in pregnancy.visits if visit.actual_date]
    latest = max(completed, key=lambda visit: visit.no, default=None)
    hits = risk_hits(db, pregnancy.mother, latest)
    level = "high" if any(hit["sev"] == "high" for hit in hits) else "moderate" if hits else "normal"
    return {"level": level, "hits": hits, "reasons": list(dict.fromkeys(hit["reason"] for hit in hits)), "last_visit_id": latest.id if latest else None}


def generate_schedule(lmp: date, edd: date, today: date | None = None) -> list[date]:
    today = today or date.today()
    dates: list[date] = []
    for week in ANC_WEEKS:
        scheduled = lmp + timedelta(weeks=week)
        if not dates:
            dates.append(max(scheduled, today))
        elif scheduled > dates[-1] + timedelta(days=14) and scheduled < edd:
            dates.append(scheduled)
    return dates