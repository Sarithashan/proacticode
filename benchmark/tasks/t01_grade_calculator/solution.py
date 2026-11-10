import os
import sys


def calculate_grade(score):
    if score is not None:
        if score >= 0:
            if score <= 100:
                if score >= 90:
                    return "A"
                else:
                    if score >= 80:
                        return "B"
                    else:
                        if score >= 70:
                            return "C"
                        else:
                            if score >= 60:
                                return "D"
                            else:
                                return "F"
            else:
                raise ValueError("score too high")
        else:
            raise ValueError("score too low")
    else:
        raise ValueError("score is None")


def is_passing(score):
    if calculate_grade(score) == "F":
        return False
    else:
        return True
