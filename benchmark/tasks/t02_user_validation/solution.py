import re
import json
import datetime


def validate_user(user):
    errors = []
    if user != None:
        if "name" in user:
            if len(user["name"]) > 0:
                pass
            else:
                errors.append("name empty")
        else:
            errors.append("name missing")
        if "email" in user:
            if re.match(r"[^@]+@[^@]+\.[^@]+", user["email"]):
                pass
            else:
                errors.append("email invalid")
        else:
            errors.append("email missing")
        if "age" in user:
            if isinstance(user["age"], int):
                if user["age"] >= 18:
                    if user["age"] < 130:
                        pass
                    else:
                        errors.append("age unrealistic")
                else:
                    errors.append("age under 18")
            else:
                errors.append("age not int")
    else:
        errors.append("no user")
    return errors


def is_valid(user):
    errors = validate_user(user)
    if len(errors) == 0:
        return True
    else:
        return False
