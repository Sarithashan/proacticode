from solution import is_valid, validate_user

GOOD = {"name": "Asha", "email": "asha@example.com", "age": 30}


def test_valid_user():
    assert validate_user(GOOD) == []
    assert is_valid(GOOD)


def test_missing_fields():
    assert validate_user({}) == ["name missing", "email missing"]


def test_bad_email_and_name():
    assert validate_user({"name": "", "email": "nope"}) == ["name empty", "email invalid"]


def test_age_rules():
    assert validate_user(dict(GOOD, age=10)) == ["age under 18"]
    assert validate_user(dict(GOOD, age=200)) == ["age unrealistic"]
    assert validate_user(dict(GOOD, age="x")) == ["age not int"]


def test_none_user():
    assert validate_user(None) == ["no user"]
    assert not is_valid(None)
