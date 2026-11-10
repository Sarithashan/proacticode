from solution import checkout, preview

ITEMS = [{"price": 100, "qty": 2}, {"price": 50, "qty": 1}]


def test_preview_by_type():
    assert preview(ITEMS, "gold") == 200.0
    assert preview(ITEMS, "silver") == 225.0
    assert preview(ITEMS, "regular") == 250.0


def test_checkout_adds_tax():
    assert checkout(ITEMS, "regular") == 295.0


def test_empty_cart():
    assert checkout([], "gold") == 0
    assert preview([], "gold") == 0
