# Design decisions

## Risk score
`R = 100 * sum_i w_i * x_i` with nine indicators (warnings, complexity, duplication, longest function,
security, failing tests, missing coverage, maintainability index, change size), each normalised to [0, 1].
Weights and category thresholds (Low < 25 <= Moderate < 50 <= High) live in `proacticode/config.py` and were
fixed **before** running the experiment. They are expert-chosen defaults, not learned or tuned values.

## Quality gate (fixed rules, applied to the final version of the code)
- **Request changes:** any failing test, any high-severity security finding, any high-severity static error.
- **Flag for review:** non-Low risk category, medium security finding, cyclomatic complexity above 10,
  more than 15% duplicated lines, unresolved warnings, or no tests.
- **Approve:** none of the above.
A low score never overrides a failing test or a critical security finding.

## Safety of automatic fixes
Fixes run on a **copy** (`refactor.py`). Some Ruff fixes are "unsafe" (they can change behaviour). They are
included deliberately: the pipeline re-runs the tests and, if more tests fail than before, **reverts** to the
original. The original files are never modified (checked by `tests/test_core.py`).

## Why baseline C exists
The proposal compares against static-analysis-only baselines. Baseline C (naive auto-fix, no validation)
was added to isolate the contribution of the validation step.

## Known weaknesses
See "Honest limitations" in the README.
