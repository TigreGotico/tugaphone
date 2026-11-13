"""The sentence sets of the scriptconv gate meet the gate's contract.

Each set has at least 200 rows and at least 30 gold rows in each category. Each
row names its sources, and pt-PT gold carries no Lisbon trait.
"""
import csv
import importlib.util
from collections import Counter
from pathlib import Path

import pytest

HERE = Path(__file__).parent / "data" / "sentences"
COLUMNS = ["id", "lang", "category", "text", "expected_ipa", "source", "tier"]
CATEGORIES = {"plain", "number", "date", "abbreviation", "homograph", "contact"}
LANGS = ["pt-PT", "pt-BR"]


def _build():
    spec = importlib.util.spec_from_file_location("sentence_build", HERE / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(name):
    with open(HERE / name, encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        header = next(reader)
        return header, [dict(zip(header, fields)) for fields in reader]


@pytest.mark.parametrize("lang", LANGS)
def test_rows_follow_the_contract(lang):
    header, rows = read(f"{lang}.tsv")
    assert header == COLUMNS
    assert all(len(row) == len(COLUMNS) for row in rows)
    assert {row["lang"] for row in rows} == {lang}
    assert {row["category"] for row in rows} == CATEGORIES
    assert {row["tier"] for row in rows} <= {"gold", "silver"}
    assert len({row["id"] for row in rows}) == len(rows)
    assert len({row["text"] for row in rows}) == len(rows)
    assert all(row["text"] and row["expected_ipa"] and row["source"] for row in rows)


@pytest.mark.parametrize("lang", LANGS)
def test_counts_meet_the_minimum(lang):
    _, rows = read(f"{lang}.tsv")
    gold = Counter(row["category"] for row in rows if row["tier"] == "gold")
    assert len(rows) >= 200
    assert min(gold[category] for category in CATEGORIES) >= 30


@pytest.mark.parametrize("lang", LANGS)
def test_each_row_names_its_sources(lang):
    _, rows = read(f"{lang}.tsv")
    for row in rows:
        assert row["source"].startswith("upl@23898e1 "), row["id"]
        if row["tier"] == "silver":
            assert "silver:" in row["source"], row["id"]
        else:
            assert "=unsourced" not in row["source"], row["id"]
            if row["category"] in ("number", "date", "abbreviation"):
                assert "reading:" in row["source"], row["id"]
            if row["category"] == "homograph":
                assert "homograph:" in row["source"], row["id"]


@pytest.mark.parametrize("lang", LANGS)
def test_the_set_is_built_from_its_spec(lang):
    _, spec = read(f"{lang}.spec.tsv")
    _, rows = read(f"{lang}.tsv")
    assert [(r["id"], r["category"], r["text"]) for r in spec] == \
        [(r["id"], r["category"], r["text"]) for r in rows]


def test_pt_pt_gold_has_no_lisbon_trait():
    build = _build()
    _, spec = read("pt-PT.spec.tsv")
    _, rows = read("pt-PT.tsv")
    checked = 0
    for entry, row in zip(spec, rows):
        if row["tier"] != "gold":
            continue
        reading = entry["reading"] if entry["reading"] != "-" else entry["text"]
        tokens = (reading.split() if entry["reading"] != "-" else build.words(reading))
        words = [t.strip(".,;:!?«»\"()").lower().split("@")[0].split("=")[0] for t in tokens]
        ipas = row["expected_ipa"].split()
        assert len(words) == len(ipas), row["id"]
        for word, ipa in zip(words, ipas):
            assert build.lisbon_trait(word, ipa) is None, (row["id"], word, ipa)
            checked += 1
    assert checked > 1000


@pytest.mark.parametrize("word,ipa,trait", [
    ("leite", "ˈlɐjtɨ", "⟨ei⟩ as [ɐj]"),
    ("tenho", "ˈtɐɲu", "stressed ⟨e⟩ as [ɐ] before a palatal"),
    ("sexto", "ˈsɐjʃtu", "stressed ⟨e⟩ as [ɐ] before a palatal"),
    ("leite", "ˈlejtɨ", None),
    ("tenho", "ˈteɲu", None),
    ("caixa", "ˈkajʃɐ", None),
])
def test_the_lisbon_check(word, ipa, trait):
    assert _build().lisbon_trait(word, ipa) == trait


@pytest.mark.parametrize("ipa,word,lang,expected", [
    ("ˈpɐrɐ", "para", "pt-PT", "ˈpɐɾɐ"),
    ("ˈkaʀu", "carro", "pt-PT", "ˈkaʁu"),
    ("ˈvĩtə", "vinte", "pt-PT", "ˈvĩtɨ"),
    ("ɐj̃", "em", "pt-PT", "ɐ̃j̃"),
    ("ˈnãw", "não", "pt-BR", "ˈnɐ̃w̃"),
    ("ˈsei̯s", "seis", "pt-BR", "ˈsejs"),
    ("'gatu", "gato", "pt-BR", "ˈɡatu"),
    ("ˈɔʎʊ", "olho", "pt-BR", "ˈɔʎu"),
])
def test_notation_changes_symbols_only(ipa, word, lang, expected):
    assert _build().notation(ipa, word, lang) == expected
