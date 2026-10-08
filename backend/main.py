from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.database import Base, engine, get_db
from backend.domain import generate_schedule, new_id, pregnancy_assessment, seed_defaults, send_sms, visit_status
from backend.models import ANCVisit, DoctorReview, Mother, Pregnancy, RiskRule, SmsLog, User
from backend.schemas import PregnancyCreate, RiskRuleOut, RiskRuleUpdate, ReviewCreate, SmsOut, VisitRecord


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        seed_defaults(db)
    yield


app = FastAPI(title="Maternal Care Coordinator API", version="1.0.0", lifespan=lifespan)
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:5500,http://127.0.0.1:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_pregnancy(db: Session, pregnancy_id: str) -> Pregnancy:
    pregnancy = db.scalar(
        select(Pregnancy).options(
            joinedload(Pregnancy.mother), joinedload(Pregnancy.visits), joinedload(Pregnancy.reviews)
        ).where(Pregnancy.id == pregnancy_id)
    )
    if not pregnancy:
        raise HTTPException(status_code=404, detail="Pregnancy not found")
    return pregnancy


def pregnancy_json(db: Session, pregnancy: Pregnancy) -> dict:
    return {
        "id": pregnancy.id,
        "mother": {
            "id": pregnancy.mother.id,
            "name": pregnancy.mother.name,
            "age": pregnancy.mother.age,
            "phone": pregnancy.mother.phone,
            "village": pregnancy.mother.village,
            "blood_group": pregnancy.mother.blood_group,
            "asha_id": pregnancy.mother.asha_id,
        },
        "lmp": pregnancy.lmp,
        "edd": pregnancy.edd,
        "gravida": pregnancy.gravida,
        "parity": pregnancy.parity,
        "status": pregnancy.status,
        "reviewed": pregnancy.reviewed,
        "gestational_week": (date.today() - pregnancy.lmp).days // 7,
        "risk": pregnancy_assessment(db, pregnancy),
        "visits": [visit_json(visit) for visit in pregnancy.visits],
        "reviews": [{
            "id": review.id, "created_at": review.created_at, "by_id": review.by_id,
            "decision": review.decision, "text": review.text,
        } for review in pregnancy.reviews],
    }


def visit_json(visit: ANCVisit) -> dict:
    return {
        "id": visit.id, "pregnancy_id": visit.pregnancy_id, "no": visit.no,
        "scheduled_date": visit.scheduled_date, "actual_date": visit.actual_date,
        "weight": visit.weight, "bp_sys": visit.bp_sys, "bp_dia": visit.bp_dia,
        "hb": visit.hb, "notes": visit.notes,
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/users")
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.role, User.id)).all()


@app.get("/api/pregnancies")
def list_pregnancies(
    status: str | None = Query(default="active", pattern="^(active|completed|all)$"),
    asha_id: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Pregnancy).options(joinedload(Pregnancy.mother), joinedload(Pregnancy.visits))
    if status != "all":
        query = query.where(Pregnancy.status == status)
    if asha_id:
        query = query.join(Pregnancy.mother).where(Mother.asha_id == asha_id)
    return [pregnancy_json(db, p) for p in db.scalars(query).unique().all()]


@app.get("/api/pregnancies/{pregnancy_id}")
def get_pregnancy_detail(pregnancy_id: str, db: Session = Depends(get_db)):
    return pregnancy_json(db, get_pregnancy(db, pregnancy_id))


