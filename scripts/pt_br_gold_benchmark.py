"""Score tugaphone against the Brazilian Portuguese pronunciation sources.

No single source is a gold for every feature, so each report row prints the
source's tier beside its number and scores only what that source can show.

    python scripts/pt_br_gold_benchmark.py --nilc unitex_sample_transcribed.txt \\
        --aeiouado aeiouado-ipa-01.csv --michaelis entries.jsonl \\
        --alib-capitals alib-capitals-coda-s.tsv --alib-bahia alib-bahia-coda-s.tsv

Each source is optional. The default lects are ``pt-BR`` and ``pt-BR-x-sp``.
``orthography2ipa`` scoring comes from the same harness as
``scripts/tts_gold_benchmark.py``, so ``$O2I_ROOT`` must name a checkout.

The sources, and what each one scores:

- The NILC Aeiouadô training file is a word gold for São Paulo speech. It scores
  PER, stress position and stressed e/o quality. PER folds the file's notation
  ([ɪ ʊ ə] and the fricative rhotics) into the spec's symbols, and it folds
  nothing else, so a ``pt-BR-x-sp`` row pays for the tap and the dropped
  infinitive ⟨r⟩ that the spec writes and the file does not.
- Michaelis prints a broad notation with no [tʃ dʒ] and no regional coda. It
  scores stress position and stressed e/o quality, and never PER. Some of its
  entries place the stress mark on the wrong vowel (chato [ʃa′tu]) or print the
  reading of another word (erótico [eroz′ivu]), so a miss against it is a lead
  to read, and no word rests on it alone.
- The Aeiouadô published lexicon is machine-generated. Its row is a comparison
  on a fixed sample and is never a gold target.
- ALiB scores only the coda /S/ of six words, one row per city, against the
  regional spec of that city.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable, Optional

TIERS = {
    "nilc": "human-revised by one research team, not independently verified",
    "michaelis": "broad notation, editor-made, method unstated, "
                 "some stress marks misplaced and some readings of another word",
    "aeiouado": "machine-generated, comparison only, never a gold target",
    "alib": "expert-human, narrow",
}

#: The symbols of the NILC converter, in the order that its ``_conv2ipa`` applies
#: them, with the glides and the nasal vowels in the IPA of the spec.
NILC_SYMBOLS = (
    ("P", "p"), ("B", "b"), ("T", "t"), ("D", "d"), ("K", "k"), ("G", "ɡ"),
    ("7", "t͡ʃ"), ("8", "d͡ʒ"), ("M", "m"), ("Ñ", "ɲ"), ("N", "n"), ("F", "f"),
    ("V", "v"), ("S", "s"), ("Z", "z"), ("X", "ʃ"), ("J", "ʒ"), ("Ĺ", "ʎ"),
    ("L", "l"), ("Ŕ", "ɾ"), ("H", "x"), ("R", "ɣ"), ("Q", "ks"), ("Ŵ", "w̃"),
    ("W", "w"), ("Ỹ", "j̃"), ("Y", "j"), ("Á", "a"), ("6", "ə"), ("É", "ɛ"),
    ("Ê", "e"), ("Ý", "i"), ("Í", "i"), ("I", "ɪ"), ("Ó", "ɔ"), ("Ô", "o"),
    ("Ú", "u"), ("U", "ʊ"), ("Ã", "ɐ̃"), ("Ẽ", "ẽ"), ("Ĩ", "ĩ"), ("Õ", "õ"),
    ("Ũ", "ũ"),
)

#: One symbol of the spec for each notation of the same sound in the sources.
NOTATION_FOLD = {"ɪ": "i", "ʊ": "u", "ə": "ɐ", "x": "ʁ", "ɣ": "ʁ", "h": "ʁ",
                 "ɦ": "ʁ", "χ": "ʁ", "ʌ": "ɐ", "y": "j"}

VOWELS = frozenset("aɐeɛəɨioɔuʊɪ")
VOCALIC = VOWELS | frozenset("jw")
VOWEL_FOLD = {"ɐ": "a", "ə": "a", "ʌ": "a", "ɛ": "e", "ɔ": "o", "ɪ": "i", "ʊ": "u", "ɨ": "i"}
TIE_BAR = "\u0361"
MID_VOWELS = frozenset("eɛoɔ")

#: The regional spec of a city, in lower case, where the ``location`` of the
#: spec names that city. Every other city scores against ``pt-BR``.
CITY_SPECS = {
    "rio de janeiro": "pt-BR-x-rj",
    "são paulo": "pt-BR-x-sp",
    "salvador": "pt-BR-x-bahia",
    "recife": "pt-BR-x-recife",
    "fortaleza": "pt-BR-x-ce",
    "belo horizonte": "pt-BR-x-mg",
    "curitiba": "pt-BR-x-pr",
    "porto alegre": "pt-BR-x-sul",
    "belém": "pt-BR-x-norte",
    "manaus": "pt-BR-x-norte",
    "florianópolis": "pt-BR-x-floripa",
    "cuiabá": "pt-BR-x-cuiaba",
}


def nilc_to_ipa(transcription: str) -> str:
    """A NILC transcription in IPA, with ``ˈ`` before the stressed syllable."""
    text = unicodedata.normalize("NFC", transcription)
    for symbol, ipa in NILC_SYMBOLS:
        text = text.replace(symbol, ipa)
    return text.replace("-@", "ˈ").replace("@", "ˈ").replace("-", "")


def load_nilc(path: Path) -> dict[str, list[str]]:
    """Each word of the training file and its distinct readings.

    A line is ``surface,lemma.TAG;TRANSCRIPTION``. Lines repeat per dictionary
    entry. An abbreviation or an acronym is spelled out, not read, so ``SIGL``
    and ``ABREV`` lines are left out.
    """
    words: dict[str, list[str]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        head, _, transcription = line.rpartition(";")
        surface, _, entry = head.partition(",")
        if not transcription or "SIGL" in entry or "ABREV" in entry:
            continue
        reading = nilc_to_ipa(transcription)
        word = unicodedata.normalize("NFC", surface).lower()
        if reading not in words[word]:
            words[word].append(reading)
    return dict(words)


def load_aeiouado(path: Path) -> dict[str, list[str]]:
    """The published lexicon: ``WORD<TAB>[transcription]`` in capitals."""
    words: dict[str, list[str]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        word, _, reading = line.partition("\t")
        reading = reading.strip().strip("[]").replace("'", "ˈ").replace(".", "")
        reading = reading.replace("ʊ̃", "w̃").replace("ỹ", "j̃").replace("ã", "ɐ̃")
        words[unicodedata.normalize("NFC", word).lower()].append(reading)
    return dict(words)


def load_michaelis(path: Path) -> dict[str, list[str]]:
    """The one-word headwords that Michaelis transcribes, and their readings."""
    words: dict[str, list[str]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        word, reading = row.get("headword") or "", row.get("ipa")
        if row.get("status") != "found" or not reading or not word.isalpha():
            continue
        word = unicodedata.normalize("NFC", word).lower()
        if reading not in words[word]:
            words[word].append(reading)
    return dict(words)


def fold_notation(ipa: str) -> str:
    """*ipa* with the notation of the sources folded into the spec's symbols."""
    return "".join(NOTATION_FOLD.get(c, c) for c in unicodedata.normalize("NFC", ipa))


