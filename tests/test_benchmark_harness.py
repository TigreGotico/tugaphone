"""The gold-benchmark harness (scripts/benchmark.py).

Covers the invariants the scoreboard's honesty depends on: fixtures
exist for every registered gold dialect and are traceable to their
source, scoring is deterministic and offline, rules-only mode really
bypasses the lexicon, and multi-variant words score against their
closest variant.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import benchmark  # noqa: E402
from tugaphone import phonemize  # noqa: E402
from tugaphone.lattice_core import pipeline  # noqa: E402
from check_benchmark_regression import regression  # noqa: E402


class TestFixtures:

    @pytest.mark.parametrize("dialect", sorted(benchmark.DIALECT_TO_REGION))
    def test_fixture_exists_and_is_traceable(self, dialect):
        path = benchmark.fixture_path(dialect)
        assert os.path.exists(path), (
            f"{dialect} is registered for gold benchmarking but has no "
            f"committed fixture — run scripts/benchmark.py "
            f"--refresh-fixtures and commit the result")
        head = open(path, encoding="utf-8").read(400)
        assert "sha256=" in head, "fixture header must pin its gold source"
        assert f"seed={benchmark.SAMPLE_SEED}" in head

    @pytest.mark.parametrize("dialect", sorted(benchmark.DIALECT_TO_REGION))
    def test_fixture_loads_words_with_variants(self, dialect):
        golds = benchmark.load_fixture(dialect)
        assert golds, "fixture must not be empty"
        assert all(isinstance(v, list) and v for v in golds.values())


class TestScoring:

    def test_normalize_strips_stress_joiners_whitespace(self):
        assert benchmark.normalize("ˈka·zɐ") == "kazɐ"
        assert benchmark.normalize("k a | z ɐ") == "ka|zɐ".replace("|", "")

    def test_notation_variants_of_one_sound_compare_equal(self):
        # Cruz-Ferreira (1999: 127): the European [ɨ] is often written ⟨ə⟩.
        assert benchmark.normalize("ɐbnɔɾmə") == benchmark.normalize("ɐbnɔɾmɨ")
        # The low nasal vowel is ⟨ɐ̃⟩ in both sources.
        assert benchmark.normalize("ˈkãtu") == benchmark.normalize("ˈkɐ̃tu")
        assert benchmark.normalize("dẽⁿʧi") == benchmark.normalize("dẽt͡ʃi")

    def test_phone_per_keeps_distinct_phones_apart(self):
        # Barbosa & Albano (2004: 229) plot [ʊ ɪ] apart from [u i]; no source
        # calls ⟨r⟩ the tap or pt-BR ⟨ə⟩ the vowel [ɐ].
        other = benchmark._OTHER
        assert benchmark.normalize("ˈsakʊ", other) != benchmark.normalize("ˈsaku", other)
        assert benchmark.normalize("ˈpiɾɐ", other) != benchmark.normalize("ˈpirɐ", other)
        assert benchmark.normalize("akə̃ˈpa", other) != benchmark.normalize("akɐ̃ˈpa", other)

    def test_phoneme_per_merges_the_rhotic_phones(self):
        merged = benchmark._INFOPEDIA + benchmark._PHONEME_MERGES
        assert benchmark.normalize("ˈkaʀu", merged) == benchmark.normalize("ˈkaʁu", merged)
        assert benchmark.normalize("ˈmaχ", merged) == benchmark.normalize("ˈmaʁ", merged)
        assert benchmark.normalize("ˈkaʀu") != benchmark.normalize("ˈkaʁu")

    def test_fold_keeps_the_trill_where_the_gold_writes_it_as_r(self):
        # pt-MZ arrematar ɐrɛmɐtˈaɾ: ⟨r⟩ is the trill beside the tap ⟨ɾ⟩.
        other = benchmark._OTHER
        assert benchmark.normalize("ˈkaru", other) != benchmark.normalize("ˈkaɾu", other)

    def test_an_affricate_is_one_segment(self):
        assert benchmark.segments("ˈad͡ʒe") == ["a", "d͡ʒ", "e"]
        assert benchmark.normalize("ˈaʤe") == benchmark.normalize("ˈad͡ʒe")
        assert benchmark.normalize("adʒe") == benchmark.normalize("ˈad͡ʒe")

    def test_fold_keeps_tap_and_uvular_apart(self):
        assert benchmark.normalize("ɐʀẽdavɛɫ") != benchmark.normalize("ɐɾẽdavɛɫ")
        assert benchmark.normalize("ˈkaro") != benchmark.normalize("ˈkaʁo")

    def test_score_word_picks_closest_variant(self):
        d, n = benchmark.score_word("ˈkazɐ", ["ˈkazɐ", "ˈkasɐ"])
        assert (d, n) == (0, 4)
        d, n = benchmark.score_word("ˈkazu", ["ˈkazɐ", "totally-off"])
        assert d == 1 and n == 4

    def test_levenshtein_basics(self):
        assert benchmark._levenshtein("", "abc") == 3
        assert benchmark._levenshtein("abc", "abc") == 0
        assert benchmark._levenshtein("kazɐ", "kasɐ") == 1

    def test_score_dialect_is_deterministic(self):
        a = benchmark.score_dialect("pt-PT", limit=40)
        b = benchmark.score_dialect("pt-PT", limit=40)
        assert a == b

    def test_baseline_matches_harness_version(self):
        with open(benchmark.RESULTS_JSON, encoding="utf-8") as fh:
            rows = json.load(fh)
        assert {r["dialect"] for r in rows} == set(benchmark.DIALECT_TO_REGION)
        assert all(r["harness_version"] == benchmark.HARNESS_VERSION
                   for r in rows)


class TestRulesOnly:
    """Rules-only is the shipped phonemize path with the packaged lexicon emptied."""

    def test_lexicon_is_bypassed(self):
        # The pt-PT lexicon row is ɐbɐfɐˈɾetɨ; the rules give the open [ɛ].
        assert benchmark.rules_only_ipa("abafarete", "pt-PT") == "ɐbɐfɐˈɾɛtɨ"
        assert phonemize("abafarete", "pt-PT") == "ɐbɐfɐˈɾetɨ"

    def test_off_the_lexicon_it_is_phonemize(self):
        assert benchmark.rules_only_ipa("aguenta", "pt-PT") == phonemize("aguenta", "pt-PT")

    def test_shipped_lexicon_untouched(self):
        benchmark.rules_only_ipa("abafarete", "pt-PT")
        assert pipeline("pt-PT").lexicon["abafarete"] == "ɐbɐfɐˈɾetɨ"


class TestStress:
    """Rows of the shared stress-accuracy definition. Each expected value
    follows from the definition by hand: the gold's stressed nucleus must
    align with the hypothesis's stressed nucleus."""

    @pytest.mark.parametrize("hyp", ["ˈsajdɐ", "ˈsaidɐ"])
    def test_saida_hiatus_read_as_diphthong_misses(self, hyp):
        # gold stresses í; both readings move the stress onto a. Counting
        # nuclei from the end calls ˈsajdɐ penultimate and scores a hit.
        assert benchmark.stress_eligible("sɐˈidɐ")
        assert benchmark.stress_hit(hyp, "sɐˈidɐ") is False

    def test_saida_rules_output_with_syllable_dots_hits(self):
        assert benchmark.stress_hit("sɐ·ˈi·dɐ", "sɐˈidɐ") is True

    def test_texto_lost_glide_is_a_segment_error_not_a_stress_error(self):
        assert benchmark.stress_hit("ˈtɐʃtu", "ˈtɐjʃtu") is True

    @pytest.mark.parametrize("gold, hyp", [
        ("meˈʎɒɹ", "meˈʎɔ"),          # melhor: final consonant lost
        ("espeˈɾãⁿtʊ", "iʃpeˈɾɐ̃tʊ"),  # esperanto: nasal release lost
        ("ˌeziʒˈe͡ɪŋsjæ", "eziˈʒẽsjɐ"),  # exigência: tied diphthong
    ])
    def test_segment_loss_after_the_stressed_vowel_hits(self, gold, hyp):
        # PER-optimal alignments tie here; the stressed vowels must pair
        # with each other, not a vowel with a consonant.
        assert benchmark.stress_hit(hyp, gold) is True

    @pytest.mark.parametrize("hyp, hit", [
        ("kɐ·li·ˈfɔɾ·nj·ɐ", True),   # glide syllabified on its own
        ("kɐliˈfɔɾniɐ", True),      # final glide read as a full vowel
        ("kɐlifɔɾˈnjɐ", False),     # stress moved onto the last syllable
    ])
    def test_california_final_glide(self, hyp, hit):
        assert benchmark.stress_hit(hyp, "kɐliˈfɔɾnjɐ") is hit

    @pytest.mark.parametrize("gold", ["ˈpaj", "ˈmaɾ", "ˈsɛw"])
    def test_monosyllable_is_ineligible(self, gold):
        assert benchmark.stress_eligible(gold) is False

    def test_gold_without_a_mark_is_ineligible(self):
        assert benchmark.stress_eligible("kazɐ") is False
        assert benchmark.score_stress("casa", "ˈkazɐ", ["kazɐ"]) is None

    def test_gold_with_two_primary_marks_is_ineligible(self):
        assert benchmark.stress_eligible("ˈkaˈzɐ") is False

    def test_multiword_entry_is_ineligible(self):
        assert benchmark.stress_eligible("ˈtiu ˈuɡu") is False
        # a fixture row whose gold carries no space
        assert benchmark.score_stress(
            "Tio Hugo", "t͡ʃiu̯ˈuɡu̯", ["t͡ʃiu̯'uɡu̯"]) is None

    def test_hypothesis_with_two_marks_misses(self):
        assert benchmark.stress_hit("ˈkaˈzɐ", "ˈkazɐ") is False

    def test_hypothesis_without_a_mark_misses(self):
        assert benchmark.stress_hit("kazɐ", "ˈkazɐ") is False

    @pytest.mark.parametrize("hyp, hit", [
        ("ɡwaɾdɐˈʃuvɐ", True),
        ("ˌɡwaɾdɐˈʃuvɐ", True),
        ("ɡwaɾˈdɐʃuvɐ", False),
    ])
    def test_compound_secondary_mark_is_ignored(self, hyp, hit):
        assert benchmark.stress_eligible("ˌɡwaɾdɐˈʃuvɐ")
        assert benchmark.stress_hit(hyp, "ˌɡwaɾdɐˈʃuvɐ") is hit

    def test_ascii_apostrophe_folds_to_primary_mark(self):
        # a fixture row: Guiné ɡi'nɛ
        assert benchmark.stress_eligible("ɡi'nɛ")
        assert benchmark.stress_hit("ɡiˈnɛ", "ɡi'nɛ") is True
        assert benchmark.stress_hit("ˈɡinɛ", "ɡi'nɛ") is False

    def test_non_syllabic_vowel_is_not_a_nucleus(self):
        # gold mɐˈɾiu̯: the stressed nucleus is i, u̯ is a glide
        assert benchmark.stress_hit("mɐˈɾiu", "mɐˈɾiu̯") is True
        assert benchmark.stress_hit("mɐɾiˈu", "mɐˈɾiu̯") is False

    def test_hit_against_any_eligible_variant(self):
        golds = ["ˈɛlitɨ", "eˈlitɨ"]
        assert benchmark.score_stress("elite", "eˈlitɨ", golds) is True
        assert benchmark.score_stress("elite", "eliˈtɨ", golds) is False

    def test_accuracy_floor(self):
        assert benchmark.stress_accuracy(0, 0) is None
        assert benchmark.stress_accuracy(19, 19) is None
        assert benchmark.stress_accuracy(15, 20) == 0.75

    def test_score_dialect_reports_stress_next_to_per(self):
        row = benchmark.score_dialect("pt-PT", limit=40)
        assert 20 <= row["n_stress"] <= row["n"]
        assert 0.0 <= row["stress_acc"] <= 1.0

    def test_baseline_rows_carry_stress(self):
        with open(benchmark.RESULTS_JSON, encoding="utf-8") as fh:
            rows = json.load(fh)
        for r in rows:
            assert r["n_stress"] >= benchmark.STRESS_MIN_WORDS
            assert 0.0 < r["stress_acc"] <= 1.0


