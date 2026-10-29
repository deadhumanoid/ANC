"""Shared test setup.

DATABASE_URL must be set before anything from `backend` is imported, because
backend/database.py reads it at import time. Every test then gets a brand-new
in-memory database, so tests never see each other's data or your real anc.db.
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from backend.database import Base, SessionLocal, engine
from backend.domain import seed_defaults
from backend.main import app


def reset_database():
    # Drop and recreate every table, then add staff, risk rules, villages and DEMO mothers.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_defaults(db)


@pytest.fixture
def db():
    """A database session on a fresh, seeded database (used by unit tests)."""
    reset_database()
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client():
    """A fake browser talking to the app, on a fresh, seeded database (used by integration tests)."""
    reset_database()
    with TestClient(app) as test_client:
        yield test_client


def lmp_weeks_ago(weeks: float) -> date:
    # Dates are always relative to today so the tests keep passing on any day they are run.
    return date.today() - timedelta(days=round(weeks * 7))


@pytest.fixture
def payload():
    """Returns a function that builds a fresh registration body; keyword arguments override fields."""
    def build(weeks_pregnant=9, **mother_overrides):
        mother = {
            "name": "Test Mother", "age": 24, "phone": "9825076143",
            "village": "bakrol", "blood_group": "O+", "asha_id": "u1",
        }
        mother.update(mother_overrides)
        return {"mother": mother, "lmp": lmp_weeks_ago(weeks_pregnant).isoformat(), "gravida": 1, "parity": 0}
    return build


@pytest.fixture
def register(client, payload):
    """Registers a mother through the API and returns the created pregnancy JSON."""
    def do(**kwargs):
        response = client.post("/api/pregnancies", json=payload(**kwargs))
        assert response.status_code == 201, response.text
        return response.json()
    return do
