from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[dict] = mapped_column(JSON, nullable=False)
    village: Mapped[str | None] = mapped_column(String(80))


class Mother(Base):
    __tablename__ = "mothers"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[dict] = mapped_column(JSON, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    village: Mapped[str] = mapped_column(String(80), nullable=False)
    blood_group: Mapped[str] = mapped_column(String(5), default="Unknown", nullable=False)
    asha_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    pregnancies: Mapped[list["Pregnancy"]] = relationship(back_populates="mother")


class Pregnancy(Base):
    __tablename__ = "pregnancies"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    mother_id: Mapped[str] = mapped_column(ForeignKey("mothers.id"), nullable=False)
    lmp: Mapped[date] = mapped_column(Date, nullable=False)
    edd: Mapped[date] = mapped_column(Date, nullable=False)
    gravida: Mapped[int] = mapped_column(Integer, nullable=False)
    parity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mother: Mapped[Mother] = relationship(back_populates="pregnancies")
    visits: Mapped[list["ANCVisit"]] = relationship(
        back_populates="pregnancy", cascade="all, delete-orphan", order_by="ANCVisit.no"
    )
    reviews: Mapped[list["DoctorReview"]] = relationship(
        back_populates="pregnancy", cascade="all, delete-orphan", order_by="DoctorReview.created_at"
    )


class ANCVisit(Base):
    __tablename__ = "anc_visits"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    pregnancy_id: Mapped[str] = mapped_column(ForeignKey("pregnancies.id"), nullable=False)
    no: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_date: Mapped[date | None] = mapped_column(Date)
    weight: Mapped[float | None] = mapped_column(Float)
    bp_sys: Mapped[int | None] = mapped_column(Integer)
    bp_dia: Mapped[int | None] = mapped_column(Integer)
    hb: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(String(2000), default="", nullable=False)
    reminded_on: Mapped[date | None] = mapped_column(Date)
    missed_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pregnancy: Mapped[Pregnancy] = relationship(back_populates="visits")


class RiskRule(Base):
    __tablename__ = "risk_rules"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    param: Mapped[str] = mapped_column(String(20), nullable=False)
    op: Mapped[str] = mapped_column(String(3), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    sev: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str] = mapped_column(String(40), nullable=False)


class DoctorReview(Base):
    __tablename__ = "doctor_reviews"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    pregnancy_id: Mapped[str] = mapped_column(ForeignKey("pregnancies.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    by_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    pregnancy: Mapped[Pregnancy] = relationship(back_populates="reviews")


class SmsLog(Base):
    __tablename__ = "sms_logs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    recipient: Mapped[str] = mapped_column(String(40), nullable=False)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    message_key: Mapped[str] = mapped_column(String(40), nullable=False)
    variables: Mapped[dict] = mapped_column(JSON, nullable=False)
    alert: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)