def nuclei(ipa: str) -> list[tuple[str, bool]]:
    """``(vowel, stressed)`` per syllable nucleus of *ipa*.

    A vowel after a vowel of the same syllable cannot arise here: every source
    writes a glide as [j w], so each vowel letter is a nucleus. Combining marks
    drop, and a nasal vowel is the same letter.
    """
    out, pending = [], False
    for ch in unicodedata.normalize("NFD", ipa):
        if ch in "ˈ'":
            pending = True
        elif ch in VOWELS:
            out.append((ch, pending))
            pending = False
    return out


def stressed_vowel(ipa: str) -> Optional[str]:
    """The letter of the stressed nucleus of *ipa*, or ``None``."""
    return next((vowel for vowel, stressed in nuclei(ipa) if stressed), None)


def sounds(ipa: str) -> tuple[list[str], Optional[int]]:
    """The sounds of *ipa*, and the index of its stressed vowel or ``None``.

    Combining marks drop, so a nasal vowel is its oral letter and a nasal glide
    its plain glide. A tie bar keeps an affricate as one sound. Vowel notations
    and mid-vowel heights fold together, because a stress comparison asks where
    the stress falls, not which vowel carries it.
    """
    out: list[str] = []
    stressed, pending, tied = None, False, False
    for ch in unicodedata.normalize("NFD", ipa):
        if ch in "ˈ'":
            pending = True
        elif ch == TIE_BAR:
            tied = True
        elif not unicodedata.combining(ch) and ch != ".":
            if tied:
                out[-1] += ch
                tied = False
                continue
            out.append(VOWEL_FOLD.get(ch, ch))
            if pending and ch in VOWELS:
                stressed, pending = len(out) - 1, False
    return out, stressed