class TestRegressionRule:

    @pytest.mark.parametrize("old, new, worse, expected", [
        (0.2000, 0.2060, 1, True),     # PER up by 0.006
        (0.2000, 0.2040, 1, False),    # PER up by 0.004, inside epsilon
        (0.2000, 0.1500, 1, False),    # PER improved
        (0.9000, 0.8940, -1, True),    # stress down by 0.006
        (0.9000, 0.8960, -1, False),   # stress down by 0.004
        (0.9000, 0.9500, -1, False),   # stress improved
        (None, 0.9000, -1, False),     # no baseline score to hold
        (0.9000, None, -1, True),      # eligible words vanished
    ])
    def test_epsilon_rule(self, old, new, worse, expected):
        assert regression(old, new, worse, 0.005) is expected


class TestInitialEs:
    """Vázquez Diéguez (2015: 250) gives "est- [(i)ʃt]" for European Portuguese."""

    @pytest.mark.parametrize("hyp", ["iʃˈtaɾ", "ɨʃˈtaɾ", "ʃˈtaɾ"])
    def test_each_reading_of_estar_scores_zero(self, hyp):
        assert benchmark.score_word(hyp, ["iʃˈtaɾ"], word="estar") == (0, 4)

    def test_without_the_word_the_vowel_counts(self):
        assert benchmark.score_word("ʃˈtaɾ", ["iʃˈtaɾ"]) == (1, 5)

    @pytest.mark.parametrize("word,hyp,gold", [
        ("este", "ˈiʃtɨ", "ˈeʃtɨ"),          # stressed ⟨e⟩
        ("essência", "iˈsẽsjɐ", "eˈsẽsjɐ"),  # double ⟨ss⟩
        ("chave", "iˈʃavɨ", "ˈʃavɨ"),        # no ⟨es⟩
    ])
    def test_other_words_keep_the_vowel(self, word, hyp, gold):
        assert benchmark.score_word(hyp, [gold], word=word)[0] == 1


