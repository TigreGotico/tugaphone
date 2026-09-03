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
