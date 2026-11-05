"""The pure steps of scripts/pt_br_gold_benchmark.py, on hand-worked values."""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "pt_br_gold_benchmark.py"
spec = importlib.util.spec_from_file_location("pt_br_gold_benchmark", SCRIPT)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


@pytest.mark.parametrize("transcription, ipa", [
    ("KÁ-@DÊY-Ŕ6S", "kaˈdejɾəs"),
    ("TŔÔW-@SÉ-ŔÃŴ", "tɾowˈsɛɾɐ̃w̃"),
    ("@HÍ7-MU", "ˈxit͡ʃmʊ"),
    ("Ê-LÊY-@SÕỸS", "elejˈsõj̃s"),
    ("@TÁR-8I", "ˈtaɣd͡ʒɪ"),
])
def test_nilc_to_ipa(transcription, ipa):
    assert bench.nilc_to_ipa(transcription) == ipa


def test_load_nilc_keeps_distinct_readings_and_drops_spelled_lines(tmp_path):
    path = tmp_path / "nilc.txt"
    path.write_text(
        "seco,seco.V:P1s;@SÉ-KU\n"
        "seco,seco.A:ms;@SÊ-KU\n"
        "seco,seco.N:ms;@SÊ-KU\n"
        "urss,urss.SIGL;Ú-É-HÍ-É-SÍ-@É-SI\n"
        "srta,senhorita.ABREV;SÊ-ÑÔ-@ŔÍ-T6\n", encoding="utf-8")
    assert bench.load_nilc(path) == {"seco": ["ˈsɛkʊ", "ˈsekʊ"]}


def test_load_aeiouado(tmp_path):
    path = tmp_path / "lexicon.csv"
    path.write_text("ROTAÇÕES\t[xo.ta.'sõỹs]\nPÁCORO\t['pa.kɔ.ɾʊ]\n", encoding="utf-8")
    assert bench.load_aeiouado(path) == {"rotações": ["xotaˈsõj̃s"], "pácoro": ["ˈpakɔɾʊ"]}


def test_load_michaelis_keeps_one_word_headwords_with_a_reading(tmp_path):
    rows = [
        {"status": "found", "headword": "Ética", "ipa": "ˈɛtikə"},
        {"status": "found", "headword": "ética", "ipa": "ˈɛtikə"},
        {"status": "found", "headword": "pé de cabra", "ipa": "ˈpɛ"},
        {"status": "found", "headword": "sem", "ipa": ""},
        {"status": "no_entry", "headword": None, "ipa": None},
    ]
    path = tmp_path / "entries.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    assert bench.load_michaelis(path) == {"ética": ["ˈɛtikə"]}


@pytest.mark.parametrize("ipa, from_end, vowel", [
    ("kaˈdejɾəs", 1, "e"),
    ("ˈpɛ", 0, "ɛ"),
    ("ˈlɐ̃padɐ", 2, "ɐ"),
    ("fleksjoˈnaɾ", 0, "a"),
    ("mesa", None, None),
])
def test_stress_position_and_vowel(ipa, from_end, vowel):
    assert bench.stress_from_end(ipa) == from_end
    assert bench.stressed_vowel(ipa) == vowel


@pytest.mark.parametrize("form, coda", [
    ("[ˈdɛjs]", "s"), ("[ˈdɛjʃ]", "ʃ"), ("[aˈʁoz]", "s"), ("[ˈpaʒ]", "ʃ"),
    ("[ˈdɛj]", None), ("", None),
])
def test_coda_s(form, coda):
    assert bench.coda_s(form) == coda


def test_stress_quality_counts_a_word_once_and_mid_vowels_only():
    golds = {
        "pele": ["ˈpɛli"],             # stress right, quality wrong
        "gato": ["ˈɡatu"],             # stress right, no mid vowel
        "seco": ["ˈsɛku", "ˈseku"],    # quality right through the second reading
        "café": ["kaˈfɛ"],             # stress wrong, quality wrong
    }
    out = {"pele": "ˈpeli", "gato": "ˈɡatu", "seco": "ˈseku", "café": "ˈkafe"}
    assert bench.score_stress_quality(golds, out.get) == {
        "stress": 3 / 4, "stress_n": 4, "mid": 1 / 3, "mid_n": 3}


def test_per_folds_notation_only():
    golds = {"gato": ["ˈɡatʊ"], "carro": ["ˈkaxʊ"], "mar": ["ˈmaɾ"]}
    out = {"gato": "ˈɡatu", "carro": "ˈkaʁu", "mar": "ˈmaʁ"}

    def distance(a, b):
        return sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))

    def normalize(ipa, strip_stress, broad):
        return ipa.replace("ˈ", "")

    assert bench.score_per(golds, out.get, normalize, distance) == {
        "per": (0 + 0 + 1 / 3) / 3, "exact": 2, "n": 3}


def test_compare_sources_reads_only_the_shared_words():
    left = {"pele": ["ˈpɛlɪ"], "gato": ["ˈɡatʊ"], "só": ["ˈsɔ"]}
    right = {"pele": ["ˈpelə"], "gato": ["ɡaˈtu"], "mar": ["ˈmaɾ"]}
    assert bench.compare_sources(left, right) == {
        "stress": 1 / 2, "stress_n": 2, "mid": 0.0, "mid_n": 1}


def test_alib_scores_the_coda_by_place(tmp_path):
    path = tmp_path / "alib.tsv"
    path.write_text(
        "word\tcapital\tipa\n"
        "dez\tRio\t[ˈdɛjʃ]\n"
        "dez\tRio\t[ˈdɛjs]\n"
        "dez\tRio\t\n"
        "paz\tRio\t[ˈpaʃ]\n"
        "dez\tRecife\t[ˈdɛs]\n", encoding="utf-8")
    places = bench.load_alib(path, "capital")
    spec_of = {"Rio": "pt-BR-x-rj", "Recife": "pt-BR-x-recife"}.get
    outputs = {"pt-BR-x-rj": "ˈdɛʃ", "pt-BR-x-recife": "ˈdɛʃ"}
    assert bench.score_alib(places, spec_of, lambda word, lect: outputs[lect]) == [
        {"place": "Recife", "lect": "pt-BR-x-recife", "n": 1, "match": 0.0, "palatal": 0.0},
        {"place": "Rio", "lect": "pt-BR-x-rj", "n": 3, "match": 2 / 3, "palatal": 2 / 3},
    ]


def test_sample_is_fixed_by_the_seed():
    words = {str(i): ["x"] for i in range(50)}
    assert list(bench.sample(words, 5)) == list(bench.sample(words, 5))
    assert len(bench.sample(words, 5)) == 5


def test_every_source_prints_a_tier():
    assert set(bench.TIERS) == {"nilc", "michaelis", "aeiouado", "alib"}
    assert "never a gold target" in bench.TIERS["aeiouado"]
