import os


def parse_number(text):
    try:
        value = eval(text)
        return value
    except:
        return None


def read_lines(path):
    try:
        with open(path) as f:
            lines = f.readlines()
            count = len(lines)
            return [line.strip() for line in lines]
    except:
        return []
