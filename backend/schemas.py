from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# These API contracts validate incoming data independently from SQLAlchemy's table definitions.
class MotherCreate(BaseModel):
    name: str | dict[str, str]
    age: int = Field(ge=12, le=55)
    phone: str = Field(pattern=r"^[6-9][0-9]{9}$")
    village: str = Field(min_length=1, max_length=80)
    blood_group: str = "Unknown"
    asha_id: str


class PregnancyCreate(BaseModel):
    """A mother registration and the pregnancy dates/history needed to schedule ANC."""

    mother: MotherCreate
    lmp: date
    gravida: int = Field(default=1, ge=1)
    parity: int = Field(default=0, ge=0)


class VisitRecord(BaseModel):
    """Measurements submitted when an ASHA worker completes a scheduled visit."""

    bp_sys: int = Field(ge=60, le=250)
    bp_dia: int = Field(ge=30, le=160)
    hb: float = Field(gt=2, le=20)
    weight: float = Field(ge=25, le=150)
    notes: str = Field(default="", max_length=2000)


class ReviewCreate(BaseModel):
    """A doctor's allowed decision and the note attached to it."""

    by_id: str
    decision: Literal["dRoutine", "dPhc", "dRefer"]
    text: str = Field(min_length=1, max_length=2000)


class RiskRuleUpdate(BaseModel):
    # Keep administrator-edited thresholds within a broad, non-negative range.
    value: float = Field(ge=0, le=300)


class RiskRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    param: str
    op: str
    value: float
    unit: str
    sev: str
    reason: str


class VillageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: dict[str, str]


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    pregnancy_id: str
    no: int
    scheduled_date: date
    actual_date: date | None
    weight: float | None
    bp_sys: int | None
    bp_dia: int | None
    hb: float | None
    notes: str


class SmsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    recipient: str
    kind: str
    message_key: str
    variables: dict
    alert: bool