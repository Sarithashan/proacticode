import pytest

from solution import calculate_grade, is_passing


@pytest.mark.parametrize("score,grade", [(95, "A"), (90, "A"), (85, "B"), (75, "C"),
                                          (65, "D"), (10, "F"), (0, "F"), (100, "A")])
def test_grades(score, grade):
    assert calculate_grade(score) == grade


@pytest.mark.parametrize("bad", [-1, 101, None])
def test_invalid(bad):
    with pytest.raises(ValueError):
        calculate_grade(bad)


def test_passing():
    assert is_passing(60)
    assert not is_passing(59)
