"""Phase 1 - code collection and quality analysis.

Runs Ruff (static analysis), Radon (complexity / maintainability),
Bandit (security), a duplicate-code check and Pytest + coverage, then
returns a flat metrics dictionary plus a list of individual findings.
"""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze as raw_analyze

from . import config
from .duplication import find_duplicates


class ToolError(RuntimeError):
    """Raised when a required analysis tool is missing or broken.

    Without this, a missing tool would look like 'no problems found'."""


def _tool(name):
    """Command prefix for a CLI tool (binary on PATH, else python -m)."""
    return [shutil.which(name)] if shutil.which(name) else [sys.executable, "-m", name]


_CHECKED = False


def check_tools(force=False):
    """Make sure Ruff, Bandit and Pytest can really run in THIS Python environment."""
    global _CHECKED
    if _CHECKED and not force:
        return
    checks = {"ruff": _tool("ruff") + ["--version"],
              "bandit": _tool("bandit") + ["--version"],
              "pytest": [sys.executable, "-m", "pytest", "--version"]}
    for name, cmd in checks.items():
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
        except OSError as exc:
            raise ToolError(f"Cannot run {name} ({exc}). Install it with: pip install {name}") from exc
        if proc.returncode != 0:
            raise ToolError(f"{name} is not working in this Python environment ({sys.executable}). "
                            f"Install it with: pip install {name}\n{proc.stderr.strip()}")
    _CHECKED = True


def source_files(workdir):
    """Python files under workdir that are NOT tests."""
    files = []
    for p in sorted(Path(workdir).rglob("*.py")):
        if p.name.startswith("test_") or p.name.endswith("_test.py") or p.name == "conftest.py":
            continue
        files.append(p)
    return files


def severity_of_ruff(code):
    if code in config.HIGH_RULES:
        return "high"
    if code.startswith(config.LOW_RULE_PREFIXES):
        return "low"
    return "medium"


# --------------------------------------------------------------------------
def run_ruff(files):
    cmd = _tool("ruff") + ["check", "--config", str(config.RUFF_CONFIG), "--no-cache",
                           "--output-format", "json"] + [str(f) for f in files]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0, 1):   # 0 = clean, 1 = findings, anything else = tool error
        raise ToolError(f"ruff failed (exit {proc.returncode}): {proc.stderr.strip()[:300]}")
    findings = []
    try:
        data = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise ToolError(f"ruff produced unreadable output: {proc.stdout[:200]}") from exc
    for d in data:
        code = d.get("code") or "E999"
        findings.append({
            "source": "ruff", "code": code, "message": d.get("message", ""),
            "file": os.path.basename(d.get("filename", "")),
            "line": d.get("location", {}).get("row", 0),
            "severity": severity_of_ruff(code), "function": None,
            "auto_fixable": d.get("fix") is not None,
        })
    return findings


def run_bandit(files):
    cmd = _tool("bandit") + ["-q", "-f", "json"] + [str(f) for f in files]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    findings = []
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        if files:
            raise ToolError(f"bandit produced unreadable output: {proc.stderr.strip()[:300]}") from exc
        data = {}
    for r in data.get("results", []):
        findings.append({
            "source": "bandit", "code": r.get("test_id"), "message": r.get("issue_text", ""),
            "file": os.path.basename(r.get("filename", "")), "line": r.get("line_number", 0),
            "severity": r.get("issue_severity", "LOW").lower(), "function": None,
            "auto_fixable": False,
        })
    return findings


def _function_lengths(tree):
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = node.end_lineno - node.lineno + 1
    return out


def run_complexity(files):
    """Radon cyclomatic complexity, maintainability index and function sizes."""
    findings, ccs, lens, mis, loc, sloc = [], [], [], [], 0, 0
    for f in files:
        src = Path(f).read_text()
        try:
            blocks = cc_visit(src)
            tree = ast.parse(src)
        except SyntaxError:
            continue
        flen = _function_lengths(tree)
        for b in blocks:
            ccs.append(b.complexity)
            if b.complexity > config.GATE_MAX_CC:
                findings.append({
                    "source": "radon", "code": "CC", "file": Path(f).name, "line": b.lineno,
                    "function": b.name, "severity": "medium", "auto_fixable": False,
                    "message": f"cyclomatic complexity {b.complexity}"})
        lens.extend(flen.values())
        mis.append(mi_visit(src, multi=True))
        raw = raw_analyze(src)
        loc += raw.loc
        sloc += raw.sloc
    return findings, {
        "loc": loc, "sloc": sloc, "n_functions": len(ccs),
        "max_cc": max(ccs) if ccs else 0,
        "mean_cc": round(sum(ccs) / len(ccs), 2) if ccs else 0.0,
        "n_cc_over10": sum(1 for c in ccs if c > config.GATE_MAX_CC),
        "max_func_len": max(lens) if lens else 0,
        "mi": round(sum(mis) / len(mis), 2) if mis else 100.0,
    }


