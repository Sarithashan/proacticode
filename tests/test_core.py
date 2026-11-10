"""Unit tests for ProactiCode's own modules (run with: pytest tests -q)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from proacticode import config, gate, risk  # noqa: E402
from proacticode.analyzer import analyze  # noqa: E402
from proacticode.duplication import find_duplicates  # noqa: E402
from proacticode.pipeline import proacticode  # noqa: E402
from proacticode.recommend import recommend  # noqa: E402

TASKS = ROOT / "benchmark" / "tasks"


def base_metrics(**over):
    m = {"ruff_high": 0, "ruff_medium": 0, "ruff_low": 0, "ruff_total": 0, "bandit_high": 0,
         "bandit_medium": 0, "bandit_low": 0, "max_cc": 2, "dup_ratio": 0.0, "max_func_len": 5,
         "mi": 90.0, "tests_failed": 0, "has_tests": True, "pass_rate": 1.0, "coverage": 1.0}
    m.update(over)
    return m


def test_weights_sum_to_one():
    assert sum(config.WEIGHTS.values()) == pytest.approx(1.0)


def test_risk_is_between_0_and_100_and_monotonic():
    good = risk.assess(base_metrics())
    bad = risk.assess(base_metrics(ruff_high=5, ruff_medium=10, max_cc=30, dup_ratio=0.5,
                                   max_func_len=120, bandit_high=3, pass_rate=0.0, coverage=0.0, mi=10.0),
                      change_lines=500)
    assert 0 <= good["score"] < bad["score"] <= 100
    assert good["category"] == "Low" and bad["category"] == "High"


def test_duplicate_detector_finds_copy_paste():
    block = "a = 1\nb = a + 2\nc = b * 3\nd = c - 4\n"
    ratio, blocks = find_duplicates(block + "x = 0\n" + block)
    assert ratio > 0.5 and blocks
    assert find_duplicates("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n")[0] == 0.0


def test_gate_blocks_on_failing_tests_even_if_risk_low():
    m = base_metrics(tests_failed=1, pass_rate=0.5)
    decision, _ = gate.decide(m, risk.assess(m))
    assert decision == "Request changes"


def test_gate_blocks_on_high_security_finding():
    m = base_metrics(bandit_high=1)
    assert gate.decide(m, risk.assess(m))[0] == "Request changes"


def test_gate_approves_clean_code():
    m = base_metrics()
    assert gate.decide(m, risk.assess(m))[0] == "Approve"


def test_analyzer_and_recommendations_on_real_task():
    m, findings = analyze(TASKS / "t05_file_parser")
    assert m["tests_failed"] == 0 and m["bandit_medium"] >= 1
    rules = {r["rule"] for r in recommend(findings)}
    assert {"E722", "B307"} <= rules


def test_pipeline_improves_a_messy_task_without_breaking_tests():
    res = proacticode(TASKS / "t01_grade_calculator", log=False)
    assert res["after"]["tests_failed"] == 0
    assert res["after"]["ruff_total"] < res["before"]["ruff_total"]
    assert res["risk_after"]["score"] <= res["risk_before"]["score"]


def test_pipeline_rejects_fix_that_breaks_behaviour():
    res = proacticode(TASKS / "t15_stress_null_object", log=False)
    assert res["reverted"] and res["after"]["tests_failed"] == 0


def test_original_task_files_are_never_modified():
    path = TASKS / "t01_grade_calculator" / "solution.py"
    before = path.read_text()
    proacticode(TASKS / "t01_grade_calculator", log=False)
    assert path.read_text() == before


def test_missing_tool_raises_instead_of_reporting_zero_findings(monkeypatch):
    from proacticode import analyzer
    monkeypatch.setattr(analyzer, "_tool", lambda name: ["definitely_not_a_real_tool"])
    with pytest.raises(analyzer.ToolError):
        analyzer.check_tools(force=True)
    monkeypatch.undo()
    analyzer.check_tools(force=True)
