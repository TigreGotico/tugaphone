#!/usr/bin/env python3
"""Gold-benchmark harness: rules-only PER and stress accuracy per dialect.

Scores tugaphone's RULES-ONLY mode (the lexicon exception path emptied)
against the unified Portuguese pronunciation gold, one region per
registered dialect code. Rules-only keeps the score non-circular per
word: a lexicon built from the same sources as the gold would measure
lookup coverage, not grapheme-rule quality.

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
import functools
import hashlib
import json
import os
import random
import re
import sys
import unicodedata
import urllib.request
from typing import Dict, List, Optional, Tuple

from orthography2ipa import G2P

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from tugaphone.lattice_core import pipeline  # noqa: E402
from tugaphone.registry import resolve_lect  # noqa: E402

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
HARNESS_VERSION = "3.0"


# ─── normalization + PER ────────────────────────────────────────────────────
# PER routine adapted from orthography2ipa's benchmark harness
# (scripts/benchmark.py of TigreGotico/orthography2ipa), simplified to the
# subset this word-level, single-convention gold needs.

_STRESS_MARKS = "ˈˌ"
_JOINERS = "·.|‿͜͡"

#: The segment rule of the shared phonemizer PER board: NFD; the ligatures
#: become their tied forms; stress marks, syllable dots, joiners and spaces go;
#: a segment is one base symbol with its combining marks and modifier letters,
#: and a tie bar joins the next base into the same segment (t͡ʃ is one segment).
_LIGATURES = (("ʧ", "t͡ʃ"), ("ʤ", "d͡ʒ"), ("ʦ", "t͡s"), ("ʣ", "d͡z"))
_SEG_TIES = "\u0361\u035c"
_SEG_MODIFIERS = "ʰʲʷˠˤːˑ"
_SEG_DROP = "ˈˌ.·|‿'"


#: Phone PER folds only what a source calls one phone written two ways. The
#: low nasal vowel is ⟨ɐ̃⟩ (Cruz-Ferreira 1999, Handbook of the IPA p.127;
#: Barbosa & Albano 2004, JIPA 34(2) p.229). An affricate without a tie bar is
#: the tied affricate. ⟨ⁿ ( ) '⟩ are markup, not phones.
_NOTATION = (("ã", "ɐ̃"), ("tʃ", "t͡ʃ"), ("dʒ", "d͡ʒ"),
             ("ⁿ", ""), ("(", ""), (")", ""), ("'", ""))

#: Cruz-Ferreira (1999: 127): the European [ɨ] "is often represented as /ə/".
_INFOPEDIA = (("ə", "ɨ"),)
_OTHER: tuple = ()
_REGION_NOTATION: Dict[str, tuple] = {"pt-PT": _INFOPEDIA, "pt-PT-x-lisbon": _INFOPEDIA}

#: Phoneme PER also merges the phones of one rhotic phoneme: [χ ʀ] with [ʁ]
#: (Pereira 2020, R-forte do português europeu) and the pt-BR coda [ɹ] with
#: [ɾ] (Barbosa & Albano 2004: 228, /R/ "is extremely variable in BP").
_PHONEME_MERGES = (("χ", "ʁ"), ("ʀ", "ʁ"), ("ɹ", "ɾ"))


#: European Portuguese drops or reduces the unstressed vowel of a word-initial
#: ⟨es⟩ + consonant, so [iʃ], [ɨʃ] and [ʃ] are one accepted reading. Vázquez
#: Diéguez (2015, Anuario de Estudios Filológicos 38) gives "esc- [(i)ʃk]" and
#: "est- [(i)ʃt]" on p. 250 and "Na sequência <es- + consoante> pode
#: desaparecer" on p. 265; Teyssier (1989: 28), quoted in Vázquez Diéguez (2015: 244), writes estar [(i)ʃ'tar].
_INITIAL_ES = re.compile(r"^[iɨ]?([ʃʒ])")
_ES_WORD = re.compile(r"^es[^aeiouáéíóúâêôãõàs]")


#: An unstressed high vowel before a vowel is a glide in casual European
#: speech and a vowel in careful speech. Mateus & Andrade (1998, D.E.L.T.A.
#: 14(1), §1.3): "in casual speech glides may be followed by any vowel"; §1.5
#: gives passear pas[i]ar / pas[j]ar. Both readings score as the glide.
_FRONT_BEFORE_VOWEL = re.compile("[iɨ](?=[aɐeɛɨoɔu])")
_BACK_BEFORE_VOWEL = re.compile("u(?=[aɐeɛɨioɔ])")


def accept_variants(word: str, ipa: str) -> str:
    """The normalized ``ipa`` with a word-initial ⟨es⟩ vowel removed and an
    unstressed high vowel before a vowel read as a glide."""
    if _ES_WORD.match(word.lower()):
        ipa = _INITIAL_ES.sub(r"\1", ipa)
    return _BACK_BEFORE_VOWEL.sub("w", _FRONT_BEFORE_VOWEL.sub("j", ipa))


def _folded(ipa: str, region: tuple) -> str:
    s = unicodedata.normalize("NFD", ipa)
    for written, sound in region + _NOTATION + _LIGATURES:
        s = s.replace(unicodedata.normalize("NFD", written), unicodedata.normalize("NFD", sound))
    return "".join(ch for ch in s if ch not in _SEG_DROP and not ch.isspace())


def segments(ipa: str, region: tuple = _INFOPEDIA, word: Optional[str] = None) -> List[str]:
    """The segments of ``ipa`` under the board's segment rule, after the
    notation folds. With ``word``, a word-initial ⟨es⟩ vowel is removed."""
    s = _folded(ipa, region)
    if word is not None:
        s = accept_variants(word, s)
    out: List[str] = []
    join = False
    for ch in s:
        if ch in _SEG_TIES:
            join = bool(out)
            if out:
                out[-1] += "\u0361"
        elif out and (join or unicodedata.combining(ch) or ch in _SEG_MODIFIERS):
            out[-1] += ch
            join = False
        else:
            out.append(ch)
    return out


def normalize(ipa: str, region: tuple = _INFOPEDIA) -> str:
    """The segments of ``ipa`` joined into one string."""
    return "".join(segments(ipa, region))


def _levenshtein(a, b) -> int:
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


def score_word(hyp: str, golds: List[str], region: tuple = _INFOPEDIA,
               word: Optional[str] = None) -> Tuple[int, int]:
    """(edit distance, reference length) against the CLOSEST gold variant.

    A word with several attested pronunciations is correct if it matches
    any of them; distance and length come from the best-matching variant
    so multi-variant words are not penalised for the variants they did
    not choose.
    """
    h = segments(hyp, region, word)
    return min((_levenshtein(h, r), len(r)) for r in (segments(g, region, word) for g in golds))


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
    """``phonemize(word, dialect_code)`` with the packaged lexicon emptied."""
    return _rules_only_engine(dialect_code).transcribe(word).strip()


@functools.lru_cache(maxsize=None)
def _rules_only_engine(dialect_code: str) -> G2P:
    lect = resolve_lect(dialect_code)
    rules = pipeline(lect)
    rules.lexicon.clear()
    return G2P(lect, pipeline=rules)


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
    region = _REGION_NOTATION.get(dialect, _OTHER)
    words = sorted(golds)
    if limit is not None:
        words = words[:limit]
    european = dialect.startswith("pt-PT")
    err = tot = exact = failed = n_stress = stress_hits = 0
    err_acc = tot_acc = err_ph = tot_ph = 0
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
        d, n = score_word(hyp, golds[word], region)
        err += d
        tot += n
        d_ph, n_ph = score_word(hyp, golds[word], region + _PHONEME_MERGES)
        err_ph += d_ph
        tot_ph += n_ph
        if european:
            d_acc, n_acc = score_word(hyp, golds[word], region, word)
            err_acc += d_acc
            tot_acc += n_acc
        if d == 0:
            exact += 1
        else:
            _count_confusions(hyp, golds[word], confusion, region)
    top_confusions = sorted(confusion.items(),
                            key=lambda kv: kv[1], reverse=True)[:20]
    return {
        "dialect": dialect,
        "region": DIALECT_TO_REGION[dialect],
        "n": len(words),
        "failed": failed,
        "per": round(err / tot, 4) if tot else None,
        "per_phoneme": round(err_ph / tot_ph, 4) if tot_ph else None,
        "per_accepted": round(err_acc / tot_acc, 4) if tot_acc else None,
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
                      confusion: Dict[Tuple[str, str], int],
                      region: tuple) -> None:
    """Character-level substitution/indel pairs vs the closest variant."""
    import difflib
    h = normalize(hyp, region)
    r = min((normalize(g, region) for g in golds),
            key=lambda r: (_levenshtein(h, r), len(r)))
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, h, r).get_opcodes():
        if op == "equal":
            continue
        key = (h[i1:i2], r[j1:j2])
        confusion[key] = confusion.get(key, 0) + 1


# ─── reports ────────────────────────────────────────────────────────────────

def scoreboard_alt(rows: List[dict]) -> str:
    """Alt text of the scoreboard figure, read from the same rows as the table."""
    by_per = sorted(rows, key=lambda r: r["per"])
    low, high = by_per[0], by_per[-1]
    return (f"Rules-only PER by dialect: {low['dialect']} {low['per']:.3f}, the lowest, and "
            f"{high['dialect']} {high['per']:.3f}, the highest.")


def write_reports(rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(RESULTS_JSON), exist_ok=True)
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    lines = [
        "# Scoreboard: rules-only PER and stress accuracy per dialect",
        "<!-- agent-hint",
        "covers: the rules-only PER and stress accuracy of each dialect",
        "source: benchmarks/results.json, tests/data/gold/",
        "generated: yes, by scripts/benchmark.py. Edit the generator, not the page",
        (
            'verify: .venv/bin/python -c "import json,re;r={x['
            "'dialect']:x for x in json.load(open('be"
            "nchmarks/results.json'))};t=re.findall(r"
            "'^\\\\| (\\\\S+) \\\\| \\\\S+ \\\\| (\\\\d+) \\\\| ([\\"
            "\\d.]+) \\\\|',open('docs/scoreboard.md').r"
            'ead(),re.M);assert len(t)==len(r) and al'
            "l(float(p)==r[d]['per'] and int(n)==r[d]"
            '[\'n\'] for d,n,p in t)"'
        ),
        "see: benchmarking.md",
        "-->",
        "",
        "Generated by `python scripts/benchmark.py` from the committed gold",
        "fixtures (`tests/data/gold/`), which are fixed-seed samples of",
        "[TigreGotico/portuguese-unified-pronunciation-lexicon]"
        "(https://huggingface.co/datasets/TigreGotico/"
        "portuguese-unified-pronunciation-lexicon).",
        "",
        "Rules-only: the packaged lexicon is emptied, so the number measures",
        "the rules, not the lexicon. See [benchmarking.md](benchmarking.md).",
        "",
        "Stress accuracy is the share of the stress-eligible gold words",
        "(one word, one primary mark, two syllables or more) whose primary",
        "stress lands on the gold's syllable. PER cannot see that choice.",
        "",
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="img/scoreboard-dark.svg">',
        f'  <img alt="{scoreboard_alt(rows)}" src="img/scoreboard.svg">',
        "</picture>",
        "",
        "`img/plot_scoreboard.py` makes this figure from",
        "`benchmarks/results.json`.",
        "",
        "PER with initial es- accepted counts [iʃ], [ɨʃ] and [ʃ] as one reading",
        "of a word-initial ⟨es⟩ + consonant in the European dialects",
        "(Vázquez Diéguez 2015: 250, 265; Teyssier 1989: 28, quoted in Vázquez Diéguez 2015: 244).",
        "",
        "| Dialect | Gold region | Words | PER | PER, initial es- accepted "
        "| Word accuracy | Stress words | Stress accuracy |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        stress = ("n/a" if r.get("stress_acc") is None
                  else f"{r['stress_acc']:.4f}")
        accepted = ("n/a" if r.get("per_accepted") is None
                    else f"{r['per_accepted']:.4f}")
        lines.append(
            f"| {r['dialect']} | {r['region']} | {r['n']} "
            f"| {r['per']:.4f} | {accepted} | {r['word_accuracy']:.4f} "
            f"| {r.get('n_stress', 0)} | {stress} |")
    lines += [
        "",
        "",
        "---",
        "[← Benchmarking](benchmarking.md) · [Home](index.md)",
        "",
    ]
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