class TestNasalGlide:
    def test_a_nasal_glide_stays_apart_from_the_bare_glide(self):
        # No source calls [w̃] and [w] one phone, so phone PER counts the edit.
        assert benchmark.normalize("kataˈlɐ̃w̃") != benchmark.normalize("kataˈlɐ̃w")
        assert benchmark.segments("ˈmɐ̃j̃") == ["m", "ɐ̃", "j̃"]

    def test_an_oral_glide_stays_apart_from_the_nasal_vowel(self):
        assert benchmark.normalize("ˈmaw") != benchmark.normalize("ˈmɐ̃w")


class TestAcceptedGlide:
    # Mateus & Andrade (1998, §1.3, §1.5): pas[i]ar / pas[j]ar.
    def test_a_high_vowel_before_a_vowel_accepts_the_glide(self):
        assert benchmark.score_word("ɐdiɐˈmẽtu", ["ɐdjɐˈmẽtu"], word="adiamento") == (0, 8)
        assert benchmark.score_word("pɐsiˈaɾ", ["pɐsjˈaɾ"], word="passear") == (0, 6)

    def test_a_reduced_vowel_before_a_vowel_accepts_the_glide(self):
        # Cruz-Ferreira (1999: 128): an unstressed /ɨ/ before a vowel "may lose
        # its syllabicity", real /ʁɨ'al/.
        assert benchmark.score_word("ɐfɨˈavɛɫ", ["ɐˈfjavɛɫ"], word="afeável") == (0, 7)
        assert benchmark.score_word("ʁɨˈaɫ", ["ʁjˈaɫ"], word="real") == (0, 4)
        assert benchmark.score_word("ɐmɐjʒuˈaɾ", ["ɐmɐjʒˈwaɾ"], word="ameijoar") == (0, 8)

    def test_phone_per_keeps_the_glide_an_edit(self):
        assert benchmark.score_word("ɐdiɐˈmẽtu", ["ɐdjɐˈmẽtu"]) == (1, 8)


