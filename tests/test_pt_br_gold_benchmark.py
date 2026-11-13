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


@pytest.mark.parametrize("ipa, vowel", [
    ("kaˈdejɾəs", "e"),
    ("ˈpɛ", "ɛ"),
    ("ˈlɐ̃padɐ", "ɐ"),
    ("fleksjoˈnaɾ", "a"),
    ("mesa", None),
])
def test_stressed_vowel(ipa, vowel):
    assert bench.stressed_vowel(ipa) == vowel


@pytest.mark.parametrize("left, right", [
    ("ˈvakwu", "ˈvakuu"),            # vácuo: a post-tonic glide against a hiatus
    ("ˈɔlju", "ˈɔleu"),              # óleo
    ("siˈẽsjə", "siˈẽsiɐ"),          # ciência
    ("aˈdɛptu", "aˈdepitu"),         # adepto: the epenthetic [i] after the stress
    ("ˈpaktu", "ˈpakitu"),           # pacto
    ("eˈʒipsju", "eˈʒipisiu"),       # egípcio: epenthesis and a hiatus together
    ("faˈlaɾ", "faˈla"),             # falar: a dropped infinitive ⟨r⟩
    ("ad͡ʒivoˈɡadu", "advoˈɡadu"),    # advogado: the epenthesis before the stress
    ("ˈtaksi", "ˈtaʃi"),             # táxi: the value of ⟨x⟩
    ("ˈvou", "ˈvoo"),                # a repeated vowel leaves a tie
    ("ˈɛlɐ", "ˈelɐ"),                # a mid-vowel difference is no stress difference
])
def test_notation_is_no_stress_difference(left, right):
    assert bench.same_stress(left, right)
    assert bench.same_stress(right, left)


@pytest.mark.parametrize("left, right", [
    ("saˈidɐ", "ˈsajdɐ"),            # saída
    ("paˈpa", "ˈpapa"),
    ("abadiˈa", "abaˈd͡ʒiɐ"),         # abadia: Michaelis against the rules
    ("owˈzadiə", "owzaˈd͡ʒiɐ"),       # ousadia
    ("iɾakũˈdu", "iɾaˈkũdu"),        # iracundo
    ("aˈlastɾaɾ", "alasˈtɾa"),       # alastrar
    ("baˈu", "ˈbaw"),                # baú against a falling diphthong
    ("kaˈfɛ", "ˈkafe"),
])
def test_a_true_stress_miss_stays_a_miss(left, right):
    assert not bench.same_stress(left, right)
    assert not bench.same_stress(right, left)


def test_a_reading_with_no_stress_mark_never_agrees():
    assert not bench.same_stress("mesa", "ˈmezɐ")


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
        "words": 4, "source_unmarked": 0, "rules_unmarked": 0, "stress": 3 / 4, "stress_n": 4,
        "stress_misses": 1, "mid": 1 / 2, "mid_n": 2, "misses": [("café", "ˈkafe", "kaˈfɛ")]}


def test_stress_counts_keep_the_input_and_the_unmarked_words():
    golds = {"mesa": ["meza"], "de": ["ˈd͡ʒi"], "gato": ["ˈɡatu"], "pacto": ["ˈpaktu"]}
    out = {"mesa": "ˈmezɐ", "de": "d͡ʒi", "gato": "ɡaˈtu", "pacto": "ˈpakitu"}
    scored = bench.score_stress_quality(golds, out.get)
    assert (scored["words"], scored["source_unmarked"], scored["rules_unmarked"],
            scored["stress_n"], scored["stress_misses"]) == (4, 1, 1, 2, 1)
    assert scored["stress"] == 1 / 2


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
        "words": 2, "stress": 1 / 2, "stress_n": 2, "stress_misses": 1, "mid": 0.0, "mid_n": 1,
        "misses": [("gato", "ˈɡatʊ", "ɡaˈtu")]}


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


def test_a_lexicon_word_leaves_the_row():
    golds = {"táxi": ["ˈtaksi"], "casa": ["ˈkazɐ"]}
    assert bench.beyond_lexicon(golds, {"táxi": "ˈtaksi"}) == {"casa": ["ˈkazɐ"]}
    assert bench.beyond_lexicon(golds, {}) == golds
