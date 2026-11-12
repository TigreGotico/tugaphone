"""Tests for the orthography2ipa integration.

Validates:
- stress detection delegates to the pt spec's declarative StressRules
  (correcting the overbroad bare -m/-n oxytone triggers)
- the engine uses orthography2ipa's bundled splitter
- differential audit: hand-tuned CHAR2IPA values appear among the
  pt spec's grapheme candidates
"""
import pytest
from silabificador import syllabify

import orthography2ipa

from tugaphone import phonemize
from tugaphone.dialects import EuropeanPortuguese
from tugaphone.tokenizer import detect_stress_position


@pytest.fixture(scope="module")
def dialect():
    return EuropeanPortuguese()


class TestStressDelegation:
    @pytest.mark.parametrize("word,expected", [
        # paroxytone default — including the unmarked -em/-am endings
        # the old bare -m oxytone trigger got wrong
        ("casa", 0), ("livro", 0), ("homem", 0), ("falam", 0),
        ("viagem", 1),                 # vi-A-gem with real syllables
        # oxytone endings
        ("falar", 1), ("azul", 1), ("rapaz", 1), ("jardim", 1),
        ("caju", 1), ("abacaxi", 3), ("atuns", 1),
        # written accents win — circumflex included
        ("médico", 0), ("lâmpada", 0), ("café", 1), ("túnel", 0),
        ("órgão", 0), ("manhã", 1), ("amável", 1),
        # monosyllables
        ("sol", 0), ("pé", 0),
    ])
    def test_gold_positions(self, dialect, word, expected):
        sylls = syllabify(word)
        assert detect_stress_position(word, sylls, dialect) == expected

    def test_spec_rules_present(self, dialect):
        assert orthography2ipa.get(dialect.dialect_code).stress is not None


class TestSyllabification:
    @pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
    def test_the_engine_uses_the_bundled_splitter(self, lect):
        # The word is stressed on ⟨do⟩. With silabificador's split the stress
        # lands on the final syllable.
        assert phonemize("distribuidoras", lect).partition("ˈ")[2].startswith("d")


class TestSpecParity:
    """Audit hand-tuned single-char mappings against the pt spec data.

    Informational gate: tugaphone's tables stay authoritative; this
    pins the agreement level so spec-data drift is noticed.
    """

    def test_char2ipa_within_spec_candidates(self, dialect):
        spec = orthography2ipa.get(dialect.dialect_code)
        agree, differ = [], []
        for char, ipa in dialect.DEFAULT_CHAR2PHONEMES.items():
            candidates = spec.graphemes.get(char)
            if candidates is None or not ipa:
                continue
            (agree if ipa in candidates else differ).append(
                (char, ipa, candidates))
        assert len(agree) >= 2 * len(differ), (
            f"tugaphone and the pt spec diverged: {differ}"
        )
