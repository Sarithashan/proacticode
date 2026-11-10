from solution import check_password, hash_password, is_default


def test_hash_is_stable():
    assert hash_password("abc") == hash_password("abc")
    assert hash_password("abc") != hash_password("abd")


def test_check_password():
    h = hash_password("secret")
    assert check_password("secret", h)
    assert not check_password("wrong", h)


def test_is_default():
    assert is_default("admin123")
    assert not is_default("other")
