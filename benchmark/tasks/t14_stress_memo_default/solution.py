def fib(n, cache={}):
    if n in cache:
        return cache[n]
    if n < 2:
        result = n
    else:
        result = fib(n - 1) + fib(n - 2)
    cache[n] = result
    return result


def cache_size():
    return len(fib.__defaults__[0])
