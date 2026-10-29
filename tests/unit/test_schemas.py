"""Unit tests for the request schemas in backend/schemas.py.

The schemas are the first gate: bad input is rejected before any route code runs.
Each test builds a schema object directly; ValidationError means the input was refused.
"""
import pytest
from pydantic import ValidationError

from backend.schemas import MotherCreate, PregnancyCreate, ReviewCreate, RiskRuleUpdate, VisitRecord

pytestmark = pytest.mark.unit


def mother(**overrides):
    data = {"name": "Test Mother", "age": 24, "phone": "9825076143", "village": "bakrol", "asha_id": "u1"}
    data.update(overrides)
    return data


def visit(**overrides):
    data = {"bp_sys": 118, "bp_dia": 76, "hb": 11.0, "weight": 55.0}
    data.update(overrides)
    return data


# --------------------------------------------------------------- MotherCreate

@pytest.mark.parametrize("phone", ["6000000000", "9999999999", "9825076143"])
def test_valid_indian_mobile_numbers(phone):
    assert MotherCreate(**mother(phone=phone)).phone == phone


@pytest.mark.parametrize("phone", [
    "5825076143",      # Indian mobiles start with 6-9
    "982507614",       # 9 digits
    "98250761430",     # 11 digits
    "98250a6143",      # letter
    "+919825076143",   # country code not accepted
    "",
])
def test_invalid_mobile_numbers_are_rejected(phone):
    with pytest.raises(ValidationError):
        MotherCreate(**mother(phone=phone))


@pytest.mark.parametrize("age", [12, 55])
def test_age_limits_are_allowed(age):
    assert MotherCreate(**mother(age=age)).age == age


@pytest.mark.parametrize("age", [11, 56, -1])
def test_age_outside_limits_is_rejected(age):
    with pytest.raises(ValidationError):
        MotherCreate(**mother(age=age))


def test_name_can_be_given_in_both_languages():
    name = {"en": "Asha Thakor", "gu": "આશા ઠાકોર"}
    assert MotherCreate(**mother(name=name)).name == name


def test_blood_group_defaults_to_unknown():
    assert MotherCreate(**mother()).blood_group == "Unknown"


def test_empty_village_is_rejected():
    with pytest.raises(ValidationError):
        MotherCreate(**mother(village=""))


# ------------------------------------------------------------ PregnancyCreate

def test_gravida_and_parity_default_to_first_pregnancy():
    record = PregnancyCreate(mother=mother(), lmp="2026-08-01")
    assert (record.gravida, record.parity) == (1, 0)


@pytest.mark.parametrize("field, value", [("gravida", 0), ("parity", -1), ("lmp", "not-a-date")])
def test_invalid_pregnancy_fields_are_rejected(field, value):
    data = {"mother": mother(), "lmp": "2026-08-01", field: value}
    with pytest.raises(ValidationError):
        PregnancyCreate(**data)


# ---------------------------------------------------------------- VisitRecord

@pytest.mark.parametrize("field, value", [
    ("bp_sys", 60), ("bp_sys", 250),
    ("bp_dia", 30), ("bp_dia", 160),
    ("hb", 2.1), ("hb", 20),
    ("weight", 25), ("weight", 150),
    ("notes", "x" * 2000),
])
def test_readings_at_the_limits_are_accepted(field, value):
    assert getattr(VisitRecord(**visit(**{field: value})), field) == value


@pytest.mark.parametrize("field, value", [
    ("bp_sys", 59), ("bp_sys", 251), ("bp_sys", 118.5),
    ("bp_dia", 29), ("bp_dia", 161),
    ("hb", 2), ("hb", 20.1),          # Hb must be MORE than 2
    ("weight", 24.9), ("weight", 150.1),
    ("notes", "x" * 2001),
])
def test_readings_outside_the_limits_are_rejected(field, value):
    with pytest.raises(ValidationError):
        VisitRecord(**visit(**{field: value}))


@pytest.mark.parametrize("missing", ["bp_sys", "bp_dia", "hb", "weight"])
def test_every_reading_is_required(missing):
    data = visit()
    del data[missing]
    with pytest.raises(ValidationError):
        VisitRecord(**data)


def test_notes_are_optional():
    assert VisitRecord(**visit()).notes == ""


# --------------------------------------------------------------- ReviewCreate

@pytest.mark.parametrize("decision", ["dRoutine", "dPhc", "dRefer"])
def test_the_three_decisions_are_accepted(decision):
    assert ReviewCreate(by_id="u3", decision=decision, text="ok").decision == decision


@pytest.mark.parametrize("decision, text", [
    ("dMaybe", "ok"),          # not one of the three decisions
    ("refer", "ok"),           # wrong spelling of a real one
    ("dRefer", ""),            # empty note
    ("dRefer", "x" * 2001),    # note too long
])
def test_invalid_reviews_are_rejected(decision, text):
    with pytest.raises(ValidationError):
        ReviewCreate(by_id="u3", decision=decision, text=text)


# ------------------------------------------------------------- RiskRuleUpdate

@pytest.mark.parametrize("value", [0, 140, 300])
def test_rule_values_in_range_are_accepted(value):
    assert RiskRuleUpdate(value=value).value == value


@pytest.mark.parametrize("value", [-0.1, 300.1])
def test_rule_values_out_of_range_are_rejected(value):
    with pytest.raises(ValidationError):
        RiskRuleUpdate(value=value)
