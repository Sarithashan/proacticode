def filter_even(numbers):
    result = []
    for n in numbers:
        if n % 2 == 0:
            result.append(n)
    return result


def square_all(numbers):
    result = []
    for n in numbers:
        result.append(n * n)
    return result


def contains_negative(numbers):
    for n in numbers:
        if n < 0:
            return True
    return False


def first_or_none(items):
    if items == None:
        return None
    if len(items) == 0:
        return None
    return items[0]


def all_positive(numbers):
    for n in numbers:
        if not n > 0:
            return False
    return True


def invert_dict(d):
    out = {}
    for k in d.keys():
        out[d[k]] = k
    return out
