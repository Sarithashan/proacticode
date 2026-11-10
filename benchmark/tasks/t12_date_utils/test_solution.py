import pytest

from solution import days_in_month, is_leap


@pytest.mark.parametrize("year,leap", [(2024, True), (2023, False), (1900, False), (2000, True)])
def test_leap(year, leap):
    assert is_leap(year) is leap


@pytest.mark.parametrize("month,days", [(1, 31), (4, 30), (6, 30), (9, 30), (11, 30), (12, 31)])
def test_days(month, days):
    assert days_in_month(month, 2023) == days


def test_february():
    assert days_in_month(2, 2024) == 29
    assert days_in_month(2, 2023) == 28


def test_bad_month():
    with pytest.raises(ValueError):
        days_in_month(13, 2023)
