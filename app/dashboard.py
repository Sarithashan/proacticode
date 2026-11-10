"""Phase 5 - ProactiCode quality dashboard (Streamlit).

Run with:  streamlit run app/dashboard.py
"""
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import style  # noqa: E402
from proacticode import risk  # noqa: E402
from proacticode.analyzer import ToolError, analyze  # noqa: E402
from proacticode.pipeline import proacticode  # noqa: E402
from proacticode.recommend import recommend  # noqa: E402

TASKS = ROOT / "benchmark" / "tasks"
RESULTS = ROOT / "results"

st.set_page_config(page_title="ProactiCode", page_icon="🛡️", layout="wide")
st.markdown(style.CSS, unsafe_allow_html=True)
st.markdown(style.hero(
    "ProactiCode",
    "Catch technical debt in Python code before it ships: analyse, score, explain, fix safely, and decide.",
    ["Ruff", "Radon", "Bandit", "Pytest", "Rule-based risk score", "Quality gate"]), unsafe_allow_html=True)

tab_how, tab_file, tab_task, tab_bench, tab_hist = st.tabs(
    ["How it works", "Analyse a file", "Run on a benchmark task", "Benchmark results", "Quality history"])


def cols_kpi(items):
    for col, (label, value, sub) in zip(st.columns(len(items)), items):
        col.markdown(style.kpi(label, value, sub), unsafe_allow_html=True)


def show_risk(r, title=None):
    if title:
        st.markdown(f"#### {title}")
    cols_kpi([("Risk score", r["score"], "0 = healthy, 100 = worst"), ("Category", r["category"], "")])
    st.markdown(style.badge(r["category"]), unsafe_allow_html=True)
    contrib = pd.Series(r["contributions"], name="points").sort_values(ascending=False)
    st.caption("Where the risk points come from (each indicator multiplied by its weight):")
    st.bar_chart(contrib, color="#4f46e5")


def rec_table(recs):
    if not recs:
        st.success("No findings. Nothing to fix.")
        return
    df = pd.DataFrame(recs)[["severity", "line", "issue", "suggestion", "auto_fixable"]]
    df.columns = ["Severity", "Line", "Issue", "What to do", "Can be fixed automatically"]
    st.dataframe(df, hide_index=True)


# ---------------------------------------------------------------- how it works
with tab_how:
    st.markdown("### What does ProactiCode do?")
    st.markdown("AI assistants write code fast, but fast code often hides problems that cost time later "
                "(this is called **technical debt**). ProactiCode checks code like a careful reviewer: "
                "it measures it, scores the risk, explains each problem, tries safe fixes on a **copy**, "
                "re-runs the tests, and gives a clear decision.")
    st.markdown(style.steps([
        (1, "Analyse", "Ruff finds style and bug patterns, Radon measures complexity, Bandit looks for security "
                       "problems, and a duplicate detector finds copy-pasted code.", "#4f46e5"),
        (2, "Score risk", "All measurements are combined into ONE number from 0 to 100 with a weighted sum.", "#7c3aed"),
        (3, "Recommend", "Every problem gets a plain-English reason and a concrete suggestion.", "#0891b2"),
        (4, "Fix a copy and test", "Safe fixes are applied to a copy. The unit tests run again. If a test "
                                   "breaks, the fix is thrown away.", "#059669"),
        (5, "Decide", "Approve, Flag for review, or Request changes. A failing test always blocks.", "#d97706"),
    ]), unsafe_allow_html=True)
    st.markdown("### How to read the numbers")
    with st.expander("Risk score and category"):
        st.write("The score adds up weighted indicators (warnings, complexity, duplication, long functions, "
                 "security, failing tests, low coverage, maintainability, size of the change). "
                 "Low is under 25, Moderate is 25 to 50, High is 50 or more. It is an estimate of quality risk, "
                 "not proof that the code is broken.")
    with st.expander("Warnings, complexity, duplication"):
        st.write("**Warnings** are issues Ruff reports. **Complexity** (cyclomatic) counts the different paths "
                 "through a function; above 10 is hard to test and read. **Duplication** is the share of "
                 "lines that are copied blocks.")
    with st.expander("Regression and 'reverted'"):
        st.write("A **regression** means a fix made more tests fail than before. ProactiCode detects this and "
                 "**reverts** (keeps the original code), so a fix never silently breaks behaviour.")
    with st.expander("Gate decisions"):
        st.write("**Approve**: all checks passed. **Flag for review**: a human should look (for example "
                 "unresolved warnings or high complexity). **Request changes**: blocking problem (failing tests "
                 "or a high-severity security finding).")

