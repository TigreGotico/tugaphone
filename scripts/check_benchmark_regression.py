#!/usr/bin/env python3
"""Fail CI when a change worsens any dialect's rules-only PER.

Re-scores every dialect from the committed gold fixtures (offline —
CI never touches the network) and compares each row's PER against the
committed baseline (``benchmarks/results.json``). A row regresses when
its PER worsens by more than an absolute epsilon (default ``0.005`` —
small enough to catch a real rule regression, large enough to absorb
float noise). Improvements are reported and never fail; commit the
regenerated baseline alongside the improving change so the new level
becomes the floor.

Usage::

    python scripts/check_benchmark_regression.py
    python scripts/check_benchmark_regression.py --epsilon 0.01
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from benchmark import (  # noqa: E402
    DIALECT_TO_REGION, HARNESS_VERSION, RESULTS_JSON, score_dialect,
)

DEFAULT_EPSILON = 0.005

#: Every registered gold dialect must produce a scored row; fewer means a
#: fixture failed to load, and silence would be a false green.
MIN_SCORED_ROWS = len(DIALECT_TO_REGION)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--epsilon", type=float, default=DEFAULT_EPSILON)
    args = ap.parse_args()

    with open(RESULTS_JSON, encoding="utf-8") as fh:
        baseline = {r["dialect"]: r for r in json.load(fh)}

    versions = {r.get("harness_version") for r in baseline.values()}
    if versions - {HARNESS_VERSION}:
        sys.exit(
            f"baseline harness_version(s) {sorted(v for v in versions if v)} "
            f"!= this checkout's {HARNESS_VERSION!r} — regenerate the "
            f"baseline (scripts/benchmark.py) before comparing.")

    rows = [score_dialect(d) for d in sorted(DIALECT_TO_REGION)]
    if len(rows) < MIN_SCORED_ROWS:
        sys.exit(f"only {len(rows)} rows scored "
                 f"(expected {MIN_SCORED_ROWS}) — failing closed.")

    header = f"{'dialect':<24}{'baseline':>10}{'new':>10}{'delta':>10}  status"
    print(header)
    print("-" * len(header))
    regressed = []
    for row in rows:
        base = baseline.get(row["dialect"])
        if base is None:
            print(f"{row['dialect']:<24}{'-':>10}{row['per']:>10.4f}"
                  f"{'-':>10}  new")
            continue
        delta = row["per"] - base["per"]
        status = "regressed" if delta > args.epsilon else "ok"
        print(f"{row['dialect']:<24}{base['per']:>10.4f}{row['per']:>10.4f}"
              f"{delta:>+10.4f}  {status}")
        if status == "regressed":
            regressed.append((row["dialect"], base["per"], row["per"]))
    print("-" * len(header))

    if regressed:
        print(f"\n{len(regressed)} dialect(s) regressed beyond "
              f"epsilon={args.epsilon}:")
        for dialect, old, new in regressed:
            print(f"  {dialect}: {old:.4f} -> {new:.4f}")
        sys.exit(1)
    print("\nno regressions detected")


if __name__ == "__main__":
    main()