def pair_cost(a: str, b: str) -> float:
    """The cost of aligning sound *a* with sound *b*.

    A vowel pairs freely with a vowel or a glide, and a consonant with a
    consonant. A vowel against a consonant costs more than two gaps, so an
    alignment never makes that pair.
    """
    if a == b:
        return 0.0
    if (a in VOCALIC) == (b in VOCALIC):
        return 0.5
    return 3.0


def alignment_cost(a: list[str], b: list[str]) -> float:
    """The cost of the cheapest alignment of *a* with *b*, one per gap."""
    row = [float(j) for j in range(len(b) + 1)]
    for i, x in enumerate(a, 1):
        last, row[0] = row[0], float(i)
        for j, y in enumerate(b, 1):
            last, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, last + pair_cost(x, y))
    return row[-1]


def same_stress(left: str, right: str) -> bool:
    """Whether two readings put the stress on the same vowel of the word.

    Counting nuclei measures the notation: a glide against a hiatus after the
    stress (vácuo [ˈvakwu], [ˈvakuu]), an epenthetic [i] (pacto [ˈpaktu],
    [ˈpakitu]) and a dropped infinitive ⟨r⟩ all change the count and not the
    stress. So the readings are aligned sound by sound, and the stress agrees
    when a cheapest alignment pairs the two stressed vowels.
    """
    a, i = sounds(left)
    b, j = sounds(right)
    if i is None or j is None:
        return False
    through = (alignment_cost(a[:i], b[:j]) + pair_cost(a[i], b[j])
               + alignment_cost(a[i + 1:], b[j + 1:]))
    return through <= alignment_cost(a, b)


def coda_s(form: str) -> Optional[str]:
    """The class of the final coda sibilant of *form*: ``s``, ``ʃ`` or ``None``.

    Voicing does not count, because the six ALiB words stand before a pause.
    """
    letters = [c for c in unicodedata.normalize("NFD", form) if c.isalpha()]
    return {"s": "s", "z": "s", "ʃ": "ʃ", "ʒ": "ʃ"}.get(letters[-1] if letters else "")


def share(hits: int, total: int) -> float:
    return hits / total if total else float("nan")


def score_stress_quality(golds: dict[str, list[str]], hyp: Callable[[str], str]) -> dict:
    """Stress and stressed e/o agreement of the rules with *golds*.

    A word counts when any of its readings agrees. Two kinds of word cannot
    show a stress position, and each has its count: a word with no stress mark
    in any reading (``source_unmarked``), and a clitic or a bare letter, which
    the rules leave without a stress mark (``rules_unmarked``). So ``words`` is
    ``stress_n`` plus those two. Stressed e/o quality counts the words where
    the rules stress the vowel that a reading stresses, and that vowel is a mid
    vowel. ``misses`` lists each stress miss as ``(word, rules, readings)``,
    with spaces between readings.
    """
    stress = stress_n = mid = mid_n = source_unmarked = rules_unmarked = 0
    misses = []
    for word, readings in golds.items():
        out = hyp(word)
        marked = [r for r in readings if stressed_vowel(r) is not None]
        if not marked:
            source_unmarked += 1
        elif stressed_vowel(out) is None:
            rules_unmarked += 1
        else:
            stress_n += 1
            agreeing = [r for r in marked if same_stress(r, out)]
            stress += bool(agreeing)
            if not agreeing:
                misses.append((word, out, " ".join(marked)))
            mids = [r for r in agreeing if stressed_vowel(r) in MID_VOWELS]
            if mids:
                mid_n += 1
                mid += any(stressed_vowel(r) == stressed_vowel(out) for r in mids)
    return {"words": len(golds), "source_unmarked": source_unmarked,
            "rules_unmarked": rules_unmarked, "stress": share(stress, stress_n),
            "stress_n": stress_n, "stress_misses": stress_n - stress,
            "mid": share(mid, mid_n), "mid_n": mid_n, "misses": misses}


