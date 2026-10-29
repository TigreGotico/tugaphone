#!/usr/bin/env python3
"""Gold-benchmark harness: rules-only PER and stress accuracy per dialect.

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


# ─── stress accuracy ────────────────────────────────────────────────────────
# PER strips stress marks, so a transcription with every segment right and
# the primary stress on the wrong syllable scores perfect. stress_acc scores
# that syllable choice alone. The definition is shared with orthography2ipa's
# board (knowledge/wiki/audits/pt-stress/stress-metric.md): the stressed
# nucleus of the gold must align, under the edit-distance alignment of the
# stress-stripped segment strings, with the stressed nucleus of the hypothesis.

_PRIMARY = "ˈ"
_SECONDARY = "ˌ"
_TIES = "\u0361\u035c"
_VOWELS = frozenset("iyɨʉɯuɪʏʊeøɘɵɤoəɛœɜɞʌɔæɐaɶɑɒɚɝ")
_NON_SYLLABIC = "\u032f"
_SYLLABIC = ("\u0329", "\u030d")

#: Fewer eligible gold words than this report stress_acc as null.
STRESS_MIN_WORDS = 20


def _fold_stress(ipa: str) -> str:
    """NFD, with the ASCII apostrophe some golds write for ˈ folded to ˈ."""
    return unicodedata.normalize("NFD", ipa).replace("'", _PRIMARY)


def _segments(ipa: str) -> Tuple[List[str], Optional[int], int]:
    """Split a folded transcription into segments for stress scoring.

    A segment is a base character with its combining marks; a tie bar
    also takes in the character after it (``t͡ʃ``, ``e͡ɪ``). Returns the
    segments with every stress mark, syllable boundary and space removed,
    the index of the stressed nucleus, and the number of primary marks.
    The stressed nucleus is the first nucleus after the primary mark: the
    mark opens its syllable, so a written boundary cannot move it. It is
    ``None`` when the word has no primary mark or more than one.
    """
    segs: List[str] = []
    marks = 0
    stress_from = 0
    for ch in ipa:
        if unicodedata.combining(ch) or (segs and segs[-1][-1] in _TIES):
            if segs:
                segs[-1] += ch
        elif ch == _PRIMARY:
            marks += 1
            stress_from = len(segs)
        elif ch not in _SECONDARY + _JOINERS and not ch.isspace():
            segs.append(ch)
    if marks != 1:
        return segs, None, marks
    stressed = next((i for i in range(stress_from, len(segs))
                     if _is_nucleus(segs[i])), None)
    return segs, stressed, marks


def _is_nucleus(seg: str) -> bool:
    if any(mark in seg for mark in _SYLLABIC):
        return True
    return seg[0] in _VOWELS and _NON_SYLLABIC not in seg


def stress_eligible(gold: str) -> bool:
    """One word, exactly one primary mark, at least two syllables."""
    folded = _fold_stress(gold.strip())
    if any(ch.isspace() for ch in folded):
        return False
    segs, stressed, marks = _segments(folded)
    return (marks == 1 and stressed is not None
            and sum(map(_is_nucleus, segs)) >= 2)


def _align(ref: List[str], hyp: List[str]) -> Dict[int, int]:
    """ref index → hyp index for every matched or substituted segment.

    The cost is the unit-cost Levenshtein distance PER takes, so every
    alignment returned is one of PER's optimal alignments. Among those,
    ties go to the alignment that pairs the fewest nuclei with non-nuclei:
    ``meˈʎɒɹ`` against ``meˈʎɔ`` must pair ɒ with ɔ, not ɔ with ɹ.
    """
    def sub(a: str, b: str) -> Tuple[int, int]:
        return int(a != b), int(_is_nucleus(a) != _is_nucleus(b))

    def add(c: Tuple[int, int], d: Tuple[int, int]) -> Tuple[int, int]:
        return c[0] + d[0], c[1] + d[1]

    gap = (1, 0)
    n, m = len(ref), len(hyp)
    dp = [[(0, 0)] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = (i, 0)
    for j in range(1, m + 1):
        dp[0][j] = (j, 0)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = min(add(dp[i - 1][j], gap), add(dp[i][j - 1], gap),
                           add(dp[i - 1][j - 1], sub(ref[i - 1], hyp[j - 1])))
    pairs: Dict[int, int] = {}
    i, j = n, m
    while i and j:
        if dp[i][j] == add(dp[i - 1][j - 1], sub(ref[i - 1], hyp[j - 1])):
            pairs[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif dp[i][j] == add(dp[i - 1][j], gap):
            i -= 1
        else:
            j -= 1
    return pairs


def stress_hit(hyp: str, gold: str) -> bool:
    """True when *hyp* puts the primary stress on the gold's syllable.

    A hypothesis with no primary mark, or with more than one, misses.
    """
    ref, ref_nucleus, _ = _segments(_fold_stress(gold.strip()))
    out, out_nucleus, _ = _segments(_fold_stress(hyp.strip()))
    if ref_nucleus is None or out_nucleus is None:
        return False
    return _align(ref, out).get(ref_nucleus) == out_nucleus


def score_stress(word: str, hyp: str, golds: List[str]) -> Optional[bool]:
    """Stress hit against any eligible variant; None if none is eligible.

    A multi-word entry is never eligible, even when its gold is written
    without a space.
    """
    eligible = [g for g in golds if stress_eligible(g)]
    if not eligible or any(ch.isspace() for ch in word.strip()):
        return None
    return any(stress_hit(hyp, g) for g in eligible)


def stress_accuracy(hits: int, n_stress: int) -> Optional[float]:
    """The reported stress_acc: null below the eligible-word floor."""
    if n_stress < STRESS_MIN_WORDS:
        return None
    return round(hits / n_stress, 4)


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
    err = tot = exact = failed = n_stress = stress_hits = 0
    confusion: Dict[Tuple[str, str], int] = {}
    for word in words:
        try:
            hyp = rules_only_ipa(word, dialect)
        except Exception:
            failed += 1
            continue
        hit = score_stress(word, hyp, golds[word])
        if hit is not None:
            n_stress += 1
            stress_hits += hit
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
        "stress_acc": stress_accuracy(stress_hits, n_stress),
        "n_stress": n_stress,
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
        "# Scoreboard — rules-only PER and stress accuracy per dialect",
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
        "Stress accuracy is the share of the stress-eligible gold words",
        "(one word, one primary mark, two syllables or more) whose primary",
        "stress lands on the gold's syllable. PER cannot see that choice.",
        "",
        "| Dialect | Gold region | Words | PER | Word accuracy "
        "| Stress words | Stress accuracy |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        stress = ("—" if r.get("stress_acc") is None
                  else f"{r['stress_acc']:.4f}")
        lines.append(
            f"| {r['dialect']} | {r['region']} | {r['n']} "
            f"| {r['per']:.4f} | {r['word_accuracy']:.4f} "
            f"| {r.get('n_stress', 0)} | {stress} |")
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
        stress = ("-" if row["stress_acc"] is None
                  else f"{row['stress_acc']:.4f}")
        print(f"{dialect:22} n={row['n']:5} PER={row['per']:.4f} "
              f"acc={row['word_accuracy']:.4f} "
              f"stress={stress} (n={row['n_stress']})")
        rows.append(row)
    if not args.dialect and args.limit is None:
        write_reports(rows)


if __name__ == "__main__":
    main()
