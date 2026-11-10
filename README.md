# ProactiCode

**A quality-aware technical-debt risk assessment and prevention framework for Python code**
Saanvi Anup K, Saritha S

ProactiCode analyses Python code, turns the findings into one risk score, explains each issue
with a concrete suggestion, applies mechanical fixes **in a separate copy**, re-runs the tests,
and then decides: **Approve / Flag for review / Request changes**.
It implements the method from our research proposal (motivated by He et al., *Speed at the Cost
of Quality*, which found that Cursor adoption raised static-analysis warnings and code complexity).

```
code -> [1 Analyse] -> [2 Risk score] -> [3 Recommend + Fix copy] -> [4 Re-test + Gate] -> [5 Dashboard]
        Ruff, Radon,    R = sum(w_i x_i)   rule templates, Ruff        Pytest + coverage,
        Bandit, dup.    Low/Moderate/High  autofix on a copy            revert if tests break
```

## What is in this repository

| Proposal phase | Code |
|---|---|
| 3.1 Code collection and quality analysis | `proacticode/analyzer.py`, `duplication.py` |
| 3.2 Technical-debt risk assessment (rule-based) | `proacticode/risk.py`, weights in `config.py` |
| 3.3 Explainable recommendations and refactoring | `proacticode/recommend.py`, `refactor.py` |
| 3.4 Automated testing and quality gates | `proacticode/gate.py`, `pipeline.py` |
| 3.5 Quality monitoring dashboard | `app/dashboard.py` (Streamlit) |
| 3.6 / 4 Baselines and evaluation | `proacticode/pipeline.py` (baselines A, B, C), `scripts/run_experiment.py` |
| Dataset | `benchmark/tasks/` (15 tasks), see `docs/dataset.md` |

```
proacticode/    the framework          benchmark/tasks/   15 tasks (solution.py + tests + meta.json)
app/            Streamlit dashboard    scripts/           validate_benchmark.py, run_experiment.py
tests/          unit tests             results/           per_task.csv, summary.md, figures
docs/           dataset + design notes
```

## Install

Python 3.10+ is required.

```bash
git clone <your-repo-url> && cd proacticode
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
# 0. FIRST: prove that Ruff, Bandit and Pytest work in this Python environment
python scripts/check_setup.py          # must end with: SETUP OK

# 1. check that the benchmark itself is valid (all 15 original solutions pass their tests)
python scripts/validate_benchmark.py

# 2. reproduce the experiment (about 2 minutes; omit --repeats for 3 timing repeats, about 6 minutes)
python scripts/run_experiment.py --repeats 1
#    -> results/per_task.csv, results/summary.md, results/fig_risk.png, results/fig_systems.png

# 3. unit tests for the framework
pytest tests -q

# 4. interactive dashboard
python -m streamlit run app/dashboard.py

# 5. use it on your own code from Python
python - <<'PY'
from pathlib import Path
from proacticode.pipeline import proacticode
r = proacticode(Path("benchmark/tasks/t01_grade_calculator"), log=False)
print(r["decision"], r["risk_before"]["score"], "->", r["risk_after"]["score"])
PY
```

To analyse your own project folder, pass a directory that contains your `.py` files and (optionally)
`test_*.py` files; tests are run with `pytest` from inside that directory.

## Systems compared (proposal Section 3.6)

| System | What it does |
|---|---|
| A. Static only | Ruff + Radon + Bandit + duplication; raw numbers, no score, no tests |
| B. Rule-based risk | A + tests + the risk score and category |
| C. Naive auto-fix | *Added ablation.* Applies the same fixes with no test validation |
| D. ProactiCode | B + recommendations + fixes in a copy + re-test + revert on regression + gate |

## Results (15 tasks, produced by `scripts/run_experiment.py`)

| System | mean warnings left (start: 3.20) | tasks with broken tests | mean time per task |
|---|---|---|---|
| A. Static only | 3.20 | 0 | 0.17 s |
| B. Rule-based risk | 3.20 | 0 | 0.74 s |
| C. Naive auto-fix | 0.93 | **2** | 1.48 s |
| D. ProactiCode | 1.20 | **0** (2 fixes rejected) | 1.49 s |

- ProactiCode reduced warnings and the risk score significantly (Wilcoxon signed-rank on the 15 paired
  tasks, p = 0.018 for risk and p = 0.018 for warnings; many tasks are tied, so treat p-values as indicative).
- The naive baseline removes more warnings, but breaks behaviour in 2 tasks. ProactiCode's test
  validation caught both and kept the original code.
- ProactiCode flagged issues it **cannot fix automatically** (e.g. copy-pasted blocks, a complexity-14
  function, `eval`, `shell=True`, MD5) and recommended manual changes. Final gate decisions:
  2 Approve, 11 Flag for review, 2 Request changes.
- Warning counts, risk scores and decisions are deterministic and reproduce exactly; timings vary by machine.
- Full per-task table: `results/summary.md`.

## Honest limitations

- **Small, hand-written benchmark.** The 15 tasks imitate common AI-generated code patterns; they are
  not real model output and not real repositories. Results do not show how ProactiCode performs on
  large projects.
- **The two regression cases are planted.** Tasks `t14` and `t15` were designed so that a mechanical fix
  changes behaviour. They show the validation mechanism works, not how often it triggers in practice.
- **Risk categories are not discriminating on small files.** All scores are below 25, so every task is
  "Low". The score still orders tasks by risk (see `results/fig_risk.png`) and the gate uses explicit
  rules (failing tests, security, complexity, duplication), but the Low/Moderate/High thresholds
  (fixed before the experiment, in `config.py`) would need recalibration on larger code.
- **No machine-learning predictor.** As the proposal states, supervised risk prediction needs labelled
  future-defect data, which this benchmark does not have. The risk model is rule-based only.
- **Not measured:** share of recommendations accepted by human reviewers, and developer review effort
  (no human study was run).
- **Python only**; static metrics are proxies for maintainability, not proof of defects.

## Troubleshooting

- **Every task shows 0 warnings / the dashboard says results look invalid.** Ruff or Bandit is not installed
  in the Python environment you ran from. Activate your virtual environment, run
  `pip install -r requirements.txt`, then `python scripts/check_setup.py`. Re-run the experiment only after it
  prints `SETUP OK`. (The code now stops with a clear `ToolError` instead of silently reporting zero findings.)
- **`streamlit` not found.** Use `python -m streamlit run app/dashboard.py` from the activated environment.
- **Pages look unstyled.** Make sure you start Streamlit from the project root so `.streamlit/config.toml` is found.
