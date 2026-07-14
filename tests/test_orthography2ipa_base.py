"""Tests for the orthography2ipa integration.

Validates:
- stress detection delegates to the pt spec's declarative StressRules
  (correcting the overbroad bare -m/-n oxytone triggers)
- SilabificadorSyllabifier registers in the orthography2ipa.syllabify
  group and feeds orthography2ipa's own stress detection
- TugaphoneG2PPlugin implements the shared engine interface lazily
- differential audit: hand-tuned CHAR2IPA values appear among the
  pt spec's grapheme candidates
"""
import pytest
from silabificador import syllabify

import orthography2ipa
from orthography2ipa.syllabifier_plugin import SyllabifierPlugin

from tugaphone.dialects import EuropeanPortuguese
from tugaphone.plugin import SilabificadorSyllabifier, TugaphoneG2PPlugin
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


class TestSyllabifierPlugin:
    def test_implements_base(self):
        assert isinstance(SilabificadorSyllabifier(), SyllabifierPlugin)

    def test_registered_via_entry_point(self):
        import orthography2ipa.registry as registry
        registry._syllabifiers = None  # force re-discovery
        plugin = orthography2ipa.get_syllabifier("pt-PT")
        assert plugin is not None
        assert type(plugin).__name__ == "SilabificadorSyllabifier"

    def test_syllables_rebuild_word(self):
        plugin = SilabificadorSyllabifier()
        for word in ("viagem", "lâmpada", "abacaxi", "sol"):
            sylls = plugin.syllabify(word, "pt-PT")
            assert "".join(sylls) == word

    def test_orthography2ipa_stress_uses_it(self):
        """orthography2ipa's own detection gets real pt syllables."""
        from orthography2ipa.stress import detect_stress

        rules = orthography2ipa.get("pt-PT").stress
        # naive splitter sees vi-a as one nucleus; silabificador fixes it
        assert detect_stress("viagem", rules, lang="pt-PT") == 1


class TestG2PEngineSurface:
    def test_implements_base_lazily(self):
        plugin = TugaphoneG2PPlugin()
        # tugaphone is an engine BUILT ON orthography2ipa, not a plugin TO it —
        # nothing over there discovers or calls this. What matters is the surface,
        # not the inheritance.
        for method in ("transcribe", "transcribe_word"):
            assert callable(getattr(plugin, method))
        assert plugin._phonemizer is None  # nothing heavy loaded yet
        assert set(plugin.language_codes) >= {"pt-PT", "pt-BR"}


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