# ---------------------------------------------------------------- analyse a file
with tab_file:
    st.markdown("### Analyse your own Python file")
    st.caption("Static analysis only (no tests are run for uploaded files).")
    up = st.file_uploader("Choose a .py file", type=["py"])
    if up is not None:
        tmp = Path(tempfile.mkdtemp())
        (tmp / "uploaded.py").write_bytes(up.read())
        try:
            m, findings = analyze(tmp, with_tests=False)
        except ToolError as exc:
            st.markdown(f'<div class="warnbox"><b>Setup problem:</b> {exc}</div>', unsafe_allow_html=True)
            st.stop()
        r = risk.assess(m)
        cols_kpi([("Risk score", r["score"], r["category"]), ("Warnings", m["ruff_total"], "from Ruff"),
                  ("Max complexity", m["max_cc"], "per function"),
                  ("Duplicated lines", f"{m['dup_ratio']:.0%}", "copy-pasted code")])
        st.markdown("#### Findings by severity")
        st.bar_chart(pd.Series({"high": m["ruff_high"] + m["bandit_high"],
                                "medium": m["ruff_medium"] + m["bandit_medium"],
                                "low": m["ruff_low"] + m["bandit_low"]}), color="#7c3aed")
        st.markdown("#### Explanations and recommendations")
        rec_table(recommend(findings))

# ---------------------------------------------------------------- full pipeline
with tab_task:
    st.markdown("### Run the full pipeline on a benchmark task")
    st.caption("Analyse, then fix a COPY, re-run the tests, and apply the quality gate. Originals are never changed.")
    names = sorted(p.name for p in TASKS.iterdir() if (p / "solution.py").exists())
    choice = st.selectbox("Benchmark task", names)
    if st.button("Run ProactiCode"):
        with st.spinner("Analysing, fixing a copy, re-testing..."):
            try:
                res = proacticode(TASKS / choice, task_name=choice, log=False)
            except ToolError as exc:
                st.markdown(f'<div class="warnbox"><b>Setup problem:</b> {exc}</div>', unsafe_allow_html=True)
                st.stop()
        st.markdown(style.decision_banner(res["decision"], res["reasons"]), unsafe_allow_html=True)
        st.markdown(f'<div class="note">{res["note"]}. Overall change: <b>{res["verdict"]}</b>.</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            show_risk(res["risk_before"], "Before")
        with c2:
            show_risk(res["risk_after"], "After")
        b, a = res["before"], res["after"]
        cmp = pd.DataFrame({"Before": [b["ruff_total"], b["max_cc"], b["dup_ratio"], b["tests_failed"]],
                            "After": [a["ruff_total"], a["max_cc"], a["dup_ratio"], a["tests_failed"]]},
                           index=["Warnings", "Max complexity", "Duplicate ratio", "Failing tests"])
        st.markdown("#### Before and after")
        st.table(cmp)
        st.markdown("#### Recommendations")
        rec_table(res["recommendations"])
        if res["diff"]:
            st.markdown("#### The change that was applied (to a copy only)")
            st.code(res["diff"], language="diff")

# ---------------------------------------------------------------- stored results
with tab_bench:
    st.markdown("### Experiment results")
    path = RESULTS / "per_task.csv"
    if not path.exists():
        st.warning("Run `python scripts/run_experiment.py` first.")
    else:
        df = pd.read_csv(path)
        d = df[df.system == "D_proacticode"]
        c = df[df.system == "C_naive_autofix"]
        if d["warnings_before"].sum() == 0:
            st.markdown('<div class="warnbox"><b>These results look invalid:</b> the static-analysis tools found '
                        'zero warnings in every task. Ruff or Bandit probably did not run. Run '
                        '<code>python scripts/check_setup.py</code>, fix what it reports, then run '
                        '<code>python scripts/run_experiment.py --repeats 1</code> again.</div>',
                        unsafe_allow_html=True)
        cols_kpi([("Tasks", len(d), "in the benchmark"),
                  ("Warnings", f"{d['warnings_before'].mean():.1f} → {d['warnings_after'].mean():.1f}",
                   "mean per task, before → after"),
                  ("Fixes rejected", int(d["reverted"].sum()), "they broke tests, so they were reverted"),
                  ("Naive fix broke", int(c["regression"].sum()), "tasks (no test validation)")])
        st.markdown("#### Per-task table")
        system = st.selectbox("System", sorted(df.system.unique()), index=3)
        view = df[df.system == system].set_index("task")
        st.dataframe(view[["kind", "warnings_before", "warnings_after", "max_cc_before", "max_cc_after",
                           "risk_before", "risk_after", "decision", "reverted", "regression", "time_s"]])
        st.markdown("#### Mean time per task (seconds)")
        st.bar_chart(df.groupby("system")["time_s"].mean(), color="#0891b2")
        if (RESULTS / "summary.md").exists():
            with st.expander("Full written summary"):
                st.markdown((RESULTS / "summary.md").read_text())

# ---------------------------------------------------------------- history
with tab_hist:
    st.markdown("### Quality history")
    st.caption("Each time ProactiCode analyses a task, one row is saved, so you can watch quality over revisions.")
    hist = RESULTS / "history.jsonl"
    if hist.exists():
        h = pd.DataFrame([json.loads(line) for line in hist.read_text().splitlines() if line.strip()])
        task = st.selectbox("Task", sorted(h.task.unique()), key="hist_task")
        sub = h[h.task == task].reset_index(drop=True)
        st.line_chart(sub[["risk", "warnings", "max_cc"]])
        st.dataframe(sub, hide_index=True)
    else:
        st.info("No history yet. Run the experiment or the pipeline first.")
