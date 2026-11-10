import pytest

from solution import Account


def test_deposit_and_withdraw():
    a = Account("x", 100)
    assert a.deposit(50) == 150
    assert a.withdraw(30) == 120
    assert a.history == [("deposit", 50), ("withdraw", 30)]


def test_validation():
    a = Account("x", 10)
    with pytest.raises(TypeError):
        a.deposit("5")
    with pytest.raises(ValueError):
        a.deposit(-1)
    with pytest.raises(ValueError):
        a.withdraw(11)


def test_fee_can_overdraw():
    a = Account("x", 5)
    assert a.fee(10) == -5
