"""Unit tests for visit_status(): done / missed / due (within 7 days) / upcoming."""
from datetime import date, timedelta

import pytest

from backend.domain import visit_status
from backend.models import ANCVisit

pytestmark = pytest.mark.unit

TODAY = date(2026, 11, 1)  # fixed date so results never depend on when the tests run


def visit(days_from_today, recorded=False):
    return ANCVisit(
        scheduled_date=TODAY + timedelta(days=days_from_today),
        actual_date=TODAY if recorded else None,
    )


@pytest.mark.parametrize("days, expected", [
    (-30, "missed"),
    (-1, "missed"),     # yesterday: the latest day that counts as missed
    (0, "due"),         # today is due, not missed
    (1, "due"),
    (7, "due"),         # boundary: exactly one week away is still due
    (8, "upcoming"),    # boundary: one day past the window
    (60, "upcoming"),
])
def test_unrecorded_visit_status_by_distance(days, expected):
    assert visit_status(visit(days), TODAY) == expected


@pytest.mark.parametrize("days", [-30, -1, 0, 7, 60])
def test_recorded_visit_is_always_done(days):
    # Once readings are saved, the scheduled date no longer matters.
    assert visit_status(visit(days, recorded=True), TODAY) == "done"


def test_defaults_to_real_today_when_no_date_given():
    v = ANCVisit(scheduled_date=date.today(), actual_date=None)
    assert visit_status(v) == "due"
