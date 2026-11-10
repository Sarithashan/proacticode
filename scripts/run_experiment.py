"""Run all four systems on every benchmark task and write results/.

Usage:  python scripts/run_experiment.py [--repeats 3]

Outputs: results/per_task.csv, results/summary.md, results/fig_risk.png,
         results/fig_systems.png
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from proacticode import pipeline  # noqa: E402

TASKS = ROOT / "benchmark" / "tasks"
OUT = ROOT / "results"
SYSTEMS = [("A_static_only", pipeline.baseline_a), ("B_rule_risk", pipeline.baseline_b),
           ("C_naive_autofix", pipeline.naive_autofix), ("D_proacticode", pipeline.proacticode)]


def flatten(task, kind, res, times):
    b, a = res["before"], res["after"]
    rb, ra = res["risk_before"], res["risk_after"]
    return {
        "task": task, "kind": kind, "system": res["system"],
        "warnings_before": b["ruff_total"], "warnings_after": a["ruff_total"],
        "max_cc_before": b["max_cc"], "max_cc_after": a["max_cc"],
        "dup_before": b["dup_ratio"], "dup_after": a["dup_ratio"],
        "bandit_before": b["bandit_high"] + b["bandit_medium"] + b["bandit_low"],
        "bandit_after": a["bandit_high"] + a["bandit_medium"] + a["bandit_low"],
        "tests_failed_before": b["tests_failed"], "tests_failed_after": a["tests_failed"],
        "coverage_after": a["coverage"],
        "risk_before": rb["score"] if rb else None, "risk_after": ra["score"] if ra else None,
        "category_before": rb["category"] if rb else None,
        "category_after": ra["category"] if ra else None,
        "decision": res["decision"], "reverted": res["reverted"], "regression": res["regression"],
        "changed_lines": res["changed_lines"], "n_recommendations": res["n_recommendations"],
        "time_s": sum(times) / len(times),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=3, help="timing repeats per run")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    hist = OUT / "history.jsonl"
    if hist.exists():
        hist.unlink()

    import json
    rows = []
    for d in sorted(TASKS.iterdir()):
        if not (d / "solution.py").exists():
            continue
        kind = json.loads((d / "meta.json").read_text())["kind"]
        for name, fn in SYSTEMS:
            times, res = [], None
            for rep in range(args.repeats):
                kw = {"task_name": d.name, "log": rep == 0} if name == "D_proacticode" else {}
                res = fn(d, **kw)
                times.append(res["time_s"])
            rows.append(flatten(d.name, kind, res, times))
            print(f"{d.name:28s} {name:16s} done", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "per_task.csv", index=False)
    write_summary(df)
    make_figures(df)
    print("Results written to", OUT)


def write_summary(df):
    lines = ["# Experiment results\n",
             f"Tasks: {df['task'].nunique()}  |  Systems: {df['system'].nunique()}\n"]
    g = df.groupby("system")
    s = pd.DataFrame({
        "mean_warnings_after": g["warnings_after"].mean().round(2),
        "mean_max_cc_after": g["max_cc_after"].mean().round(2),
        "mean_risk_after": g["risk_after"].mean().round(2),
        "tasks_with_test_regression": g["regression"].sum().astype(int),
        "fixes_reverted": g["reverted"].sum().astype(int),
        "mean_time_s": g["time_s"].mean().round(2),
    })
    lines += ["## Per-system summary (all tasks)\n", s.to_markdown(), "\n"]

    d = df[df.system == "D_proacticode"].set_index("task")
    c = df[df.system == "C_naive_autofix"].set_index("task")
    lines += ["## Warnings before vs after (initial mean = "
              f"{d['warnings_before'].mean():.2f})\n"]
    lines += [f"- ProactiCode final mean warnings: {d['warnings_after'].mean():.2f}",
              f"- Naive auto-fix final mean warnings: {c['warnings_after'].mean():.2f}\n"]

    improved = (d["risk_before"] - d["risk_after"] > 1.0).sum()
    lines += ["## Recommendation effectiveness (ProactiCode)\n",
              f"- Tasks where risk score improved by more than 1 point: {improved}/{len(d)}",
              f"- Tasks where fixes were rejected after causing a test regression: {int(d['reverted'].sum())}/{len(d)}",
              f"- Tasks where the final version still has a test failure: {int((d['tests_failed_after'] > 0).sum())}/{len(d)}",
              f"- Naive auto-fix (no validation) left broken code in {int(c['regression'].sum())}/{len(c)} tasks\n"]

    lines.append("## Gate decisions (ProactiCode)\n")
    lines.append(d["decision"].value_counts().to_markdown() + "\n")

    lines.append("## Paired significance tests (Wilcoxon signed-rank, before vs after)\n")
    for label, frame in [("ProactiCode", d), ("Naive auto-fix", c)]:
        for col_b, col_a, name in [("risk_before", "risk_after", "risk score"),
                                   ("warnings_before", "warnings_after", "warning count")]:
            diff = frame[col_b] - frame[col_a]
            if (diff == 0).all():
                lines.append(f"- {label}, {name}: no change on any task")
                continue
            try:
                p = wilcoxon(frame[col_b], frame[col_a]).pvalue
                lines.append(f"- {label}, {name}: p = {p:.4f} (n={len(frame)})")
            except ValueError as e:
                lines.append(f"- {label}, {name}: test not applicable ({e})")
    lines.append("")

    lines.append("## Per-task detail (ProactiCode)\n")
    cols = ["kind", "warnings_before", "warnings_after", "max_cc_before", "max_cc_after",
            "risk_before", "risk_after", "decision", "reverted"]
    lines.append(d[cols].to_markdown() + "\n")

    lines += ["## What was NOT measured\n",
              "- Supervised ML risk prediction: no labelled future-defect data exists in this benchmark, "
              "so (as stated in the proposal) the risk model is rule-based only.",
              "- Share of recommendations accepted by human reviewers and developer review effort: "
              "no human study was run.",
              "- Results come from 15 small hand-written tasks and are not evidence about real repositories.\n"]
    (OUT / "summary.md").write_text("\n".join(lines))


def make_figures(df):
    d = df[df.system == "D_proacticode"].set_index("task")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = range(len(d))
    ax.bar([i - 0.2 for i in x], d["risk_before"], 0.4, label="Before", color="#c97b5a")
    ax.bar([i + 0.2 for i in x], d["risk_after"], 0.4, label="After ProactiCode", color="#4a8f7b")
    ax.set_xticks(list(x))
    ax.set_xticklabels([t.split("_")[0] for t in d.index])
    ax.set_ylabel("Risk score (0-100)")
    ax.set_xlabel("Benchmark task")
    ax.set_title("Risk score per task, before vs after")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fig_risk.png", dpi=150)
    plt.close(fig)

    g = df.groupby("system")
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    names = [s.split("_")[0] for s in g.groups]
    axes[0].bar(names, g["warnings_after"].mean(), color="#6c7fb3")
    axes[0].set_title("Mean warnings left")
    axes[1].bar(names, g["regression"].sum(), color="#c97b5a")
    axes[1].set_title("Tasks with broken tests")
    axes[2].bar(names, g["time_s"].mean(), color="#8a8a8a")
    axes[2].set_title("Mean time per task (s)")
    for a in axes:
        a.set_xlabel("System (A, B, C, D)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_systems.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
