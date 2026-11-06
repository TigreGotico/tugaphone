#!/usr/bin/env python3
"""Benchmark tugaphone vs espeak-ng vs epitran on the Portuguese Unified
Pronunciation Lexicon.

Gold: ``TigreGotico/portuguese-unified-pronunciation-lexicon`` (HF).
Scores both ``ipa_broad`` (phonemic) and ``ipa_narrow`` (phonetic) columns
against all three G2P engines across the major Lusophone dialect regions.

Usage:
    python benchmarks/g2p_comparison.py                          # all regions, 2000 words each
    python benchmarks/g2p_comparison.py --region pt-PT --limit 500
    python benchmarks/g2p_comparison.py --modes tugaphone_full,tugaphone_rules,espeak,epitran
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import unicodedata
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

RESULTS_JSON = os.path.join(REPO_ROOT, "benchmarks", "g2p_comparison.json")

# toolkit → gold region mapping
TUGAPHONE_REGIONS = [
    "pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL",
    "pt-PT-x-lisbon", "pt-BR-x-sao-paulo", "pt-BR-x-rio-janeiro",
]

# espeak voice → gold region(s) it's compared against
ESPEAK_VOICE_MAP = {
    "pt-pt": ["pt-PT", "pt-PT-x-lisbon", "pt-AO", "pt-MZ", "pt-TL"],
    "pt-br": ["pt-BR", "pt-BR-x-sao-paulo", "pt-BR-x-rio-janeiro"],
}

# epitran only has por-Latn (European-leaning) — compare against all regions
# but interpretation should note the mismatch for pt-BR

WORDS_PER_REGION = 2000
SAMPLE_SEED = 20260708

_STRESS_MARKS = "\u02c8\u02cc"
_JOINERS = "\u00b7.|‿͜͡"
_SYLLABLE_DOT = "\u00b7"   # tugaphone syllable dot


def normalize(ipa: str) -> str:
    """Strip stress, syllable markers, whitespace; NFC."""
    s = unicodedata.normalize("NFC", ipa)
    for ch in _STRESS_MARKS + _JOINERS:
        s = s.replace(ch, "")
    return "".join(s.split())


# ---------------------------------------------------------------------------
# phonemizers
# ---------------------------------------------------------------------------

_tugaphone_full: object = None
_tugaphone_rules_cache: Dict[str, object] = {}
_epitran_inst = None


def _get_tugaphone_full():
    global _tugaphone_full
    if _tugaphone_full is None:
        from tugaphone import TugaPhonemizer
        _tugaphone_full = TugaPhonemizer()
    return _tugaphone_full


def _get_tugaphone_rules_inventory(dialect: str):
    inv = _tugaphone_rules_cache.get(dialect)
    if inv is None:
        from tugaphone.registry import get_dialect_inventory
        inv = get_dialect_inventory(dialect)
        try:
            inv.IRREGULAR_WORDS = {}
        except Exception:
            object.__setattr__(inv, "IRREGULAR_WORDS", {})
        _tugaphone_rules_cache[dialect] = inv
    return inv


def phonemize_tugaphone_full(word: str, dialect: str) -> str:
    """Full tugaphone: lexicon + rule fallback."""
    from tugaphone.tokenizer import Sentence
    ph = _get_tugaphone_full()
    return Sentence(word, dialect=ph._inventory_for_dialect(dialect)).ipa.strip()


def phonemize_tugaphone_rules(word: str, dialect: str) -> str:
    """Rules-only tugaphone (lexicon emptied)."""
    from tugaphone.tokenizer import Sentence
    inv = _get_tugaphone_rules_inventory(dialect)
    return Sentence(word, dialect=inv).ipa.strip()


def phonemize_tugaphone_simple(word: str, dialect: str) -> str:
    """Use TugaPhonemizer.phonemize_sentence (single word)."""
    ph = _get_tugaphone_full()
    return ph.phonemize_sentence(word, dialect)


def phonemize_espeak(word: str, voice: str = "pt") -> str:
    """Call espeak-ng with IPA output."""
    try:
        cp = subprocess.run(
            ["espeak-ng", "-x", "-v", voice, word, "--ipa"],
            capture_output=True, text=True, timeout=5,
        )
        out = cp.stdout.strip()
        if cp.returncode != 0:
            return ""
        return out.replace("\n", " ")
    except Exception:
        return ""


def phonemize_epitran(word: str) -> str:
    """epitran por-Latn transliteration."""
    global _epitran_inst
    if _epitran_inst is None:
        import epitran
        _epitran_inst = epitran.Epitran("por-Latn")
    try:
        return _epitran_inst.transliterate(word)
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------

def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                prev[j] + 1,
                cur[j - 1] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = cur
    return prev[-1]


def score_word(hyp: str, golds: List[str]) -> Tuple[int, int, int]:
    """Return (edit_distance, ref_length, 1_if_exact_match).
    Edit distance is against the closest gold variant.
    """
    h = normalize(hyp)
    best_d, best_n = None, None
    for gold in golds:
        r = normalize(gold)
        d = _levenshtein(h, r)
        if best_d is None or d / max(len(r), 1) < best_d / max(best_n, 1):
            best_d, best_n = d, len(r)
    exact = 1 if best_d == 0 else 0
    return best_d, best_n, exact


# ---------------------------------------------------------------------------
# data loading
# ---------------------------------------------------------------------------

def load_gold_and_sample(region: str, limit: int) -> Dict[str, List[str]]:
    """Load gold from HF dataset, sample *limit* words for *region*.
    Returns {word: [ipa_variants]}.
    """
    from datasets import load_dataset
    ds = load_dataset(
        "TigreGotico/portuguese-unified-pronunciation-lexicon",
        split="train",
        trust_remote_code=False,
    )
    # filter to region, non-empty ipa_narrow
    filtered = ds.filter(
        lambda r: r["region"] == region and r["ipa_narrow"] and r["ipa_narrow"].strip()
    )
    # gather all variants per word
    data: Dict[str, Dict[str, List[str]]] = defaultdict(
        lambda: {"broad": [], "narrow": []}
    )
    for row in filtered:
        w = row["word"].strip()
        narrow = (row["ipa_narrow"] or "").strip()
        broad = (row["ipa_broad"] or "").strip()
        if not w or not narrow:
            continue
        entry = data[w]
        if narrow not in entry["narrow"]:
            entry["narrow"].append(narrow)
        if broad and broad not in entry["broad"]:
            entry["broad"].append(broad)
        # if broad missing, copy narrow as fallback
        if not entry["broad"]:
            entry["broad"] = list(entry["narrow"])

    # sample
    words = sorted(data.items())
    rng = random.Random(SAMPLE_SEED)
    rng.shuffle(words)
    sample = dict(words[:limit])
    return sample


# ---------------------------------------------------------------------------
# benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark(
    regions: Optional[List[str]] = None,
    limit: int = WORDS_PER_REGION,
    modes: Optional[List[str]] = None,
) -> List[dict]:
    """Score every (region, mode) combination, return rows."""
    if regions is None:
        regions = TUGAPHONE_REGIONS
    if modes is None:
        modes = ["tugaphone_full", "tugaphone_rules", "espeak", "epitran"]

    rows: List[dict] = []

    for region in regions:
        print(f"\n{'='*60}")
        print(f"Region: {region}")
        print(f"{'='*60}")
        print(f"Loading gold data …", end=" ", flush=True)

        try:
            gold = load_gold_and_sample(region, limit)
        except Exception as e:
            print(f"FAILED: {e}")
            continue

        print(f"{len(gold)} words")

        # determine espeak voice
        espeak_voice = "pt"
        for voice, regions_list in ESPEAK_VOICE_MAP.items():
            if region in regions_list:
                espeak_voice = voice
                break

        for mode in modes:
            print(f"  {mode:22} …", end=" ", flush=True)
            err = tot = exact = failed = 0
            errors_narrow = err_b = tot_b = exact_b = 0  # for ipa_broad

            for word, variants in gold.items():
                try:
                    if mode == "tugaphone_full":
                        hyp = phonemize_tugaphone_simple(word, region)
                    elif mode == "tugaphone_rules":
                        hyp = phonemize_tugaphone_rules(word, region)
                    elif mode == "espeak":
                        hyp = phonemize_espeak(word, espeak_voice)
                    elif mode == "epitran":
                        hyp = phonemize_epitran(word)
                    else:
                        hyp = ""
                except Exception:
                    failed += 1
                    continue

                if not hyp:
                    failed += 1
                    continue

                # score against ipa_narrow
                d, n, ex = score_word(hyp, variants["narrow"])
                err += d
                tot += n
                exact += ex

                # score against ipa_broad
                if variants["broad"]:
                    d_b, n_b, ex_b = score_word(hyp, variants["broad"])
                    err_b += d_b
                    tot_b += n_b
                    exact_b += ex_b

            per_narrow = round(err / tot, 4) if tot else None
            per_broad = round(err_b / tot_b, 4) if tot_b else None
            acc_narrow = round(exact / len(gold), 4) if gold else None
            acc_broad = round(exact_b / len(gold), 4) if gold else None

            print(f"PER(narrow)={per_narrow} PER(broad)={per_broad} "
                  f"acc={acc_narrow}")

            rows.append({
                "region": region,
                "mode": mode,
                "n_words": len(gold),
                "failed": failed,
                "per_narrow": per_narrow,
                "per_broad": per_broad,
                "word_accuracy_narrow": acc_narrow,
                "word_accuracy_broad": acc_broad,
            })

    return rows


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def print_table(rows: List[dict]) -> None:
    """Print a formatted markdown comparison table."""
    # header
    col_w = {
        "mode": 22, "pt-PT": 14, "pt-BR": 14, "pt-AO": 14,
        "pt-MZ": 14, "pt-TL": 14,
        "pt-PT-x-lisbon": 14, "pt-BR-x-sao-paulo": 14,
        "pt-BR-x-rio-janeiro": 14,
    }

    def _row_cells(mode: str, metric: str, col_map: Dict[str, str]):
        cells = [f"**{metric}**"]
        for r in ["pt-PT", "pt-PT-x-lisbon", "pt-BR", "pt-BR-x-sao-paulo",
                   "pt-BR-x-rio-janeiro", "pt-AO", "pt-MZ", "pt-TL"]:
            key = col_map.get(r, "-")
            cells.append(key)
        return cells

    # group by metric
    for target in ["narrow", "broad"]:
        per_key = f"per_{target}"
        acc_key = f"word_accuracy_{target}"

        print(f"\n## ipa_{target} — PER (↓ better) / Word Accuracy (↑ better)")
        print()
        # header
        headers = ["Mode"] + [
            "pt-PT", "pt-PT-lx", "pt-BR", "pt-BR-sp", "pt-BR-rj",
            "pt-AO", "pt-MZ", "pt-TL",
        ]
        print("| " + " | ".join(f"{h:<12}" for h in headers) + " |")
        print("|" + "|".join(":" + "-"*11 for _ in headers) + "|")

        for mode in ["tugaphone_full", "tugaphone_rules", "espeak", "epitran"]:
            mode_rows = [r for r in rows if r["mode"] == mode]
            vals = {}
            for r in mode_rows:
                vals[r["region"]] = r
            short_regions = {
                "pt-PT": "pt-PT", "pt-PT-x-lisbon": "pt-PT-lx",
                "pt-BR": "pt-BR", "pt-BR-x-sao-paulo": "pt-BR-sp",
                "pt-BR-x-rio-janeiro": "pt-BR-rj",
                "pt-AO": "pt-AO", "pt-MZ": "pt-MZ", "pt-TL": "pt-TL",
            }
            cells = [f"{mode:<22}"]
            for r_full in ["pt-PT", "pt-PT-x-lisbon", "pt-BR",
                            "pt-BR-x-sao-paulo", "pt-BR-x-rio-janeiro",
                            "pt-AO", "pt-MZ", "pt-TL"]:
                val = vals.get(r_full)
                if val and val[per_key] is not None:
                    cells.append(f"PER={val[per_key]:.3f}")
                else:
                    cells.append("-")
            print("| " + " | ".join(f"{c:<12}" for c in cells) + " |")

            # word accuracy row
            cells = [f"{mode:<22}"]
            for r_full in ["pt-PT", "pt-PT-x-lisbon", "pt-BR",
                            "pt-BR-x-sao-paulo", "pt-BR-x-rio-janeiro",
                            "pt-AO", "pt-MZ", "pt-TL"]:
                val = vals.get(r_full)
                if val and val[acc_key] is not None:
                    cells.append(f"acc={val[acc_key]:.3f}")
                else:
                    cells.append("-")
            print("| " + " | ".join(f"{c:<12}" for c in cells) + " |")
            print()  # blank line between modes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--region", help="Benchmark one region only.")
    ap.add_argument("--limit", type=int, default=WORDS_PER_REGION,
                    help=f"Words per region (default {WORDS_PER_REGION}).")
    ap.add_argument("--modes", default="tugaphone_full,tugaphone_rules,espeak,epitran",
                    help="Comma-separated modes to run.")
    ap.add_argument("--output", default=RESULTS_JSON,
                    help="JSON results path.")
    args = ap.parse_args()

    regions = [args.region] if args.region else TUGAPHONE_REGIONS
    modes = [m.strip() for m in args.modes.split(",")]

    rows = run_benchmark(regions=regions, limit=args.limit, modes=modes)

    # write JSON
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"\nResults written to {args.output}")

    # print tables
    print_table(rows)


if __name__ == "__main__":
    main()