class TestStrongR:
    def test_european_strong_r_phones_are_one_segment(self):
        # Pereira (2020: iii): [ʁ, ʀ, r, χ, ...] in the Lisbon sub-region.
        assert benchmark.score_word("ɐbɐʁɨˈɡadu", ["ɐbɐʀəˈɡadu"], word="abarregado") == (0, 9)
        assert benchmark.score_word("ˈʁatu", ["ˈχatu"], word="rato") == (0, 4)

    def test_brazilian_strong_r_phones_are_one_segment(self):
        # Barbosa & Albano (2004: 228): velar, or glottal in casual speech.
        assert benchmark.score_word("ˈʁaʃɐ", ["ˈxaʃɐ"], word="racha", brazilian=True) == (0, 4)
        assert benchmark.score_word("ˈbuʁu", ["ˈbuhu"], word="burro", brazilian=True) == (0, 4)

    def test_the_tap_stays_apart_from_the_strong_r(self):
        assert benchmark.score_word("ˈkaʁu", ["ˈkaɾu"], word="caro") == (1, 4)

    def test_phone_per_keeps_the_strong_r_an_edit(self):
        assert benchmark.score_word("ˈʁatu", ["ˈʀatu"]) == (1, 4)


def test_comma_joined_infopedia_readings_are_variants(tmp_path, monkeypatch):
    fixture = tmp_path / "pt-PT.tsv"
    fixture.write_text("# header\nabadejo\tɐbɐˈdɐʒu,ɐbɐˈdeʒu\tinfopedia\n", encoding="utf-8")
    monkeypatch.setattr(benchmark, "fixture_path", lambda dialect: str(fixture))
    assert benchmark.load_fixture("pt-PT") == {"abadejo": ["ɐbɐˈdɐʒu", "ɐbɐˈdeʒu"]}


