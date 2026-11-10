from solution import (all_positive, contains_negative, filter_even, first_or_none,
                      invert_dict, square_all)


def test_filter_even():
    assert filter_even([1, 2, 3, 4]) == [2, 4]
    assert filter_even([]) == []


def test_square_all():
    assert square_all([1, 2, 3]) == [1, 4, 9]


def test_contains_negative():
    assert contains_negative([1, -2])
    assert not contains_negative([1, 2])


def test_first_or_none():
    assert first_or_none(None) is None
    assert first_or_none([]) is None
    assert first_or_none([7, 8]) == 7


def test_all_positive():
    assert all_positive([1, 2])
    assert not all_positive([1, 0])


def test_invert_dict():
    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