@app.post("/api/pregnancies", status_code=201)
def create_pregnancy(payload: PregnancyCreate, db: Session = Depends(get_db)):
    today = date.today()
    if payload.lmp > today or (today - payload.lmp).days > 280:
        raise HTTPException(status_code=422, detail="LMP must be within the current 40-week pregnancy window")
    asha = db.get(User, payload.mother.asha_id)
    if not asha or asha.role != "asha":
        raise HTTPException(status_code=422, detail="asha_id must identify an ASHA worker")
    duplicate = db.scalar(
        select(Mother).join(Pregnancy).where(
            Mother.phone == payload.mother.phone, Pregnancy.status == "active"
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail={"message": "An active pregnancy already uses this phone number", "mother_id": duplicate.id})
    name = payload.mother.name
    localized_name = name if isinstance(name, dict) else {"en": name, "gu": name}
    mother = Mother(
        id=new_id("m"), name=localized_name, age=payload.mother.age, phone=payload.mother.phone,
        village=payload.mother.village, blood_group=payload.mother.blood_group, asha_id=payload.mother.asha_id,
    )
    edd = payload.lmp + timedelta(days=280)
    pregnancy = Pregnancy(
        id=new_id("p"), mother=mother, lmp=payload.lmp, edd=edd,
        gravida=payload.gravida, parity=payload.parity, status="active", reviewed=False,
    )
    pregnancy.visits = [
        ANCVisit(id=new_id("v"), no=index, scheduled_date=scheduled, notes="")
        for index, scheduled in enumerate(generate_schedule(payload.lmp, edd, today), start=1)
    ]
    db.add(pregnancy)
    send_sms(db, mother.phone, "k_reg", "m_reg", {
        "name": {language: text.split()[0] for language, text in localized_name.items()},
        "edd": edd.isoformat(), "date": pregnancy.visits[0].scheduled_date.isoformat(),
    })
    db.commit()
    return pregnancy_json(db, get_pregnancy(db, pregnancy.id))


@app.post("/api/visits/{visit_id}/record")
def record_visit(visit_id: str, payload: VisitRecord, db: Session = Depends(get_db)):
    visit = db.get(ANCVisit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    if visit.actual_date:
        raise HTTPException(status_code=409, detail="Visit has already been recorded")
    pregnancy = get_pregnancy(db, visit.pregnancy_id)
    visit.actual_date = date.today()
    visit.bp_sys, visit.bp_dia = payload.bp_sys, payload.bp_dia
    visit.hb, visit.weight, visit.notes = payload.hb, payload.weight, payload.notes
    db.flush()
    assessment = pregnancy_assessment(db, pregnancy)
    mother = pregnancy.mother
    if assessment["level"] == "high":
        pregnancy.reviewed = False
        send_sms(db, "u3", "k_alert", "m_alert", {
            "name": mother.name, "village": {"k": f"v_{mother.village}"},
            "w": (date.today() - pregnancy.lmp).days // 7, "reasons": assessment["reasons"],
        }, alert=True)
    next_visit = next((item for item in pregnancy.visits if item.actual_date is None and item.no > visit.no), None)
    variables = {"name": {lang: text.split()[0] for lang, text in mother.name.items()}}
    if next_visit:
        send_sms(db, mother.phone, "k_visit", "m_visit", {**variables, "date": next_visit.scheduled_date.isoformat()})
    else:
        send_sms(db, mother.phone, "k_visit", "m_visitLast", variables)
    db.commit()
    return {"visit": visit_json(visit), "risk": assessment}


@app.post("/api/pregnancies/{pregnancy_id}/reviews", status_code=201)
def create_review(pregnancy_id: str, payload: ReviewCreate, db: Session = Depends(get_db)):
    pregnancy = get_pregnancy(db, pregnancy_id)
    doctor = db.get(User, payload.by_id)
    if not doctor or doctor.role != "doctor":
        raise HTTPException(status_code=422, detail="by_id must identify a doctor")
    review = DoctorReview(
        id=new_id("review"), pregnancy=pregnancy, created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        by_id=payload.by_id, decision=payload.decision, text=payload.text.strip(),
    )
    pregnancy.reviewed = True
    mother = pregnancy.mother
    if payload.decision == "dRefer":
        send_sms(db, mother.phone, "k_referral", "m_referral", {"name": {lang: text.split()[0] for lang, text in mother.name.items()}})
    elif payload.decision == "dPhc":
        send_sms(db, mother.phone, "k_docvisit", "m_docvisit", {"name": {lang: text.split()[0] for lang, text in mother.name.items()}})
    send_sms(db, mother.asha_id, "k_docnote", "m_docnote", {
        "name": mother.name, "decision": {"k": payload.decision}, "note": payload.text.strip(),
    })
    db.add(review)
    db.commit()
    return {"id": review.id, "pregnancy_id": pregnancy_id, "created_at": review.created_at, "by_id": review.by_id, "decision": review.decision, "text": review.text}


@app.get("/api/risk-rules", response_model=list[RiskRuleOut])
def list_risk_rules(db: Session = Depends(get_db)):
    return db.scalars(select(RiskRule).order_by(RiskRule.id)).all()


@app.patch("/api/risk-rules/{rule_id}", response_model=RiskRuleOut)
def update_risk_rule(rule_id: str, payload: RiskRuleUpdate, db: Session = Depends(get_db)):
    rule = db.get(RiskRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Risk rule not found")
    rule.value = payload.value
    db.commit()
    db.refresh(rule)
    return rule


@app.get("/api/summary")
def get_summary(db: Session = Depends(get_db)):
    pregnancies = db.scalars(
        select(Pregnancy).options(joinedload(Pregnancy.mother), joinedload(Pregnancy.visits)).where(Pregnancy.status == "active")
    ).unique().all()
    visits = [visit for pregnancy in pregnancies for visit in pregnancy.visits]
    by_visit = []
    for number in range(1, 5):
        due = [visit for visit in visits if visit.no == number and visit.scheduled_date <= date.today()]
        by_visit.append({"visit_no": number, "due": len(due), "done": sum(bool(visit.actual_date) for visit in due)})
    by_asha = []
    for user in db.scalars(select(User).where(User.role == "asha")).all():
        assigned = [pregnancy for pregnancy in pregnancies if pregnancy.mother.asha_id == user.id]
        assigned_visits = [visit for pregnancy in assigned for visit in pregnancy.visits]
        by_asha.append({"asha_id": user.id, "name": user.name, "pregnancies": len(assigned),
                        "completed": sum(bool(visit.actual_date) for visit in assigned_visits),
                        "missed": sum(visit_status(visit) == "missed" for visit in assigned_visits),
                        "high_risk": sum(pregnancy_assessment(db, p)["level"] == "high" for p in assigned)})
    return {"active_pregnancies": len(pregnancies), "completed_visits": sum(bool(v.actual_date) for v in visits),
            "missed_visits": sum(visit_status(v) == "missed" for v in visits), "by_visit": by_visit, "by_asha": by_asha}


@app.get("/api/sms", response_model=list[SmsOut])
def list_sms(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    return db.scalars(select(SmsLog).order_by(SmsLog.created_at.desc()).limit(limit)).all()


@app.post("/api/reminders/run")
def run_reminders(db: Session = Depends(get_db)):
    today = date.today()
    pregnancies = db.scalars(
        select(Pregnancy).options(joinedload(Pregnancy.mother), joinedload(Pregnancy.visits)).where(Pregnancy.status == "active")
    ).unique().all()
    reminders = missed_notices = 0
    for pregnancy in pregnancies:
        mother = pregnancy.mother
        for visit in pregnancy.visits:
            status = visit_status(visit, today)
            if not visit.actual_date and status != "missed" and (visit.scheduled_date - today).days <= 3 and visit.reminded_on != today:
                visit.reminded_on = today
                reminders += 1
                send_sms(db, mother.phone, "k_reminder", "m_reminder", {
                    "name": {lang: text.split()[0] for lang, text in mother.name.items()},
                    "date": visit.scheduled_date.isoformat(), "village": {"k": f"v_{mother.village}"},
                })
            if status == "missed" and not visit.missed_notified:
                visit.missed_notified = True
                missed_notices += 1
                send_sms(db, mother.phone, "k_missed", "m_missed", {"name": mother.name, "date": visit.scheduled_date.isoformat()})
                send_sms(db, mother.asha_id, "k_missed", "m_missedAsha", {"name": mother.name, "n": visit.no, "date": visit.scheduled_date.isoformat()})
    db.commit()
    return {"reminders_sent": reminders, "missed_notices_sent": missed_notices}