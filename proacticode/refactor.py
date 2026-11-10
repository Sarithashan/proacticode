"""Phase 3/4 - apply mechanical fixes in a SEPARATE working copy.

Only Ruff autofixes from config.FIX_RULES are applied. Some are "unsafe"
(they may change behaviour in rare cases); that is deliberate - the quality
gate re-runs the tests and rejects the change if behaviour broke.
"""
import difflib
import shutil
import subprocess
from pathlib import Path

from . import config
from .analyzer import _tool, source_files


def copy_workdir(src, dst):
    if Path(dst).exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
    return Path(dst)


def apply_fixes(workdir):
    """Run ruff --fix on the working copy. Returns number of changed lines."""
    files = source_files(workdir)
    before = {f: f.read_text().splitlines() for f in files}
    cmd = _tool("ruff") + ["check", "--config", str(config.RUFF_CONFIG), "--no-cache", "--fix",
                           "--unsafe-fixes", "--select", ",".join(config.FIX_RULES), "--exit-zero",
                           "--quiet"] + [str(f) for f in files]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        from .analyzer import ToolError
        raise ToolError(f"ruff --fix failed (exit {proc.returncode}): {proc.stderr.strip()[:300]}")
    changed = 0
    for f in files:
        after = f.read_text().splitlines()
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, before[f], after).get_opcodes():
            if tag != "equal":
                changed += max(i2 - i1, j2 - j1)
    return changed


def unified_diff(orig_dir, new_dir):
    """Human-readable diff of all source files (used by the dashboard)."""
    out = []
    for f in source_files(orig_dir):
        g = Path(new_dir) / f.relative_to(orig_dir)
        out += difflib.unified_diff(f.read_text().splitlines(), g.read_text().splitlines(),
                                    f"original/{f.name}", f"proposed/{f.name}", lineterm="")
    return "\n".join(out)
