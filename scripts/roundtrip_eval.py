"""Measure how well ``mode="respell"`` forces an accent through a base voice.

The claim respelling has to earn: feeding the *respelled* text to the base voice
must land closer to the *target* accent than feeding the *original* text to the
base voice does. This script measures exactly that on orthography2ipa's
sentence-level Portuguese TTS gold, over every pt-family lect
(:func:`tugaphone.registry.list_dialects`), using the same character PER and IPA
normalisation as tugaphone's own gold benchmark.

For each lect it reports three character-error rates against the *base* lect's
reading:

* ``base``   — PER( base(original) , target(original) ): the accent gap with no
  forcing at all (how far the base voice already is from the target).
* ``respell``— PER( base(respell) , target(original) ): the residual gap after
  forcing the text through respelling.
* ``gain``   — ``base - respell``: how much of the gap respelling closed
  (positive = respelling helped; ``0`` = nothing respellable for this lect).

``target(original)`` is the lattice's own transcription of the sentence in the
target lect (the accent we are forcing toward), not the hand gold — we are
measuring the *respeller*, holding the lattice fixed on both sides.

    python scripts/roundtrip_eval.py                 # every pt-family lect
    python scripts/roundtrip_eval.py pt-BR pt-PT-x-porto
    python scripts/roundtrip_eval.py --base pt-PT --limit 40
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from importlib import import_module
from pathlib import Path

from tugaphone.accent import respell
from tugaphone.lattice_core import phonemize
from tugaphone.registry import list_dialects


def _load_o2i_benchmark():
    o2i_file = Path(import_module("orthography2ipa").__file__).resolve()
    for parent in o2i_file.parents:
        cand = parent / "scripts" / "benchmark.py"
        if cand.exists():
            spec = importlib.util.spec_from_file_location("_o2i_benchmark", cand)
            module = importlib.util.module_from_spec(spec)
            sys.modules["_o2i_benchmark"] = module
            spec.loader.exec_module(module)
            return module
    raise RuntimeError("orthography2ipa benchmark script not found")


O2I = _load_o2i_benchmark()


def _per(hyp: str, ref: str) -> float:
    h = O2I.normalize(hyp, True, False)
    r = O2I.normalize(ref, True, False)
    if not r:
        return float("nan")
    return O2I.levenshtein(h, r) / len(r)


def _default_lects():
    return sorted(set(O2I._PORTUGUESE_TTS_LANGS) & set(list_dialects()))


def main(argv) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lects", nargs="*", help="lect codes (default: all)")
    parser.add_argument("--base", default="pt-PT", help="base voice lect")
    parser.add_argument("--limit", type=int, default=200,
                        help="max gold sentences per lect")
    args = parser.parse_args(argv)

    lects = args.lects or _default_lects()
    base = args.base
    print(f"base voice = {base}")
    print(f"{'lect':<22}{'base':>9}{'respell':>9}{'gain':>9}{'n':>6}")
    rows = []
    for lect in lects:
        if lect == base:
            continue
        pairs = O2I.load_portuguese_tts(lect, args.limit)
        if not pairs:
            continue
        b_sum = r_sum = 0.0
        n = 0
        for sentence, _gold in pairs:
            try:
                target = phonemize(sentence, lect)
                base_orig = phonemize(sentence, base)
                base_resp = phonemize(respell(sentence, lect, base), base)
            except Exception:
                continue
            pb = _per(base_orig, target)
            pr = _per(base_resp, target)
            if pb != pb or pr != pr:
                continue
            b_sum += pb
            r_sum += pr
            n += 1
        if not n:
            continue
        pb, pr = b_sum / n, r_sum / n
        rows.append((lect, pb, pr, pb - pr, n))
        print(f"{lect:<22}{pb:>9.4f}{pr:>9.4f}{pb - pr:>+9.4f}{n:>6}")

    if rows:
        print("-" * 55)
        mb = sum(r[1] for r in rows) / len(rows)
        mr = sum(r[2] for r in rows) / len(rows)
        print(f"{'MEAN':<22}{mb:>9.4f}{mr:>9.4f}{mb - mr:>+9.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
