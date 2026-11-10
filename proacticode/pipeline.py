"""ProactiCode end-to-end pipeline (analysis -> risk -> recommend -> fix -> validate -> gate)
and the comparison baselines used in the experiments."""
import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from . import gate, risk
from .analyzer import analyze
from .recommend import recommend
from .refactor import apply_fixes, copy_workdir, unified_diff

HISTORY_FILE = Path(__file__).resolve().parent.parent / "results" / "history.jsonl"


def _log_history(task, system, m, r, decision):
    try:
        HISTORY_FILE.parent.mkdir(exist_ok=True)
        rec = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "task": task,
               "system": system, "risk": r["score"], "category": r["category"],
               "warnings": m["ruff_total"], "max_cc": m["max_cc"], "decision": decision}
        with open(HISTORY_FILE, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
def baseline_a(task_dir):
    """A: static analysis only. Raw warnings, no score, no recommendations, no tests."""
    t0 = time.perf_counter()
    m, findings = analyze(task_dir, with_tests=False)
    return {"system": "A_static_only", "before": m, "after": m, "findings": findings,
            "risk_before": None, "risk_after": None, "decision": None, "reverted": False,
            "regression": False, "changed_lines": 0, "n_recommendations": 0,
            "time_s": time.perf_counter() - t0}


def baseline_b(task_dir):
    """B: A + tests + rule-based risk score and category. No recommendations or fixes."""
    t0 = time.perf_counter()
    m, findings = analyze(task_dir)
    r = risk.assess(m)
    return {"system": "B_rule_risk", "before": m, "after": m, "findings": findings,
            "risk_before": r, "risk_after": r, "decision": None, "reverted": False,
            "regression": False, "changed_lines": 0, "n_recommendations": 0,
            "time_s": time.perf_counter() - t0}


def naive_autofix(task_dir, keep_workdir=False):
    """C (ablation): apply the same fixes WITHOUT test validation or reverting."""
    t0 = time.perf_counter()
    m0, f0 = analyze(task_dir)
    r0 = risk.assess(m0)
    work = copy_workdir(task_dir, Path(tempfile.mkdtemp(prefix="pc_naive_")) / "w")
    changed = apply_fixes(work)
    m1, f1 = analyze(work)
    r1 = risk.assess(m1, change_lines=changed)
    regression = m1["tests_failed"] > m0["tests_failed"]
    return {"system": "C_naive_autofix", "before": m0, "after": m1, "findings": f1,
            "risk_before": r0, "risk_after": r1, "decision": None, "reverted": False,
            "regression": regression, "changed_lines": changed,
            "n_recommendations": 0, "time_s": time.perf_counter() - t0}


def proacticode(task_dir, task_name=None, log=True):
    """D: the full proposed framework."""
    t0 = time.perf_counter()
    task_dir = Path(task_dir)
    # 1) analyse original (kept untouched)
    m0, f0 = analyze(task_dir)
    r0 = risk.assess(m0)
    recs = recommend(f0)
    # 2) apply mechanical fixes in a separate working copy
    work = copy_workdir(task_dir, Path(tempfile.mkdtemp(prefix="pc_work_")) / "w")
    changed = apply_fixes(work)
    # 3) re-analyse + re-run tests on the modified copy
    m1, f1 = analyze(work)
    # 4) validate: reject the change if it breaks behaviour
    regression = m1["tests_failed"] > m0["tests_failed"]
    reverted = regression
    if reverted:
        m1, f1, changed_eff = m0, f0, 0
        diff = ""
        note = "automatic fixes rejected: they broke previously passing tests"
    else:
        changed_eff = changed
        diff = unified_diff(task_dir, work)
        note = "automatic fixes accepted" if changed else "no mechanical fixes available"
    r1 = risk.assess(m1, change_lines=changed_eff)
    decision, reasons = gate.decide(m1, r1)
    out = {
        "system": "D_proacticode", "before": m0, "after": m1, "findings": f1,
        "findings_before": f0, "recommendations": recs, "n_recommendations": len(recs),
        "risk_before": r0, "risk_after": r1, "verdict": gate.change_verdict(r0["score"], r1["score"]),
        "decision": decision, "reasons": reasons, "note": note, "diff": diff,
        "reverted": reverted, "regression_caught": regression, "regression": False,
        "changed_lines": changed_eff, "time_s": time.perf_counter() - t0,
    }
    if log:
        _log_history(task_name or task_dir.name, "D_proacticode", m1, r1, decision)
    return out