def score_per(golds: dict[str, list[str]], hyp: Callable[[str], str], normalize: Callable,
              levenshtein: Callable) -> dict:
    """Mean best PER and exact matches of the rules against *golds*."""
    pers = []
    for word, readings in golds.items():
        out = normalize(fold_notation(hyp(word)), True, True)
        refs = [normalize(fold_notation(r), True, True) for r in readings]
        pers.append(min(levenshtein(out, ref) / max(len(ref), 1) for ref in refs))
    return {"per": share(sum(pers), len(pers)), "exact": sum(p == 0 for p in pers),
            "n": len(pers)}


def compare_sources(left: dict[str, list[str]], right: dict[str, list[str]]) -> dict:
    """Stress and stressed e/o agreement of two sources on the words they share."""
    shared = sorted(set(left) & set(right))
    stress = stress_n = mid = mid_n = 0
    misses = []
    for word in shared:
        pairs = [(a, b) for a in left[word] for b in right[word]
                 if stressed_vowel(a) is not None and stressed_vowel(b) is not None]
        if pairs:
            stress_n += 1
            agreeing = [(a, b) for a, b in pairs if same_stress(a, b)]
            stress += bool(agreeing)
            if not agreeing:
                misses.append((word, " ".join(left[word]), " ".join(right[word])))
            mids = [(a, b) for a, b in agreeing
                    if stressed_vowel(a) in MID_VOWELS and stressed_vowel(b) in MID_VOWELS]
            if mids:
                mid_n += 1
                mid += any(stressed_vowel(a) == stressed_vowel(b) for a, b in mids)
    return {"words": len(shared), "stress": share(stress, stress_n), "stress_n": stress_n,
            "stress_misses": stress_n - stress, "mid": share(mid, mid_n), "mid_n": mid_n,
            "misses": misses}


def load_alib(path: Path, place_column: str) -> dict[str, dict[str, list[str]]]:
    """place -> word -> the printed forms. A cell with no form is left out."""
    places: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            form = (row.get("ipa") or "").strip()
            if form.startswith("["):
                places[row[place_column]][row["word"]].append(form)
    return places


def score_alib(places: dict[str, dict[str, list[str]]], spec_of: Callable[[str], str],
               hyp: Callable[[str, str], str]) -> list[dict]:
    """One row per place: the share of forms with the spec's coda /S/ class."""
    rows = []
    for place in sorted(places):
        spec = spec_of(place)
        hits = total = palatal = 0
        for word, forms in places[place].items():
            want = coda_s(hyp(word, spec))
            for form in forms:
                got = coda_s(form)
                if got is None:
                    continue
                total += 1
                palatal += got == "ʃ"
                hits += got == want
        rows.append({"place": place, "lect": spec, "n": total, "match": share(hits, total),
                     "palatal": share(palatal, total)})
    return rows


def sample(words: dict[str, list[str]], size: int, seed: int = 7) -> dict[str, list[str]]:
    """A fixed random *size* of the words, as the WikiPron measure draws it."""
    keys = sorted(words)
    random.Random(seed).shuffle(keys)
    return {w: words[w] for w in keys[:size]}


def print_rows(rows: Iterable[tuple]) -> None:
    for source, tier, lect, measure, value, n in rows:
        print(f"{source:<12}{lect:<14}{measure:<16}{value:>8.4f}{n:>7}  {tier}")


