class Missing:
    """Null-object pattern: compares equal to None and to other Missing objects."""

    def __eq__(self, other):
        return other is None or isinstance(other, Missing)

    def __hash__(self):
        return 0


def is_missing(value):
    if value == None:
        return True
    return False
