#!/usr/bin/env python3
"""Gold-benchmark harness: rules-only PER per dialect, offline in CI.

Scores tugaphone's RULES-ONLY mode (the lexicon exception path emptied)
against the unified Portuguese pronunciation gold, one region per
registered dialect code. Rules-only keeps the score non-circular per
word: the lexicon tugaphone ships (tugalex) is built from the same
sources as the gold, so scoring the lexicon path would measure lookup
coverage, not grapheme-rule quality.

Gold source
───────────
``TigreGotico/portuguese-unified-pronunciation-lexicon`` on Hugging Face
(CC BY-SA 4.0) — the convention-normalized merge of Infopédia, the
Portal da Língua Portuguesa 10-region lexicon and pt.wiktionary.org.
The ``ipa_narrow`` column is scored: it matches tugaphone's transcription
depth (explicit [ɐ ɨ ɾ ʀ ɫ]).

Offline discipline
──────────────────
CI never touches the network. ``--refresh-fixtures`` (a maintainer
action) downloads the gold, draws a fixed-seed sample of
``FIXTURE_WORDS`` words per region and commits it under
``tests/data/gold/<dialect>.tsv`` with the dataset file's SHA-256 in the
header. Scoring runs (default mode, and the CI regression gate) read
only those committed fixtures.

Usage::

    python scripts/benchmark.py                       # score all dialects
    python scripts/benchmark.py --dialect pt-PT       # one dialect
    python scripts/benchmark.py --refresh-fixtures    # network; resample gold
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import unicodedata
import urllib.request
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "data", "gold")
RESULTS_JSON = os.path.join(REPO_ROOT, "benchmarks", "results.json")
SCOREBOARD_MD = os.path.join(REPO_ROOT, "docs", "scoreboard.md")

GOLD_URL = (
    "https://huggingface.co/datasets/TigreGotico/"
    "portuguese-unified-pronunciation-lexicon"
    "/resolve/main/portuguese_pronunciation_lexicon.jsonl"
)

#: tugaphone dialect code → unified-gold region tag. Regions with no
#: registered preset (pt-BR-x-carioca, pt-BR-x-caipira, untagged "pt")
#: are not scored.
DIALECT_TO_REGION: Dict[str, str] = {
    "pt-PT": "pt-PT",
    "pt-PT-x-lisbon": "pt-PT-x-lisboa",
    "pt-BR": "pt-BR",
    "pt-BR-x-sao-paulo": "pt-BR-x-saopaulo",
    "pt-BR-x-rio-janeiro": "pt-BR-x-riodejaneiro",
    "pt-AO": "pt-AO",
    "pt-MZ": "pt-MZ-x-maputo",
    "pt-TL": "pt-TL-x-dili",
}

#: Words per dialect fixture. Fixed-seed sample of the region's gold.
FIXTURE_WORDS = 1000
SAMPLE_SEED = 20260713

#: Bump when the scoring method itself changes (normalization, alignment),
#: so a baseline produced by an older method is never compared against.
HARNESS_VERSION = "1.0"


# ─── normalization + PER ────────────────────────────────────────────────────
# PER routine adapted from orthography2ipa's benchmark harness
# (scripts/benchmark.py of TigreGotico/orthography2ipa), simplified to the
# subset this word-level, single-convention gold needs.

_STRESS_MARKS = "ˈˌ"
_JOINERS = "·.|‿͜͡"


def normalize(ipa: str) -> str:
    """One comparable form: NFC, no stress marks, no syllable/tie joiners,
    no whitespace. Both sides of every comparison go through this."""
    s = unicodedata.normalize("NFC", ipa)
    for ch in _STRESS_MARKS + _JOINERS:
        s = s.replace(ch, "")
    return "".join(s.split())


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
            cur.append(min(prev[j] + 1,          # deletion
                           cur[j - 1] + 1,       # insertion
                           prev[j - 1] + (ca != cb)))  # substitution
        prev = cur
    return prev[-1]


def score_word(hyp: str, golds: List[str]) -> Tuple[int, int]:
    """(edit distance, reference length) against the CLOSEST gold variant.

    A word with several attested pronunciations is correct if it matches
    any of them; distance and length come from the best-matching variant
    so multi-variant words are not penalised for the variants they did
    not choose.
    """
    h = normalize(hyp)
    best: Optional[Tuple[int, int]] = None
    for gold in golds:
        r = normalize(gold)
        d = _levenshtein(h, r)
        if best is None or d / max(len(r), 1) < best[0] / max(best[1], 1):
            best = (d, len(r))
    assert best is not None
    return best


# ─── rules-only phonemization ───────────────────────────────────────────────

def rules_only_ipa(word: str, dialect_code: str) -> str:
    """Phonemize *word* with the dialect's grapheme rules ONLY.

    The dialect inventory is built normally, then its lexicon exception
    table is emptied, so every word takes the rule path. The engine and
    inventory are cached per dialect (module-level), because inventory
    construction loads the full tugalex map.
    """
    inv = _rules_only_inventory(dialect_code)
    from tugaphone.tokenizer import Sentence
    return Sentence(word, dialect=inv).ipa.strip()


_INV_CACHE: Dict[str, object] = {}


def _rules_only_inventory(dialect_code: str):
    inv = _INV_CACHE.get(dialect_code)
    if inv is None:
        from tugaphone.registry import get_dialect_inventory
        inv = get_dialect_inventory(dialect_code)
        try:
            inv.IRREGULAR_WORDS = {}
        except Exception:  # frozen dataclass
            object.__setattr__(inv, "IRREGULAR_WORDS", {})
        _INV_CACHE[dialect_code] = inv
    return inv


# ─── fixtures ───────────────────────────────────────────────────────────────

def fixture_path(dialect: str) -> str:
    return os.path.join(FIXTURE_DIR, f"{dialect}.tsv")


def refresh_fixtures() -> None:
    """Download the gold, sample it and rewrite every dialect fixture.

    Maintainer action (network). The dataset file's SHA-256 goes into
    each fixture header so a fixture is traceable to the exact gold it
    was drawn from.
    """
    print(f"downloading {GOLD_URL} …", file=sys.stderr)
    with urllib.request.urlopen(GOLD_URL) as resp:
        raw = resp.read()
    digest = hashlib.sha256(raw).hexdigest()
    by_region: Dict[str, Dict[str, List[str]]] = {}
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        region, word = row.get("region"), row.get("word")
        ipa = (row.get("ipa_narrow") or "").strip()
        if not region or not word or not ipa:
            continue
        variants = by_region.setdefault(region, {}).setdefault(word, [])
        if ipa not in variants:
            variants.append(ipa)

    os.makedirs(FIXTURE_DIR, exist_ok=True)
    for dialect, region in sorted(DIALECT_TO_REGION.items()):
        words = sorted(by_region.get(region, {}).items())
        rng = random.Random(SAMPLE_SEED)
        rng.shuffle(words)
        sample = sorted(words[:FIXTURE_WORDS])
        path = fixture_path(dialect)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(
                "# gold fixture: TigreGotico/"
                "portuguese-unified-pronunciation-lexicon"
                f" region={region}\n"
                f"# source sha256={digest}\n"
                f"# sample: seed={SAMPLE_SEED} words={len(sample)}"
                f" (cap {FIXTURE_WORDS})\n"
                "# columns: word<TAB>ipa_narrow (one row per variant)\n"
            )
            for word, variants in sample:
                for ipa in variants:
                    fh.write(f"{word}\t{ipa}\n")
        print(f"wrote {path} ({len(sample)} words)", file=sys.stderr)


def load_fixture(dialect: str) -> Dict[str, List[str]]:
    """word → attested IPA variants, from the committed fixture."""
    golds: Dict[str, List[str]] = {}
    with open(fixture_path(dialect), encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            word, ipa = line.rstrip("\n").split("\t")
            golds.setdefault(word, []).append(ipa)
    return golds


# ─── scoring ────────────────────────────────────────────────────────────────

def score_dialect(dialect: str, limit: Optional[int] = None) -> dict:
    golds = load_fixture(dialect)
    words = sorted(golds)
    if limit is not None:
        words = words[:limit]
    err = tot = exact = failed = 0
    confusion: Dict[Tuple[str, str], int] = {}
    for word in words:
        try:
            hyp = rules_only_ipa(word, dialect)
        except Exception:
            failed += 1
            continue
        d, n = score_word(hyp, golds[word])
        err += d
        tot += n
        if d == 0:
            exact += 1
        else:
            _count_confusions(hyp, golds[word], confusion)
    top_confusions = sorted(confusion.items(),
                            key=lambda kv: kv[1], reverse=True)[:20]
    return {
        "dialect": dialect,
        "region": DIALECT_TO_REGION[dialect],
        "n": len(words),
        "failed": failed,
        "per": round(err / tot, 4) if tot else None,
        "word_accuracy": round(exact / len(words), 4) if words else None,
        "top_confusions": [
            {"got": a, "expected": b, "count": c}
            for (a, b), c in top_confusions
        ],
        "harness_version": HARNESS_VERSION,
    }


def _count_confusions(hyp: str, golds: List[str],
                      confusion: Dict[Tuple[str, str], int]) -> None:
    """Character-level substitution/indel pairs vs the closest variant."""
    import difflib
    h = normalize(hyp)
    r = min((normalize(g) for g in golds),
            key=lambda r: _levenshtein(h, r) / max(len(r), 1))
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, h, r).get_opcodes():
        if op == "equal":
            continue
        key = (h[i1:i2], r[j1:j2])
        confusion[key] = confusion.get(key, 0) + 1


# ─── reports ────────────────────────────────────────────────────────────────

def write_reports(rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(RESULTS_JSON), exist_ok=True)
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    lines = [
        "# Scoreboard — rules-only PER per dialect",
        "",
        "Generated by `python scripts/benchmark.py` from the committed gold",
        "fixtures (`tests/data/gold/`), which are fixed-seed samples of",
        "[TigreGotico/portuguese-unified-pronunciation-lexicon]"
        "(https://huggingface.co/datasets/TigreGotico/"
        "portuguese-unified-pronunciation-lexicon).",
        "Rules-only: the lexicon exception path is emptied, so the number",
        "measures grapheme-rule quality, not lexicon lookup coverage — see",
        "[benchmarking.md](benchmarking.md).",
        "",
        "| Dialect | Gold region | Words | PER | Word accuracy |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['dialect']} | {r['region']} | {r['n']} "
            f"| {r['per']:.4f} | {r['word_accuracy']:.4f} |")
    lines.append("")
    with open(SCOREBOARD_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dialect", help="Score one dialect code only.")
    ap.add_argument("--limit", type=int, default=None,
                    help="Cap words per dialect (ad-hoc runs).")
    ap.add_argument("--refresh-fixtures", action="store_true",
                    help="Re-download the gold and rewrite the committed "
                         "fixtures (network; maintainer action).")
    args = ap.parse_args()

    if args.refresh_fixtures:
        refresh_fixtures()
        return

    dialects = [args.dialect] if args.dialect else sorted(DIALECT_TO_REGION)
    rows = []
    for dialect in dialects:
        row = score_dialect(dialect, args.limit)
        print(f"{dialect:22} n={row['n']:5} PER={row['per']:.4f} "
              f"acc={row['word_accuracy']:.4f}")
        rows.append(row)
    if not args.dialect and args.limit is None:
        write_reports(rows)


if __name__ == "__main__":
    main()
