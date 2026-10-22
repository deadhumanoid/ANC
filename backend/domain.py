from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import ANCVisit, Mother, Pregnancy, RiskRule, SmsLog, Village


# Visit weeks and rule definitions are the defaults used to seed a new database.
ANC_WEEKS = (12, 20, 28, 36)
DEFAULT_RULES = (
    ("r1", "bp_sys", ">=", 140, "u_mmHg", "high", "r_highbp"),
    ("r2", "bp_dia", ">=", 90, "u_mmHg", "high", "r_highbp"),
    ("r3", "hb", "<", 7, "u_gdl", "high", "r_sevan"),
    ("r4", "hb", "<", 10, "u_gdl", "moderate", "r_an"),
    ("r5", "age", "<", 18, "u_yrs", "moderate", "r_teen"),
    ("r6", "age", ">", 35, "u_yrs", "moderate", "r_old"),
)
DEFAULT_VILLAGES = (
    ("bakrol", {"en": "Bakrol", "gu": "બાકરોલ"}),
    ("vadod", {"en": "Vadod", "gu": "વડોદ"}),
    ("gana", {"en": "Gana", "gu": "ગાના"}),
    ("vallabh_vidyanagar", {"en": "Vallabh Vidyanagar", "gu": "વલ્લભ વિદ્યાનગર"}),
    ("umreth", {"en": "Umreth", "gu": "ઉમરેઠ"}),
    ("petlad", {"en": "Petlad", "gu": "પેટલાદ"}),
)


def new_id(prefix: str) -> str:
    # Prefixes make IDs easier to recognize in logs while UUIDs keep them unique.
    return f"{prefix}_{uuid4().hex}"


def seed_defaults(db: Session) -> None:
    # Seed reference data on every startup, but never overwrite administrator-edited rules.
    if not db.get(RiskRule, "r1"):
        db.add_all([
            RiskRule(id=rule[0], param=rule[1], op=rule[2], value=rule[3], unit=rule[4], sev=rule[5], reason=rule[6])
            for rule in DEFAULT_RULES
        ])
    for village_id, name in DEFAULT_VILLAGES:
        if not db.get(Village, village_id):
            db.add(Village(id=village_id, name=name))

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

    # Use recognizable fictional data only for a completely empty patient database.
    if db.scalar(select(Mother.id).limit(1)) is None:
        today = date.today()
        demo_mothers = (
            ("demo_m1", {"en": "DEMO Meera Patel", "gu": "ડેમો મીરા પટેલ"}, 26, "9000000001", "bakrol", "u1", "O+"),
            ("demo_m2", {"en": "DEMO Hetal Parmar", "gu": "ડેમો હેતલ પરમાર"}, 29, "9000000002", "vadod", "u1", "B+"),
            ("demo_m3", {"en": "DEMO Nita Macwan", "gu": "ડેમો નીતા મેકવાન"}, 24, "9000000003", "gana", "u2", "A+"),
        )
        for mother_id, name, age, phone, village, asha_id, blood_group in demo_mothers:
            lmp = today - timedelta(weeks=12)
            edd = lmp + timedelta(days=280)
            mother = Mother(
                id=mother_id, name=name, age=age, phone=phone, village=village,
                blood_group=blood_group, asha_id=asha_id,
            )
            pregnancy = Pregnancy(
                id=f"demo_p{mother_id[-1]}", mother=mother, lmp=lmp, edd=edd,
                gravida=1, parity=0, status="active", reviewed=False,
            )
            pregnancy.visits = [
                ANCVisit(
                    id=f"demo_v{mother_id[-1]}_{index}", no=index,
                    scheduled_date=scheduled, actual_date=today if index == 1 else None,
                    bp_sys=118 if index == 1 else None, bp_dia=76 if index == 1 else None,
                    hb=11.2 if index == 1 else None, weight=54.0 if index == 1 else None,
                    notes="Synthetic demo measurement; not a real patient record." if index == 1 else "",
                )
                for index, scheduled in enumerate(generate_schedule(lmp, edd, today), start=1)
            ]
            db.add(pregnancy)
        db.commit()


def send_sms(db: Session, recipient: str, kind: str, message_key: str, variables: dict, alert: bool = False) -> None:
    # Store a template key and variables for localized display; no SMS gateway is called.
    db.add(SmsLog(
        id=new_id("sms"), created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        recipient=recipient, kind=kind, message_key=message_key, variables=variables, alert=alert,
    ))


def visit_status(visit: ANCVisit, today: date | None = None) -> str:
    # Accept an explicit date so callers and tests can evaluate status deterministically.
    today = today or date.today()
    if visit.actual_date:
        return "done"
    if visit.scheduled_date < today:
        return "missed"
    if (visit.scheduled_date - today).days <= 7:
        return "due"
    return "upcoming"


def risk_hits(db: Session, mother: Mother, visit: ANCVisit | None) -> list[dict]:
    # Age is always available; clinical readings remain absent until a visit is recorded.
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
        # Rule operators are stored as data so thresholds can be edited without code changes.
        triggered = value >= rule.value if rule.op == ">=" else value > rule.value if rule.op == ">" else value < rule.value
        if triggered:
            hits.append({"id": rule.id, "param": rule.param, "sev": rule.sev, "reason": rule.reason, "value": value})
    return [
        hit for hit in hits
        # A stricter high-risk rule replaces a moderate rule on the same reading.
        if not (hit["sev"] == "moderate" and any(
            other["param"] == hit["param"] and other["sev"] == "high" for other in hits
        ))
    ]


def pregnancy_assessment(db: Session, pregnancy: Pregnancy) -> dict:
    # Only the latest completed visit contributes readings to the current assessment.
    completed = [visit for visit in pregnancy.visits if visit.actual_date]
    latest = max(completed, key=lambda visit: visit.no, default=None)
    hits = risk_hits(db, pregnancy.mother, latest)
    level = "high" if any(hit["sev"] == "high" for hit in hits) else "moderate" if hits else "normal"
    return {"level": level, "hits": hits, "reasons": list(dict.fromkeys(hit["reason"] for hit in hits)), "last_visit_id": latest.id if latest else None}


def generate_schedule(lmp: date, edd: date, today: date | None = None) -> list[date]:
    # Late registrations start today; later visits retain the intended spacing and EDD bound.
    today = today or date.today()
    dates: list[date] = []
    for week in ANC_WEEKS:
        scheduled = lmp + timedelta(weeks=week)
        if not dates:
            # Never leave the first contact in the past after late registration.
            dates.append(max(scheduled, today))
        elif scheduled > dates[-1] + timedelta(days=14) and scheduled < edd:
            dates.append(scheduled)
    return dates