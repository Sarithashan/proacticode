from solution import Inventory


def make():
    inv = Inventory()
    inv.add("pen", 10)
    inv.add("ink", 2)
    return inv


def test_add_accumulates():
    inv = make()
    inv.add("pen", 5)
    assert inv.items["pen"] == 15


def test_remove_rules():
    inv = make()
    assert inv.remove("pen", 4)
    assert not inv.remove("pen", 100)
    assert not inv.remove("ghost", 1)


def test_remove_to_zero_deletes():
    inv = make()
    assert inv.remove("ink", 2)
    assert not inv.in_stock("ink")


def test_low_stock():
    assert make().low_stock(5) == ["ink"]
