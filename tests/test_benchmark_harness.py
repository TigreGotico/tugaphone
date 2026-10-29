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

    def test_lexicon_is_bypassed(self):
        inv = benchmark._rules_only_inventory("pt-PT")
        assert inv.IRREGULAR_WORDS == {}

    def test_rules_only_still_transcribes(self):
        assert benchmark.rules_only_ipa("casa", "pt-PT")

    def test_normal_inventory_untouched(self):
        # the harness must not leak its emptied lexicon into normal use
        from tugaphone.registry import get_dialect_inventory
        benchmark._rules_only_inventory("pt-BR")
        assert get_dialect_inventory("pt-BR").IRREGULAR_WORDS


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