def run_duplication(files):
    findings, ratios = [], []
    for f in files:
        ratio, blocks = find_duplicates(Path(f).read_text())
        ratios.append(ratio)
        for blk in blocks:
            findings.append({
                "source": "dup", "code": "DUP", "file": Path(f).name, "line": blk[0],
                "function": None, "severity": "medium", "auto_fixable": False,
                "message": "repeated block at lines " + ", ".join(str(n) for n in blk)})
    return findings, (max(ratios) if ratios else 0.0)


def run_tests(workdir, modules):
    """Run pytest (+coverage) in workdir. Returns dict with test statistics."""
    has_tests = any(Path(workdir).rglob("test_*.py"))
    empty = {"tests_total": 0, "tests_failed": 0, "tests_passed": 0,
             "pass_rate": None, "coverage": None, "has_tests": False}
    if not has_tests:
        return empty
    tmp = tempfile.mkdtemp(prefix="pc_")
    xml_path, cov_path = Path(tmp) / "r.xml", Path(tmp) / "cov.json"
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no",
           f"--junitxml={xml_path}", f"--cov-report=json:{cov_path}"]
    cmd += [f"--cov={m}" for m in modules]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, env=env,
                              timeout=config.TEST_TIMEOUT_S)
        if not xml_path.exists() and ("No module named" in proc.stderr or "unrecognized arguments" in proc.stderr
                                      or "No module named" in proc.stdout):
            raise ToolError("pytest or pytest-cov is missing. Install with: pip install pytest pytest-cov")
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp, ignore_errors=True)
        return dict(empty, has_tests=True, tests_total=1, tests_failed=1, pass_rate=0.0)
    res = dict(empty, has_tests=True)
    if xml_path.exists():
        root = ET.parse(xml_path).getroot()
        suite = root if root.tag == "testsuite" else root.find("testsuite")
        total = int(suite.get("tests", 0))
        bad = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
        res.update(tests_total=total, tests_failed=bad, tests_passed=total - bad,
                   pass_rate=(total - bad) / total if total else None)
    else:  # collection crashed (e.g. syntax error in the module)
        res.update(tests_total=1, tests_failed=1, tests_passed=0, pass_rate=0.0)
    if cov_path.exists():
        res["coverage"] = round(json.loads(cov_path.read_text())["totals"]["percent_covered"] / 100, 3)
    shutil.rmtree(tmp, ignore_errors=True)
    return res


# --------------------------------------------------------------------------
def analyze(workdir, with_tests=True):
    """Analyse every non-test .py file in workdir.

    Returns (metrics, findings). `metrics` is a flat dict, `findings` a list
    of dicts describing individual issues.
    """
    check_tools()
    t0 = time.perf_counter()
    files = source_files(workdir)
    findings = run_ruff(files)
    findings += run_bandit(files)
    cc_findings, cc_metrics = run_complexity(files)
    findings += cc_findings
    dup_findings, dup_ratio = run_duplication(files)
    findings += dup_findings

    def count(src, sev):
        return sum(1 for f in findings if f["source"] == src and f["severity"] == sev)

    m = dict(cc_metrics)
    m.update({
        "ruff_total": sum(1 for f in findings if f["source"] == "ruff"),
        "ruff_high": count("ruff", "high"), "ruff_medium": count("ruff", "medium"),
        "ruff_low": count("ruff", "low"),
        "bandit_high": count("bandit", "high"), "bandit_medium": count("bandit", "medium"),
        "bandit_low": count("bandit", "low"),
        "dup_ratio": round(dup_ratio, 3),
    })
    if with_tests:
        m.update(run_tests(workdir, [f.stem for f in files]))
    else:
        m.update({"tests_total": 0, "tests_failed": 0, "tests_passed": 0,
                  "pass_rate": None, "coverage": None, "has_tests": False})
    m["analysis_time_s"] = round(time.perf_counter() - t0, 3)
    return m, findings
