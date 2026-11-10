"""Central configuration: thresholds, weights and rule lists.

All numbers here were fixed BEFORE running the experiments (see docs/design.md)
so that the risk score is not tuned to the benchmark results.
"""
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
RUFF_CONFIG = PKG_DIR / "ruff.toml"

# ---- severity mapping for Ruff rule codes ---------------------------------
HIGH_RULES = {"F821", "F822", "F823", "E902", "E999"}      # undefined names, syntax
LOW_RULE_PREFIXES = ("E1", "E2", "E3", "E5", "W", "F401", "F841", "C4", "PERF", "SIM", "RET")
# Everything else (B*, other F*, C901, PLR09*, E7xx) is treated as medium.

# ---- rules the refactoring stage is allowed to auto-fix -------------------
# Fixes marked "unsafe" by Ruff are included on purpose: they are only kept
# if the automated tests still pass (quality gate), which is the point of
# the validation stage in the proposal.
FIX_RULES = ["F401", "F841", "E711", "E712", "E713", "E714", "E731",
             "W291", "W293", "W391", "SIM102", "SIM103", "SIM108", "SIM110",
             "SIM118", "C4", "PERF401", "RET505", "RET506", "B006"]

# ---- risk score R = 100 * sum(w_i * x_i), weights sum to 1 ----------------
WEIGHTS = {
    "warnings":   0.20,   # weighted static-analysis warnings
    "complexity": 0.18,   # max cyclomatic complexity
    "duplication": 0.10,  # share of duplicated lines
    "func_length": 0.08,  # longest function
    "security":   0.15,   # Bandit findings
    "tests":      0.15,   # failing tests
    "coverage":   0.04,   # missing coverage
    "maintainability": 0.05,  # Radon maintainability index
    "change_size": 0.05,  # size of the modification (0 for a fresh analysis)
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

LOW_MAX = 25.0        # R < 25  -> Low
MODERATE_MAX = 50.0   # R < 50  -> Moderate, otherwise High

# ---- quality-gate thresholds ----------------------------------------------
GATE_MAX_CC = 10
GATE_MAX_DUP = 0.15
IMPROVE_EPS = 1.0     # risk-score change treated as "no change"

TEST_TIMEOUT_S = 60
