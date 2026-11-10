import hashlib

DEFAULT_PASSWORD = "admin123"


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def check_password(password, hashed):
    if hash_password(password) == hashed:
        return True
    else:
        return False


def is_default(password):
    return password == DEFAULT_PASSWORD
