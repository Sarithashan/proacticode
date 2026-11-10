from solution import cache_size, fib


def test_values():
    assert fib(10) == 55
    assert fib(1) == 1
    assert fib(0) == 0


def test_cache_is_shared_between_calls():
    fib(12)
    assert cache_size() >= 12