class TestBrazilianNasal:
    # Barbosa & Albano (2004: 229, 230).
    def test_the_glide_after_a_nasal_vowel_is_one_segment(self):
        assert benchmark._score_rows("katɐˈlɐ̃w̃", [("katɐˈlɐ̃w", "wiktionary")], "pt-BR")[:2] == (0, 7)
        assert benchmark._score_rows("tɐ̃ˈbẽj̃", [("tɐ̃ˈbẽj", "wiktionary")], "pt-BR")[:2] == (0, 5)

    def test_an_oral_glide_after_an_oral_vowel_stays(self):
        assert benchmark._score_rows("ˈpaw̃", [("ˈpaw", "wiktionary")], "pt-BR")[:2] == (1, 3)

    def test_a_stressed_vowel_before_a_nasal_onset_is_one_reading(self):
        assert benchmark.score_word("ˈsĩmu", ["ˈsimu"], word="cimo", brazilian=True) == (0, 4)
        assert benchmark.score_word("kamĩˈɲɐ̃du", ["kamiˈɲɐ̃du"], word="caminhando", brazilian=True) == (0, 8)

    def test_an_unstressed_vowel_before_m_or_n_stays_nasal(self):
        assert benchmark.score_word("bɐ̃ˈnɐnɐ", ["baˈnɐnɐ"], word="banana", brazilian=True) == (1, 6)

    def test_an_unstressed_a_is_one_reading(self):
        assert benchmark.score_word("akõˈtesi", ["ɐkõˈtesi"], word="acontece", brazilian=True) == (0, 7)
        assert benchmark.score_word("ˈsiɾɐ", ["ˈsiɾa"], word="Cira", brazilian=True) == (0, 4)
        assert benchmark._score_rows("ˈsɛlulɐ", [("ˈsɛlulə", "wiktionary")], "pt-BR",
                                     word="célula", brazilian=True)[:2] == (0, 6)

    def test_a_stressed_a_and_a_pretonic_a_before_a_nasal_stay(self):
        assert benchmark.score_word("ˈkasɐ", ["ˈkɐsɐ"], word="casa", brazilian=True) == (1, 4)
        assert benchmark.score_word("bɐˈnɐnɐ", ["baˈnɐnɐ"], word="banana", brazilian=True) == (1, 6)
        assert benchmark.score_word("ˈsiɾɐ", ["ˈsiɾa"], word="Cira") == (1, 4)

    def test_european_rows_keep_the_nasal_vowel(self):
        assert benchmark.score_word("ˈsĩmu", ["ˈsimu"], word="cimo") == (1, 4)


