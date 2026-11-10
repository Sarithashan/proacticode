"""Check the benchmark itself: every original solution must pass its own tests,
and a manifest (benchmark/manifest.csv) is written with basic statistics."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from proacticode.analyzer import analyze  # noqa: E402

TASKS = ROOT / "benchmark" / "tasks"


def main():
    rows, bad = [], []
    for d in sorted(TASKS.iterdir()):
        if not (d / "solution.py").exists():
            continue
        m, _ = analyze(d)
        import json
        meta = json.loads((d / "meta.json").read_text())
        ok = m["tests_failed"] == 0 and m["tests_total"] > 0
        if not ok:
            bad.append(d.name)
        rows.append({"task": d.name, "kind": meta["kind"], "loc": m["loc"],
                     "tests": m["tests_total"], "tests_failed": m["tests_failed"],
                     "coverage": m["coverage"], "planted_issues": meta["planted_issues"]})
        print(f"{d.name:28s} tests={m['tests_total']:2d} failed={m['tests_failed']} "
              f"cov={m['coverage']}  {'OK' if ok else 'PROBLEM'}")
    with open(ROOT / "benchmark" / "manifest.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    if bad:
        print("\nINVALID TASKS:", bad)
        sys.exit(1)
    print(f"\nAll {len(rows)} tasks valid. Manifest written to benchmark/manifest.csv")


if __name__ == "__main__":
    main()
