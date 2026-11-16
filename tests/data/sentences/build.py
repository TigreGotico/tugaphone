"""Build the sentence sets of the scriptconv sentence gate from their specs.

    python tests/data/sentences/build.py pt-PT pt-BR

Each spec row gives a sentence and the words a reader says for it. This script
looks up the IPA of each spoken word in the human rows of the Portuguese
unified pronunciation lexicon, at a fixed revision, and writes
``<lang>.tsv``. The README in this folder states the rules.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
DATASET = "TigreGotico/portuguese-unified-pronunciation-lexicon"
REVISION = "23898e1437dc77e84681bb7ce5580a9b3e2d04ba"
URLS = {"I": "infopedia_url", "M": "michaelis_url", "W": "wiktionary_url"}
# bifonia's Infopédia reading of each sense of a heterophonic homograph.
BIFONIA = ("https://raw.githubusercontent.com/TigreGotico/bifonia/"
           "4bf96deea757024c42968631d37d309511911c69/bifonia/data/infopedia_pt.csv")
# Source letters by priority, then the regions each letter is read from.
PRIORITY = {
    "pt-PT": [("I", "pt-PT"), ("W", "pt-PT"), ("W", "pt")],
    "pt-BR": [("M", "pt-BR"), ("W", "pt-BR"), ("W", "pt")],
}
COLUMNS = ("id", "lang", "category", "text", "expected_ipa", "source", "tier")
SPEC_COLUMNS = ("id", "category", "text", "reading", "cite")
NEEDS_CITE = ("number", "date", "abbreviation", "homograph")
VOWELS = "aeiouɐɛɔɨ"
TILDE = "̃"
# Cited readings that the lexicon lacks or gives only as a letter name.
# Each key is "word=ipa" as a spec token writes it.
CITED = {
    "pt-PT": {
        "a=ɐ": "CF130",
    },
    "pt-BR": {},
}
# The reading a word takes when its spec token picks none. Each other reading
# of these words in the lexicon is the name of the letter.
DEFAULT_PICKS = {
    "pt-PT": {"o": "o@u", "e": "e@i", "a": "a=ɐ"},
    "pt-BR": {"o": "o@u", "e": "e@i"},
}
CITED_SOURCES = {
    "CF130": "Cruz-Ferreira 1999, Handbook of the IPA, p. 130: the article and the preposition a are [ɐ]",
}


def load_lexicon(path: str) -> dict[tuple[str, str], list[dict]]:
    """The human rows of the lexicon, by (lowercase word, region)."""
    rows: dict[tuple[str, str], list[dict]] = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if any(row[url] for url in URLS.values()):
                rows[(row["word"].lower(), row["region"])].append(row)
    return rows


def r_units(word: str) -> list[str]:
    """The rhotic of each written r of *word*, by its place in the spelling."""
    units, i = [], 0
    while i < len(word):
        if word[i] == "r":
            if word[i:i + 2] == "rr":
                units.append("ʁ")
                i += 2
                continue
            units.append("ʁ" if i == 0 or word[i - 1] in "nls" else "ɾ")
        i += 1
    return units


def notation(ipa: str, word: str, lang: str) -> str:
    """*ipa* in the notation of the gate. Each change is a symbol, not a sound."""
    s = unicodedata.normalize("NFD", ipa)
    for old, new in (("'", "ˈ"), ("g", "ɡ"), (".", ""), ("(", ""), (")", ""),
                     ("i̯", "j"), ("u̯", "w"), ("ʀ", "ʁ"), ("ɪ", "i"), ("ʊ", "u")):
        s = s.replace(old, new)
    s = s.replace("ə", "ɨ" if lang == "pt-PT" else "ɐ")
    if lang == "pt-BR":
        s = s.replace("a" + TILDE, "ɐ" + TILDE)
    # Both elements of a nasal diphthong carry the tilde.
    s = re.sub(rf"([{VOWELS}]){TILDE}([jw])(?!{TILDE})", rf"\1{TILDE}\2{TILDE}", s)
    s = re.sub(rf"([{VOWELS}])([jw]){TILDE}", rf"\1{TILDE}\2{TILDE}", s)
    if "r" in s:
        units = r_units(unicodedata.normalize("NFC", word.lower()))
        rhotics = [c for c in s if c in "rɾʁ"]
        if len(rhotics) != len(units):
            raise ValueError(f"{word} {ipa}: {len(rhotics)} rhotics, {len(units)} written r")
        out, k = [], 0
        for c in s:
            if c in "rɾʁ":
                out.append(units[k] if c == "r" else c)
                k += 1
            else:
                out.append(c)
        s = "".join(out)
    return unicodedata.normalize("NFC", s)


def lisbon_trait(word: str, ipa: str) -> str | None:
    """The Lisbon trait in *ipa*, which pt-PT gold must not carry, or None."""
    if "ei" in word and "ɐj" in ipa:
        return "⟨ei⟩ as [ɐj]"
    if re.search(r"[eéê](lh|nh|ch|x|j|g[ei])", word) and re.search(r"ˈ[^ˈ]*ɐj?[ʎɲʃʒ]", ipa):
        return "stressed ⟨e⟩ as [ɐ] before a palatal"
    return None


def candidates(lexicon, word: str, lang: str) -> list[tuple[str, str]]:
    """(ipa, source letter) pairs for *word*, best source first, one per IPA."""
    seen: dict[str, str] = {}
    for letter, region in PRIORITY[lang]:
        for row in lexicon.get((word, region), []):
            if row[URLS[letter]] and row["ipa_narrow"]:
                [seen.setdefault(notation(alt.strip(), word, lang), letter) for alt in row["ipa_narrow"].split(",") if alt.strip()]
    # Infopédia writes an optional vowel as "(ə)", and the dataset keeps both
    # forms: keep the full one. For ⟨ou⟩ Infopédia gives [o] and [ow]: keep [o].
    return [(ipa, src) for ipa, src in seen.items()
            if not any(_drops_one_vowel(other, ipa) for other in seen)
            and not ("ou" in word and "ow" in ipa and ipa.replace("ow", "o") in seen)]


def _drops_one_vowel(full: str, short: str) -> bool:
    """Whether *short* is *full* with one [ɨ] left out."""
    return any(full[:i] + full[i + 1:] == short for i, c in enumerate(full) if c == "ɨ")


def load_bifonia() -> dict[str, list[tuple[str, str]]]:
    """(ipa, sense) pairs of each word of bifonia's Infopédia sense table."""
    from urllib.request import urlopen

    with urlopen(BIFONIA) as f:
        rows = csv.DictReader(f.read().decode("utf-8").splitlines())
        senses: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for row in rows:
            senses[row["word"]].append((notation(row["ipa"], row["word"], "pt-PT"), row["sense"]))
    return senses