def main(argv: Optional[list[str]] = None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--nilc", type=Path, help="unitex_sample_transcribed.txt")
    ap.add_argument("--aeiouado", type=Path, help="aeiouado-ipa-01.csv")
    ap.add_argument("--michaelis", type=Path, help="entries.jsonl of the crawl")
    ap.add_argument("--alib-capitals", type=Path, help="alib-capitals-coda-s.tsv")
    ap.add_argument("--alib-bahia", type=Path, help="alib-bahia-coda-s.tsv")
    ap.add_argument("--lects", nargs="+", default=["pt-BR", "pt-BR-x-sp"])
    ap.add_argument("--aeiouado-sample", type=int, default=3000)
    ap.add_argument("--json", type=Path, help="write the report here")
    ap.add_argument("--stress-misses", type=Path, help="write each stress miss here as TSV")
    args = ap.parse_args(argv)

    from tts_gold_benchmark import O2I

    from tugaphone import phonemize

    cache: dict[tuple[str, str], str] = {}

    def hyp(word: str, lect: str) -> str:
        if (word, lect) not in cache:
            cache[word, lect] = phonemize(word, lect)
        return cache[word, lect]

    nilc = load_nilc(args.nilc) if args.nilc else {}
    aeiouado = load_aeiouado(args.aeiouado) if args.aeiouado else {}
    michaelis = load_michaelis(args.michaelis) if args.michaelis else {}
    report: dict = {"tiers": TIERS, "lects": {}, "alib": []}
    rows = []
    misses: list[tuple] = []

    def stress_counts(source: str, lect: str, scored: dict) -> dict:
        """*scored* without its miss list, which goes to ``misses``."""
        found = scored.pop("misses")
        misses.extend((source, lect, *miss) for miss in found)
        print(f"{source} {lect}: {scored['words']} words in, {scored['stress_n']} compared, "
              f"{scored.get('source_unmarked', 0)} unmarked in the source, "
              f"{scored.get('rules_unmarked', 0)} unmarked by the rules, "
              f"{scored['stress_misses']} stress misses")
        return scored

    for lect in args.lects:
        by_lect = report["lects"].setdefault(lect, {})

        def rules(word: str, lect: str = lect) -> str:
            return hyp(word, lect)

        if nilc:
            per = score_per(nilc, rules, O2I.normalize, O2I.levenshtein)
            sq = stress_counts("NILC", lect, score_stress_quality(nilc, rules))
            by_lect["nilc"] = {**per, **sq}
            rows += [("NILC", TIERS["nilc"], lect, "PER, folded", per["per"], per["n"]),
                     ("NILC", TIERS["nilc"], lect, "stress", sq["stress"], sq["stress_n"]),
                     ("NILC", TIERS["nilc"], lect, "stressed e/o", sq["mid"], sq["mid_n"])]
        if michaelis:
            sq = stress_counts("Michaelis", lect, score_stress_quality(michaelis, rules))
            by_lect["michaelis"] = sq
            rows += [("Michaelis", TIERS["michaelis"], lect, "stress", sq["stress"], sq["stress_n"]),
                     ("Michaelis", TIERS["michaelis"], lect, "stressed e/o", sq["mid"], sq["mid_n"])]
        if aeiouado:
            per = score_per(sample(aeiouado, args.aeiouado_sample), rules, O2I.normalize,
                            O2I.levenshtein)
            by_lect["aeiouado"] = per
            rows.append(("Aeiouadô", TIERS["aeiouado"], lect, "PER, folded", per["per"], per["n"]))
    if nilc and michaelis:
        both = stress_counts("NILC=Mich.", "", compare_sources(nilc, michaelis))
        report["nilc_vs_michaelis"] = both
        rows += [("NILC=Mich.", TIERS["michaelis"], "", "stress", both["stress"], both["stress_n"]),
                 ("NILC=Mich.", TIERS["michaelis"], "", "stressed e/o", both["mid"], both["mid_n"])]
    print(f"{'source':<12}{'lect':<14}{'measure':<16}{'value':>8}{'n':>7}  tier")
    print_rows(rows)

    alib = []
    if args.alib_capitals:
        alib += score_alib(load_alib(args.alib_capitals, "capital"),
                           lambda city: CITY_SPECS.get(city.lower(), "pt-BR"), hyp)
    if args.alib_bahia:
        alib += score_alib(load_alib(args.alib_bahia, "city"),
                           lambda city: "pt-BR-x-bahia", hyp)
    if alib:
        print(f"\nALiB coda /S/ ({TIERS['alib']})")
        print(f"{'place':<24}{'lect':<16}{'palatal':>8}{'match':>8}{'n':>6}")
        for row in alib:
            print(f"{row['place']:<24}{row['lect']:<16}{row['palatal']:>8.3f}"
                  f"{row['match']:>8.3f}{row['n']:>6}")
    report["alib"] = alib
    if args.stress_misses:
        args.stress_misses.write_text("source\tlect\tword\tfirst\tsecond\n" + "".join(
            "\t".join(row) + "\n" for row in misses), encoding="utf-8")
    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                             encoding="utf-8")
    return report


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
