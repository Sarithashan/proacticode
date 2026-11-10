from solution import add, identity, transpose


def test_transpose():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


def test_add():
    assert add([[1, 2], [3, 4]], [[1, 1], [1, 1]]) == [[2, 3], [4, 5]]


def test_identity():
    assert identity(3) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert identity(0) == []
