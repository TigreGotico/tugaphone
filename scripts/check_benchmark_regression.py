#!/usr/bin/env python3
"""Fail CI when a change worsens any dialect's rules-only PER or stress.

Re-scores every dialect from the committed gold fixtures (offline —
CI never touches the network) and compares each row against the
committed baseline (``benchmarks/results.json``). A row regresses when
its PER rises, or its stress accuracy falls, by more than an absolute
epsilon (default ``0.005`` — small enough to catch a real rule
regression, large enough to absorb float noise). A row whose baseline
has a stress accuracy and whose new score has none also regresses: the
stress-eligible words vanished. Improvements are reported and never
fail; commit the regenerated baseline alongside the improving change so
the new level becomes the floor.

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

    regressed = []
    for metric, worse in (("per", 1), ("stress_acc", -1)):
        regressed += _compare(metric, worse, rows, baseline, args.epsilon)

    if regressed:
        print(f"\n{len(regressed)} row(s) regressed beyond "
              f"epsilon={args.epsilon}:")
        for dialect, metric, old, new in regressed:
            print(f"  {dialect} {metric}: {_fmt(old)} -> {_fmt(new)}")
        sys.exit(1)
    print("\nno regressions detected")


def regression(old, new, worse: int, epsilon: float) -> bool:
    """True when *new* is worse than *old* by more than *epsilon*.

    *worse* is +1 for a metric where higher is worse (PER) and -1 for one
    where lower is worse (stress accuracy). A score that disappears
    against a baseline that had one regresses; a baseline with no score
    has nothing to hold.
    """
    if old is None:
        return False
    if new is None:
        return True
    return (new - old) * worse > epsilon


def _compare(metric: str, worse: int, rows, baseline, epsilon: float):
    header = (f"{metric:<24}{'baseline':>10}{'new':>10}{'delta':>10}"
              "  status")
    print(header)
    print("-" * len(header))
    regressed = []
    for row in rows:
        new = row[metric]
        base = baseline.get(row["dialect"], {})
        if metric not in base:
            print(f"{row['dialect']:<24}{'-':>10}{_fmt(new):>10}"
                  f"{'-':>10}  new")
            continue
        old = base[metric]
        bad = regression(old, new, worse, epsilon)
        delta = "-" if old is None or new is None else f"{new - old:+.4f}"
        print(f"{row['dialect']:<24}{_fmt(old):>10}{_fmt(new):>10}"
              f"{delta:>10}  {'regressed' if bad else 'ok'}")
        if bad:
            regressed.append((row["dialect"], metric, old, new))
    print("-" * len(header))
    return regressed


def _fmt(value) -> str:
    return "-" if value is None else f"{value:.4f}"


if __name__ == "__main__":
    main()
