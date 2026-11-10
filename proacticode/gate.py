"""Phase 4 - quality gate: Approve / Flag for review / Request changes."""
from . import config


def trend(before, after, key, lower_is_better=True):
    d = after - before
    if abs(d) < 1e-9:
        return "preserved"
    return "improved" if (d < 0) == lower_is_better else "worsened"


def change_verdict(risk_before, risk_after):
    d = risk_after - risk_before
    if d < -config.IMPROVE_EPS:
        return "improved"
    if d > config.IMPROVE_EPS:
        return "worsened"
    return "preserved"


def decide(m, risk):
    """Decision for the FINAL version of the code. Returns (decision, reasons)."""
    blocking, review = [], []
    if m.get("tests_failed", 0) > 0:
        blocking.append(f"{m['tests_failed']} required test(s) failing")
    if m["bandit_high"] > 0:
        blocking.append(f"{m['bandit_high']} high-severity security finding(s)")
    if m["ruff_high"] > 0:
        blocking.append(f"{m['ruff_high']} high-severity static-analysis error(s)")
    if blocking:
        return "Request changes", blocking
    if risk["category"] != "Low":
        review.append(f"risk category is {risk['category']} (score {risk['score']})")
    if m["bandit_medium"] > 0:
        review.append(f"{m['bandit_medium']} medium-severity security finding(s)")
    if m["max_cc"] > config.GATE_MAX_CC:
        review.append(f"max cyclomatic complexity {m['max_cc']} > {config.GATE_MAX_CC}")
    if m["dup_ratio"] > config.GATE_MAX_DUP:
        review.append(f"{m['dup_ratio']:.0%} duplicated lines")
    if m["ruff_total"] > 0:
        review.append(f"{m['ruff_total']} unresolved warning(s)")
    if not m.get("has_tests"):
        review.append("no tests available to validate behaviour")
    if review:
        return "Flag for review", review
    return "Approve", ["all configured checks passed"]