def resolve(lexicon, token: str, lang: str, bifonia=None) -> tuple[str, str, str | None]:
    """(word, ipa, source) for one spec token; source None means not human-sourced.

    ``word`` alone takes the only reading of the best source. ``word@ipa``
    picks one of the human readings. ``word=ipa`` takes a reading from
    :data:`CITED`. ``word~ipa`` is a reading with no human source.
    """
    token = DEFAULT_PICKS[lang].get(token, token)
    if "~" in token:
        word, ipa = token.split("~")
        return word, unicodedata.normalize("NFC", ipa), None
    if "=" in token:
        if token not in CITED[lang]:
            raise ValueError(f"{token}: not in CITED[{lang}]")
        word, ipa = token.split("=")
        return word, ipa, CITED[lang][token]
    word, _, pick = token.partition("@")
    found = candidates(lexicon, word, lang)
    if pick and lang == "pt-PT" and bifonia:
        found += [(ipa, f"B:{sense}") for ipa, sense in bifonia.get(word, [])
                  if ipa not in dict(found)]
    if not found:
        raise LookupError(f"{lang} {word}: no human reading")
    if pick:
        pick = unicodedata.normalize("NFC", pick)
        for ipa, src in found:
            if ipa == pick:
                return word, ipa, src
        raise LookupError(f"{lang} {word}@{pick}: not among {[i for i, _ in found]}")
    best = found[0][1]
    top = [ipa for ipa, src in found if src == best]
    if len(top) > 1:
        raise LookupError(f"{lang} {word}: pick one of {[i for i, _ in found]}")
    return word, top[0], best


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[\w@=~ˈˌ̀-ͯ]+", text.lower())]


def build(lang: str, lexicon, bifonia=None) -> tuple[list[dict], list[str]]:
    """The rows of *lang*, and the defects of its spec."""
    out, errors = [], []
    with open(HERE / f"{lang}.spec.tsv", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        if tuple(next(reader)) != SPEC_COLUMNS:
            raise ValueError(f"{lang}.spec.tsv: header must be {SPEC_COLUMNS}")
        for n, fields in enumerate(reader, 2):
            if not fields or fields[0].startswith("#"):
                continue
            row = dict(zip(SPEC_COLUMNS, fields))
            reading = row["reading"] if row["reading"] != "-" else row["text"]
            tokens = reading.split() if row["reading"] != "-" else words(reading)
            ipas, sources, unsourced, lisbon = [], [], [], []
            before = len(errors)
            for token in tokens:
                token = token.strip(".,;:!?«»\"()").lower()
                try:
                    word, ipa, src = resolve(lexicon, token, lang, bifonia)
                except (LookupError, ValueError) as e:
                    errors.append(f"{row['id']}: {e}")
                    continue
                ipas.append(ipa)
                if src is None:
                    unsourced.append(word)
                    sources.append(f"{word}=unsourced")
                    continue
                sources.append(f"{word}={src}")
                trait = lang == "pt-PT" and lisbon_trait(word, ipa)
                if trait:
                    lisbon.append(f"{word} {trait}")
            if row["category"] in NEEDS_CITE and not row["cite"]:
                errors.append(f"{row['id']}: a {row['category']} row needs a cite")
            if lisbon:
                errors.append(f"{row['id']}: Lisbon trait in pt-PT: {lisbon}")
            if len(errors) > before:
                continue
            tier = "silver" if unsourced or row["cite"].startswith("silver:") else "gold"
            source = f"upl@{REVISION[:7]} " + " ".join(sources)
            if row["cite"]:
                source += f" | {row['cite']}"
            if unsourced and not row["cite"].startswith("silver:"):
                source += f" | silver: no human reading for {', '.join(unsourced)}"
            out.append({"id": row["id"], "lang": lang, "category": row["category"],
                        "text": row["text"], "expected_ipa": " ".join(ipas),
                        "source": source, "tier": tier})
    return out, errors


def main(langs: list[str]) -> int:
    from huggingface_hub import hf_hub_download

    path = hf_hub_download(DATASET, "portuguese_pronunciation_lexicon.jsonl",
                           repo_type="dataset", revision=REVISION)
    lexicon = load_lexicon(path)
    bifonia = load_bifonia()
    failed = False
    for lang in langs:
        rows, errors = build(lang, lexicon, bifonia)
        if errors:
            print("\n".join(f"{lang} {e}" for e in errors))
            failed = True
            continue
        with open(HERE / f"{lang}.tsv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, lineterminator="\n")
            writer.writerow(COLUMNS)
            writer.writerows([row[c] for c in COLUMNS] for row in rows)
        print(f"{lang}: {len(rows)} rows written")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
