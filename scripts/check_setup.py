"""Run this FIRST. It proves that every tool ProactiCode needs works in your Python environment.

    python scripts/check_setup.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from proacticode.analyzer import ToolError, _tool, analyze, check_tools  # noqa: E402


def version(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()[0]
    except Exception as exc:  # noqa: BLE001
        return f"NOT FOUND ({exc})"


print("Python      :", sys.executable)
print("ruff        :", version(_tool("ruff") + ["--version"]))
print("bandit      :", version(_tool("bandit") + ["--version"]))
print("pytest      :", version([sys.executable, "-m", "pytest", "--version"]))
try:
    check_tools(force=True)
except ToolError as exc:
    print("\nSETUP PROBLEM:", exc)
    sys.exit(1)

# end-to-end self test: a file with known problems must produce known findings
tmp = Path(tempfile.mkdtemp())
(tmp / "sample.py").write_text("import os\n\ndef f(x):\n    if x == None:\n        return eval('1')\n    return 0\n")
m, findings = analyze(tmp, with_tests=False)
codes = {f["code"] for f in findings}
print("\nFindings on the self-test file:", sorted(codes))
if {"F401", "E711", "B307"} <= codes:
    print("\nSETUP OK - Ruff and Bandit are really finding problems.")
else:
    print("\nSETUP PROBLEM: expected F401, E711 and B307 but got", sorted(codes))
    sys.exit(1)
