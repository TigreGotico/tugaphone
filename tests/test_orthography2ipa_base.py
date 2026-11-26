"""Tests for the orthography2ipa integration.

Validates:
- stress placement follows the pt spec's declarative StressRules
  (correcting the overbroad bare -m/-n oxytone triggers)
- the engine uses orthography2ipa's bundled splitter
"""
import re
import unicodedata

import pytest
from silabificador import syllabify

import orthography2ipa

from tugaphone import phonemize

# A syllable nucleus: a run of vowel symbols. The glides [j w] are not nuclei.
NUCLEUS = re.compile("[aɐeɛəɨioɔuʊɪ]̃?(?:[aɐeɛəɨioɔuʊɪ]̃?)*")


def stressed_index(word, lect="pt-PT"):
    """The 0-based syllable that carries ``ˈ``, counted in silabificador's split.

    The syllables from the mark to the end of the word are its nuclei.
    """
    after = unicodedata.normalize("NFD", phonemize(word, lect)).partition("ˈ")[2]
    return len(syllabify(word)) - len(NUCLEUS.findall(after))


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
    def test_gold_positions(self, word, expected):
        assert stressed_index(word) == expected, phonemize(word, "pt-PT")

    def test_spec_rules_present(self):
        assert orthography2ipa.get("pt-PT").stress is not None


class TestSyllabification:
    @pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
    def test_the_engine_uses_the_bundled_splitter(self, lect):
        # The word is stressed on ⟨do⟩. With silabificador's split the stress
        # lands on the final syllable.
        assert phonemize("distribuidoras", lect).partition("ˈ")[2].startswith("d")