class TestBrazilianFinalR:
    # Barbosa & Albano (2004: 228); Callou, Moraes & Leite (1998: 67).
    def test_a_word_final_rhotic_is_optional(self):
        assert benchmark.score_word("kõˈpɾa", ["kõˈpɾaɾ"], word="comprar", brazilian=True) == (0, 5)
        assert benchmark.score_word("laˈɡa", ["laˈɡaʁ"], word="lagar", brazilian=True) == (0, 4)

    def test_an_added_rhotic_stays_an_edit(self):
        assert benchmark.score_word("ˈpaɾ", ["ˈpa"], word="pá", brazilian=True) == (1, 2)

    def test_a_medial_rhotic_stays(self):
        assert benchmark.score_word("ˈkata", ["ˈkaɾta"], word="carta", brazilian=True) == (1, 5)

    def test_european_rows_keep_the_final_rhotic(self):
        assert benchmark.score_word("kõˈpɾa", ["kõˈpɾaɾ"], word="comprar") == (1, 6)


class TestBrazilianCodaS:
    # Barbosa & Albano (2004: 229); Brito (2016: 141).
    def test_a_palatal_coda_s_is_the_alveolar(self):
        assert benchmark.score_word("ˈsestɐ", ["ˈseʃtɐ"], word="cesta", brazilian=True) == (0, 5)
        assert benchmark.score_word("ˈmezmu", ["ˈmeʒmu"], word="mesmo", brazilian=True) == (0, 5)
        assert benchmark.score_word("ˈdɔjs", ["ˈdɔjʃ"], word="dois", brazilian=True) == (0, 4)

    def test_an_onset_palatal_and_an_affricate_stay(self):
        assert benchmark.score_word("ˈsa", ["ˈʃa"], word="chá", brazilian=True) == (1, 2)
        assert benchmark.score_word("ˈtʃi", ["ˈt͡ʃi"], word="ti", brazilian=True) == (0, 2)

    def test_european_rows_keep_the_palatal_coda(self):
        assert benchmark.score_word("ˈsestɐ", ["ˈseʃtɐ"], word="cesta") == (1, 5)


class TestAcceptedLedger:
    def test_a_skipped_process_counts_its_edit_again(self):
        assert benchmark.score_word("kõˈpɾa", ["kõˈpɾaɾ"], word="comprar", brazilian=True) == (0, 5)
        assert benchmark.score_word("kõˈpɾa", ["kõˈpɾaɾ"], word="comprar", brazilian=True,
                                    skip=frozenset({"final_r"})) == (1, 6)

    def test_every_named_process_is_a_step(self):
        source = open(benchmark.__file__, encoding="utf-8").read()
        for name, _, _ in benchmark.ACCEPTED_PROCESSES:
            assert f'"{name}" not in skip' in source

    def test_the_ledger_has_each_process_of_the_lect(self):
        rows = {r["dialect"]: r for r in json.load(open(os.path.join(os.path.dirname(__file__), "..", "benchmarks", "results.json"), encoding="utf-8"))}
        assert set(rows["pt-PT"]["accepted_edits"]) == {"glide", "strong_r", "initial_es"}
        assert rows["pt-BR"]["accepted_edits"]["final_r"] == 38


