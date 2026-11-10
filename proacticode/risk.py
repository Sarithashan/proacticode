"""Phase 2 - rule-based technical-debt risk score.

R = 100 * sum_i (w_i * x_i), where every x_i is a quality indicator
normalised to [0, 1] (0 = healthy, 1 = worst). Weights live in config.py.
"""
from . import config


def _clip(v):
    return max(0.0, min(1.0, v))


def indicators(m, change_lines=0):
    """Map raw metrics `m` to normalised indicators x_i in [0, 1]."""
    weighted_warn = 3 * (m["ruff_high"]) + 1 * m["ruff_medium"] + 0.25 * m["ruff_low"]
    sec = 3 * m["bandit_high"] + 2 * m["bandit_medium"] + 1 * m["bandit_low"]
    if m.get("has_tests") and m.get("pass_rate") is not None:
        x_tests = 1.0 - m["pass_rate"]
        x_cov = 1.0 - (m["coverage"] if m.get("coverage") is not None else 0.0)
    else:  # no tests = unknown behaviour: treat as moderately risky
        x_tests, x_cov = 0.5, 1.0
    return {
        "warnings": _clip(weighted_warn / 15.0),
        "complexity": _clip((m["max_cc"] - 5) / 15.0),
        "duplication": _clip(m["dup_ratio"] / 0.30),
        "func_length": _clip((m["max_func_len"] - 20) / 60.0),
        "security": _clip(sec / 6.0),
        "tests": _clip(x_tests),
        "coverage": _clip(x_cov),
        "maintainability": _clip((65.0 - m["mi"]) / 65.0),
        "change_size": _clip(change_lines / 100.0),
    }


def category(score):
    if score < config.LOW_MAX:
        return "Low"
    if score < config.MODERATE_MAX:
        return "Moderate"
    return "High"


def assess(m, change_lines=0):
    """Return {'score', 'category', 'indicators', 'contributions'}."""
    x = indicators(m, change_lines)
    contrib = {k: round(100 * config.WEIGHTS[k] * x[k], 2) for k in x}
    score = round(sum(contrib.values()), 2)
    return {"score": score, "category": category(score), "indicators": x,
            "contributions": contrib}
