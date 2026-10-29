"""Unit tests for risk_hits() and pregnancy_assessment() in backend/domain.py.

The thresholds are stored as data (the risk_rules table), so these tests use the `db`
fixture to read the six default rules. The mothers and visits are plain Python objects
that are never saved, so each test controls exactly which readings are checked.

Default rules: systolic >= 140, diastolic >= 90, Hb < 7 -> high;
               Hb < 10, age < 18, age > 35 -> moderate.
"""
from datetime import date

import pytest

from backend.domain import pregnancy_assessment, risk_hits
from backend.models import ANCVisit, Mother, Pregnancy, RiskRule

pytestmark = pytest.mark.unit

T = date(2026, 11, 1)


def make_visit(no=1, done=True, bp_sys=118, bp_dia=76, hb=11.5):
    """A visit with normal readings unless a test overrides one."""
    return ANCVisit(
        id=f"v{no}", no=no, scheduled_date=T, actual_date=T if done else None,
        bp_sys=bp_sys, bp_dia=bp_dia, hb=hb, weight=55.0,
    )


def flags(hits):
    """Turn the list of hits into a set of (reason, severity) pairs for easy comparison."""
    return {(hit["reason"], hit["sev"]) for hit in hits}


# ------------------------------------------------------------------ risk_hits

@pytest.mark.parametrize("readings, age, expected", [
    ({}, 25, set()),
    # systolic BP boundary
    ({"bp_sys": 139}, 25, set()),
    ({"bp_sys": 140}, 25, {("r_highbp", "high")}),
    # diastolic BP boundary
    ({"bp_dia": 89}, 25, set()),
    ({"bp_dia": 90}, 25, {("r_highbp", "high")}),
    # haemoglobin: two rules on the same reading
    ({"hb": 10.0}, 25, set()),
    ({"hb": 9.9}, 25, {("r_an", "moderate")}),
    ({"hb": 7.0}, 25, {("r_an", "moderate")}),
    ({"hb": 6.9}, 25, {("r_sevan", "high")}),         # severe anaemia hides plain anaemia
    # age boundaries
    ({}, 17, {("r_teen", "moderate")}),
    ({}, 18, set()),
    ({}, 35, set()),
    ({}, 36, {("r_old", "moderate")}),
    # several problems at once
    ({"bp_sys": 145, "hb": 6.5}, 40, {("r_highbp", "high"), ("r_sevan", "high"), ("r_old", "moderate")}),
], ids=[
    "all-normal",
    "sys-139", "sys-140",
    "dia-89", "dia-90",
    "hb-10.0", "hb-9.9", "hb-7.0", "hb-6.9",
    "age-17", "age-18", "age-35", "age-36",
    "combined",
])
def test_rule_boundaries(db, readings, age, expected):
    assert flags(risk_hits(db, Mother(age=age), make_visit(**readings))) == expected


def test_high_systolic_and_diastolic_give_two_hits(db):
    hits = risk_hits(db, Mother(age=25), make_visit(bp_sys=150, bp_dia=95))
    assert sorted(hit["param"] for hit in hits) == ["bp_dia", "bp_sys"]


def test_hit_reports_the_reading_that_tripped_it(db):
    [hit] = risk_hits(db, Mother(age=25), make_visit(bp_sys=146))
    assert hit["id"] == "r1"
    assert hit["value"] == 146


def test_without_a_visit_only_age_is_checked(db):
    assert flags(risk_hits(db, Mother(age=40), None)) == {("r_old", "moderate")}
    assert risk_hits(db, Mother(age=25), None) == []


def test_edited_threshold_is_used_straight_away(db):
    db.get(RiskRule, "r1").value = 150
    db.commit()
    assert risk_hits(db, Mother(age=25), make_visit(bp_sys=145)) == []
    assert flags(risk_hits(db, Mother(age=25), make_visit(bp_sys=150))) == {("r_highbp", "high")}


# ------------------------------------------------------- pregnancy_assessment

def assess(db, age=25, visits=()):
    return pregnancy_assessment(db, Pregnancy(mother=Mother(age=age), visits=list(visits)))


def test_no_visits_and_normal_age_is_normal(db):
    result = assess(db)
    assert result["level"] == "normal"
    assert result["reasons"] == []
    assert result["last_visit_id"] is None


def test_no_visits_but_age_over_35_is_moderate(db):
    result = assess(db, age=38)
    assert result["level"] == "moderate"
    assert result["reasons"] == ["r_old"]


def test_high_beats_moderate(db):
    result = assess(db, visits=[make_visit(bp_sys=145, hb=9.0)])
    assert result["level"] == "high"
    assert set(result["reasons"]) == {"r_highbp", "r_an"}


def test_reasons_are_not_repeated(db):
    # Two BP rules fire, but the reason "High BP" should be listed once.
    result = assess(db, visits=[make_visit(bp_sys=150, bp_dia=95)])
    assert len(result["hits"]) == 2
    assert result["reasons"] == ["r_highbp"]


def test_only_the_latest_recorded_visit_counts(db):
    # High BP at visit 1, normal at visit 2: the current assessment is normal.
    result = assess(db, visits=[make_visit(no=1, bp_sys=150), make_visit(no=2)])
    assert result["level"] == "normal"
    assert result["last_visit_id"] == "v2"


def test_latest_means_highest_visit_number_not_list_order(db):
    result = assess(db, visits=[make_visit(no=2, bp_sys=150), make_visit(no=1)])
    assert result["level"] == "high"
    assert result["last_visit_id"] == "v2"


def test_unrecorded_visits_are_ignored(db):
    result = assess(db, visits=[make_visit(no=1), make_visit(no=2, done=False, bp_sys=180)])
    assert result["level"] == "normal"
    assert result["last_visit_id"] == "v1"