class TestBrazilianAccepted:
    def score(self, hyp, gold, word):
        return benchmark.score_word(hyp, [gold], word=word, brazilian=True)

    def test_the_coda_rhotic_is_one_segment(self):
        # Barbosa & Albano (2004: 228): /R/ is extremely variable in BP.
        assert self.score("adawˈbeɾtu", "adawˈbeʁtu", "Adalberto") == (0, 9)
        assert self.score("vawdeˈmaɾ", "vawdeˈmaʁ", "Valdemar") == (0, 7)

    def test_an_onset_rhotic_stays_an_edit(self):
        assert self.score("ˈɾatu", "ˈʁatu", "rato") == (1, 4)

    def test_epenthesis_in_a_written_cluster_is_one_reading(self):
        # Collischonn (2004: 64, 67): presence or absence of the vowel varies.
        assert self.score("ˈkakitu", "ˈkaktu", "cacto") == (0, 5)
        assert self.score("ad͡ʒivoˈɡadu", "advoˈɡadu", "advogado") == (0, 8)

    def test_a_written_vowel_stays_an_edit(self):
        assert self.score("ɡnɛ", "ɡiˈnɛ", "Guiné") == (1, 4)
        assert self.score("ˈbde", "biˈde", "bidê") == (1, 4)

    def test_the_glide_of_a_final_stressed_vowel_before_s_is_one_reading(self):
        # Leiria (Organon 28: 133): the diphthongization is variable.
        assert self.score("eskoˈses", "eskoˈsejs", "escocês") == (0, 7)
        assert self.score("ˈtɾes", "ˈtɾejs", "três") == (0, 4)

    def test_a_written_i_before_the_final_s_stays_an_edit(self):
        assert self.score("ˈʁas", "ʁaˈjs", "raiz") == (1, 4)
        assert self.score("ˈlapis", "ˈlapijs", "lápis") == (1, 6)

    def test_an_onset_rhotic_before_a_glide_or_schwa_stays_an_edit(self):
        # Barbosa & Albano (2004: 228) cover coda /R/ only.
        assert self.score("siˈɡaɾə", "siˈɡaʁə", "cigarra") == (1, 6)
        assert self.score("deɾˈwi", "deʁˈwi", "derruir") == (1, 5)

    def test_an_unstressed_final_s_keeps_its_glide_an_edit(self):
        # Leiria (Organon 28: 133-134) studies stressed final syllables only.
        assert self.score("ˈpɛɾes", "ˈpɛɾejs", "Pérez") == (1, 6)
        assert self.score("nus", "nujs", "nos") == (1, 4)

    def test_strict_phone_per_keeps_each_process_an_edit(self):
        assert benchmark.score_word("ˈkakitu", ["ˈkaktu"], word="cacto") == (1, 5)
        assert benchmark.score_word("eskoˈses", ["eskoˈsejs"]) == (1, 8)


class TestInfopediaTap:
    # Infopédia contrasts caro ˈkaru with carro ˈkaʀu: its ⟨r⟩ is the tap.
    def test_the_infopedia_r_is_the_tap(self):
        assert benchmark.score_word("ˈkaɾu", ["ˈkaru"]) == (0, 4)

    def test_the_strong_r_stays_apart_in_phone_per(self):
        assert benchmark.score_word("ˈkaʁu", ["ˈkaʀu"]) == (1, 4)

    def test_other_regions_keep_r_as_the_trill(self):
        assert benchmark.score_word("ɐɾɛmɐˈtaɾ", ["ɐrɛmɐˈtaɾ"], benchmark._OTHER) == (1, 8)


class TestSourceNotation:
    def test_folds_follow_the_source_of_the_row(self):
        assert benchmark.source_notation("infopedia", "pt-PT") == benchmark._INFOPEDIA
        assert benchmark.source_notation("wiktionary", "pt-PT") == ()
        assert benchmark.source_notation("wiktionary", "pt-BR") == (
            ("ɪ", "i"), ("ʊ", "u"), ("\u0303w\u0303", "\u0303w"), ("\u0303j\u0303", "\u0303j"))
        assert benchmark.source_notation("none", "pt-PT-x-lisboa") == ()

    def test_a_row_of_several_sources_takes_all_their_folds(self):
        assert benchmark.source_notation("wiktionary+infopedia", "pt-PT") == benchmark._INFOPEDIA

    def test_a_wiktionary_lax_vowel_scores_as_the_tense_vowel(self):
        assert benchmark._score_rows("ˈpatu", [("ˈpatʊ", "wiktionary")], "pt-BR")[:2] == (0, 4)
        assert benchmark._score_rows("ˈpatu", [("ˈpatʊ", "none")], "pt-BR")[:2] == (1, 4)

    def test_sources_merge_in_a_fixed_order(self):
        assert benchmark.merge_sources(["michaelis", "none", "wiktionary"]) == "wiktionary+michaelis"
        assert benchmark.merge_sources(["none"]) == "none"

    def test_the_pt_br_fixture_rows_all_have_a_source(self):
        rows = [r for v in benchmark.load_fixture_rows("pt-BR").values() for r in v]
        assert {sources for _, sources in rows} == {"wiktionary", "wiktionary+michaelis"}

    @pytest.mark.parametrize("dialect", sorted(benchmark.DIALECT_TO_REGION))
    def test_every_fixture_row_names_its_sources(self, dialect):
        rows = [r for v in benchmark.load_fixture_rows(dialect).values() for r in v]
        assert rows and all(sources for _, sources in rows)


