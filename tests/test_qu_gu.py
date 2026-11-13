"""The u of ⟨qu⟩ and ⟨gu⟩: silent before e/i, a glide [w] before a/o.

Before ⟨e i⟩ the u is silent in most words (*quero*, *guerra*,
*riquíssimo*), and the written accent on the vowel does not change
that. A closed set of words pronounces it as [w]; since the trema was
dropped nothing in the spelling marks them (Acordo Ortográfico 1990,
Base XIV, 1.º: "aguentar, anguiforme, arguir, bilíngue (ou bilingue),
lingueta, linguista, linguístico; cinquenta, equestre, frequentar,
tranquilo, ubiquidade"). Before ⟨a o⟩ the u is always the glide [w]
(*quando*, *guarda*), never a vowel of its own.

Each expected transcription below is the Infopédia form in the unified
gold (``TigreGotico/portuguese-unified-pronunciation-lexicon``).
"""
import os
import sys

import pytest

from tugaphone.registry import get_dialect_inventory
from tugaphone.tokenizer import Sentence, is_grapheme_silent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from benchmark import normalize, stress_hit  # noqa: E402


@pytest.fixture(scope="module")
def pt():
    inv = get_dialect_inventory("pt-PT")
    object.__setattr__(inv, "IRREGULAR_WORDS", {})
    return inv


def ipa(word, inv):
    return Sentence(word, dialect=inv).ipa.strip()


# word, Infopédia transcription, the consonant + u reading it requires
ROWS = [
    ("antiguidade", "ɐ̃tiɡwiˈdad", "ɡw"),
    ("linguiça", "lĩˈɡwisɐ", "ɡw"),
    ("pinguim", "pĩˈɡwĩ", "ɡw"),
    ("aguentar", "ɐɡwẽˈtar", "ɡw"),
    ("tranquilo", "trɐ̃ˈkwilu", "kw"),
    ("cinquenta", "sĩˈkwẽtɐ", "kw"),
    ("quando", "ˈkwɐ̃du", "kw"),
    ("guarda", "ˈɡwardɐ", "ɡw"),
    ("quase", "ˈkwazɨ", "kw"),
    ("quero", "ˈkɛɾu", "k"),
    ("guerra", "ˈɡɛʀɐ", "ɡ"),
    ("riquíssimo", "ʁiˈkisimu", "k"),
]


@pytest.mark.parametrize("word,gold,onset", ROWS)
def test_u_after_q_g(word, gold, onset, pt):
    out = normalize(ipa(word, pt))
    at = out.index(onset[0])
    if onset.endswith("w"):
        assert out[at:at + 2] == onset, out
    else:
        assert out[at + 1] not in "uw", out


@pytest.mark.parametrize("word,gold,onset", ROWS)
def test_stress_on_the_gold_syllable(word, gold, onset, pt):
    """A u read as a vowel adds a nucleus, and the mark lands on it."""
    out = ipa(word, pt)
    assert stress_hit(out, gold), out


@pytest.mark.parametrize("before,after,word,silent", [
    ("q", "ero", "quero", True),
    ("riq", "íssimo", "riquíssimo", True),
    ("aq", "ecer", "aquecer", True),
    ("g", "erra", "guerra", True),
    ("antig", "idade", "antiguidade", False),
    ("ling", "iça", "linguiça", False),
    ("ping", "im", "pinguim", False),
    ("ag", "entar", "aguentar", False),
    ("q", "ando", "quando", False),
    ("g", "arda", "guarda", False),
])
def test_is_grapheme_silent(before, after, word, silent, pt):
    assert is_grapheme_silent("u", before, after, word, pt) is silent
