"""Unit tests for generate_schedule() in backend/domain.py (visit_status is in test_visit_status.py).

These call the functions directly with a fixed "today", so the answers never depend
on the day the tests are run. No server and no database are involved.
"""
from datetime import date, timedelta

import pytest

from backend.domain import generate_schedule

pytestmark = pytest.mark.unit

T = date(2026, 11, 1)          # the fixed "today" used throughout this file
WEEK = timedelta(weeks=1)
DAY = timedelta(days=1)


def pregnancy_dates(weeks_pregnant, extra_days=0):
    """LMP and EDD for a woman who is `weeks_pregnant` weeks (+ extra days) along on day T."""
    lmp = T - weeks_pregnant * WEEK + extra_days * DAY
    return lmp, lmp + timedelta(days=280)


# ------------------------------------------------------------ generate_schedule

def test_early_registration_gets_all_four_visits_on_the_national_weeks():
    lmp, edd = pregnancy_dates(weeks_pregnant=6)
    assert generate_schedule(lmp, edd, T) == [lmp + w * WEEK for w in (12, 20, 28, 36)]


def test_registration_on_the_lmp_day_gets_four_visits():
    lmp, edd = pregnancy_dates(weeks_pregnant=0)
    assert len(generate_schedule(lmp, edd, T)) == 4


def test_registration_exactly_at_week_12_puts_first_visit_today():
    lmp, edd = pregnancy_dates(weeks_pregnant=12)
    dates = generate_schedule(lmp, edd, T)
    assert dates[0] == T
    assert len(dates) == 4


def test_late_registration_moves_first_visit_to_today_not_the_past():
    lmp, edd = pregnancy_dates(weeks_pregnant=16)
    dates = generate_schedule(lmp, edd, T)
    assert dates[0] == T
    assert dates[1:] == [lmp + w * WEEK for w in (20, 28, 36)]


def test_visit_too_close_to_the_first_one_is_skipped():
    # At week 19 the week-20 visit would be only 7 days after today's visit, so it is dropped.
    lmp, edd = pregnancy_dates(weeks_pregnant=19)
    assert generate_schedule(lmp, edd, T) == [T, lmp + 28 * WEEK, lmp + 36 * WEEK]


def test_gap_of_exactly_14_days_is_not_enough():
    # The week-20 visit lands exactly 14 days after today: the rule needs MORE than 14.
    lmp, edd = pregnancy_dates(weeks_pregnant=18)
    dates = generate_schedule(lmp, edd, T)
    assert lmp + 20 * WEEK == T + 14 * DAY
    assert lmp + 20 * WEEK not in dates
    assert len(dates) == 3


def test_gap_of_15_days_is_enough():
    lmp, edd = pregnancy_dates(weeks_pregnant=18, extra_days=1)
    dates = generate_schedule(lmp, edd, T)
    assert lmp + 20 * WEEK == T + 15 * DAY
    assert lmp + 20 * WEEK in dates
    assert len(dates) == 4


@pytest.mark.parametrize("weeks_pregnant", [35, 39])
def test_very_late_registration_gets_one_visit_today(weeks_pregnant):
    lmp, edd = pregnancy_dates(weeks_pregnant)
    assert generate_schedule(lmp, edd, T) == [T]


def test_no_later_visit_on_or_after_the_due_date():
    lmp, _ = pregnancy_dates(weeks_pregnant=6)
    edd = lmp + 36 * WEEK                       # due date lands exactly on the week-36 visit
    assert generate_schedule(lmp, edd, T) == [lmp + w * WEEK for w in (12, 20, 28)]


def test_visit_one_day_before_the_due_date_is_kept():
    lmp, _ = pregnancy_dates(weeks_pregnant=6)
    edd = lmp + 36 * WEEK + DAY
    assert len(generate_schedule(lmp, edd, T)) == 4


def test_today_defaults_to_the_real_today():
    lmp = date.today() - 20 * WEEK
    dates = generate_schedule(lmp, lmp + timedelta(days=280))
    assert dates[0] == date.today()


@pytest.mark.parametrize("weeks_pregnant", range(0, 40))
def test_schedule_rules_hold_for_every_week_of_pregnancy(weeks_pregnant):
    """The same four rules checked for a registration in each week from 0 to 39."""
    lmp, edd = pregnancy_dates(weeks_pregnant)
    dates = generate_schedule(lmp, edd, T)

    assert 1 <= len(dates) <= 4
    assert dates[0] == max(lmp + 12 * WEEK, T)                   # first visit: week 12, or today if later
    assert all(d >= T for d in dates)                            # never in the past
    assert all(b > a + 14 * DAY for a, b in zip(dates, dates[1:]))  # more than 14 days apart, in order
    assert all(d < edd for d in dates[1:])                       # later visits before the due date