class TestBrazilianAcceptedScope:
    """Each accepted step covers what its source covers (#459)."""

    def score(self, hyp, gold, word):
        return benchmark.score_word(hyp, [gold], word=word, brazilian=True)

    def test_a_retroflex_coda_rhotic_is_one_segment(self):
        assert self.score("noˈtuɾnɐ", "noˈtuɽnɐ", "noturna") == (0, 7)

    def test_a_nasal_or_lax_epenthetic_vowel_drops(self):
        assert self.score("adˈmitu", "adĩˈmitu", "admito") == (0, 6)
        assert self.score("kɐɾɐkˈtɛɾis", "kɐɾɐkɪˈtɛɾis", "caracteres") == (0, 10)

    def test_the_labial_nasal_triggers_epenthesis(self):
        # Collischonn (2004: 66): "e a nasal labial", amnésia.
        assert self.score("amˈnɛzjɐ", "amiˈnɛzjɐ", "amnésia") == (0, 7)

    def test_a_lax_final_glide_before_s_drops(self):
        assert self.score("ˈves", "ˈveɪs", "vez") == (0, 3)

    def test_a_stressed_high_vowel_is_not_a_glide(self):
        assert self.score("ˈtʃjɐ", "ˈtʃiɐ", "tia") == (1, 3)


class TestReferenceKind:

    def test_portal_rows_are_labelled_machine_reference(self):
        # Every fixture row of these regions has the source "none": a Portal
        # da Língua Portuguesa row, generated by its rule-based LUPo system.
        portal = {d for d in benchmark.DIALECT_TO_REGION
                  if {line.rstrip("\n").split("\t")[2]
                      for line in open(benchmark.fixture_path(d), encoding="utf-8")
                      if not line.startswith("#")} == {"none"}}
        assert portal == {"pt-AO", "pt-MZ", "pt-BR-x-rio-janeiro",
                          "pt-BR-x-sao-paulo", "pt-PT-x-lisbon", "pt-TL"}
        kinds = {d: benchmark.REFERENCE_KIND[d] for d in benchmark.DIALECT_TO_REGION}
        assert {d for d, k in kinds.items() if k == "portal_lupo"} == portal
        assert {d for d, k in kinds.items() if k == "human"} == {"pt-PT", "pt-BR"}

    def test_results_json_records_reference_kind(self):
        rows = json.load(open(benchmark.RESULTS_JSON, encoding="utf-8"))
        assert {r["dialect"]: r["reference_kind"] for r in rows} == benchmark.REFERENCE_KIND


def test_a_written_vowel_left_of_the_cluster_stays():
    # #459: a written C + ⟨i⟩ + C before the cluster is a lexical vowel.
    def score(hyp, gold):
        return benchmark.score_word(hyp, [gold], word="pitapto", brazilian=True)
    assert score("pitaptu", "pitaptu") == (0, 7)
    assert score("pitaptu", "pitapitu") == (0, 7)
    assert score("ptaptu", "pitaptu") == (1, 7)


def test_the_scoreboard_page_matches_the_committed_results():
    with open(benchmark.RESULTS_JSON, encoding="utf-8") as fh:
        rows = json.load(fh)
    with open(benchmark.SCOREBOARD_MD, encoding="utf-8") as fh:
        assert benchmark.render_scoreboard(rows) == fh.read()
