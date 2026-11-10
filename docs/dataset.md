# Dataset: ProactiCode benchmark (15 tasks)

## Purpose
A small, fully reproducible set of Python programs that contain typical code-quality problems,
each with unit tests, so that ProactiCode can be measured on whether its changes **improve quality
without breaking behaviour**.

## How it was created
1. **Task selection.** 15 small utility programs (grading, validation, list helpers, cart, file
   parsing, passwords, inventory, text statistics, shell runner, matrices, bank account, dates,
   stack/queue, memoised fibonacci, null object).
2. **Writing the solutions.** Each `solution.py` was written by hand to be *functionally correct but
   messy*, imitating patterns often produced by code assistants: deep nesting, `else` after `return`,
   loops that build lists, comparison with `None`/booleans, unused imports and variables, copy-pasted
   blocks, long functions, bare `except`, `eval`, `subprocess(shell=True)`, MD5 hashing, a hard-coded
   password.
3. **Writing the tests.** Each task has `test_solution.py` (pytest), 2-12 tests, 86-100% line coverage.
4. **Annotation (task kind and planted issues).** Every task has `meta.json` with
   `kind` and a plain-language list of the planted issues:
   - `typical` (12 tasks): ordinary quality problems.
   - `control` (1 task, t13): already-clean code; the system should leave it alone.
   - `stress` (2 tasks, t14, t15): a mechanical Ruff fix changes behaviour, which only the tests reveal.
5. **Validation.** `python scripts/validate_benchmark.py` runs every original solution against its tests
   and writes `benchmark/manifest.csv` (LOC, number of tests, coverage). The script exits with an error if
   any original solution fails its own tests.
6. **Preprocessing.** None beyond the above; the analysis tools read the files directly. Test files
   (`test_*.py`) are excluded from quality metrics so that only the code under review is scored.

## Ground truth
There is no ground-truth label of "true defect". The reference for behaviour is the test suite:
a change is a regression if more tests fail after it than before.

## Licensing and provenance
All code was written for this project; no third-party code or scraped repositories are used.

## Limitations
- Synthetic: patterns resemble AI-generated code but were not produced by a code assistant.
- Small and short programs (10-50 lines): scores from these tasks do not transfer directly to large repositories.
- Stress tasks were designed on purpose and over-represent regressions compared with real code.
