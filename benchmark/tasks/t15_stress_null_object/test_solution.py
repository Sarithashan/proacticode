from solution import Missing, is_missing


def test_none_is_missing():
    assert is_missing(None)


def test_null_object_is_missing():
    assert is_missing(Missing())


def test_regular_values_are_not_missing():
    assert not is_missing(0)
    assert not is_missing("")
