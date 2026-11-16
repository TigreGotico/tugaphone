"""Hiatus before the diminutive suffixes: *Vinha* reads *V.inha*.

A vowel that meets the ``-inh-`` of a diminutive, or of a word
lexicalised from one, does not diphthongise. *rainha* is ``ra.i.nha``
with the ``i`` as a nucleus of its own, not ``rai.nha`` with a falling
``[aj]``. The break decides two things at once: the suffix vowel
becomes the penult and takes the stress, and the vowel before it stays
atonic and reduces.

The ``u`` of ``qu``/``gu`` is a graphic filler rather than a nucleus,
so *mesquinho* and *amiguinho* keep ``qui``/``gui`` whole, and a
consonant before the suffix leaves nothing to break, so *cozinha* and
*farinha* are untouched.

Syllabification already places the suffix vowel correctly for every
word below. These cases are the guard on that: they run the real
pipeline and lock the outcome so a syllabifier change cannot silently
turn the hiatus back into a diphthong.
"""
import pytest

from tugaphone.tokenizer import Sentence
from tugaphone.registry import get_dialect_inventory


def _rules_only(dialect_code="pt-PT"):
    inv = get_dialect_inventory(dialect_code)
    object.__setattr__(inv, "IRREGULAR_WORDS", {})
    return inv


@pytest.fixture(scope="module")
def pt():
    return _rules_only()


def ipa(word, inv):
    return Sentence(word, dialect=inv).ipa.strip()


# Vowel + -inh-: the suffix vowel is a syllable of its own and carries
# the stress.
HIATUS_WORDS = [
    "rainha", "rainhas", "moinho", "moinhos", "campainha", "bainha",
    "bainhas", "ladainha", "tainha", "sainha", "remoinho", "embainhar",
    "amoinhar", "arruinhar", "cainho", "azoinha",
]

# Controls: -inha/-inho after a consonant, and true diphthongs that
# must survive untouched.
DIPHTHONG_CONTROLS = [
    "cozinha", "vizinha", "sozinho", "farinha", "galinha", "andorinha",
    "raia", "moita", "boina", "baixinho", "pauzinho", "coisinha",
    "mesquinho", "amiguinho", "saquinho", "rosquinha",
]


@pytest.mark.parametrize("word", HIATUS_WORDS)
def test_suffix_vowel_is_its_own_syllable(word, pt):
    sent = Sentence(word, dialect=pt)
    syllables = sent.words[0].syllables
    assert "i" in syllables, (
        f"{word}: expected a bare 'i' syllable (hiatus), got {syllables}")


@pytest.mark.parametrize("word", DIPHTHONG_CONTROLS)
def test_controls_keep_their_syllabification(word, pt):
    sent = Sentence(word, dialect=pt)
    syllables = sent.words[0].syllables
    assert "i" not in syllables, (
        f"{word}: must not gain a hiatus break, got {syllables}")


@pytest.mark.parametrize("word,expected", [
    ("rainha", "ʁɐ·ˈi·ɲɐ"),
    ("moinho", "mu·ˈi·ɲu"),
    ("campainha", "kɐ̃·pɐ·ˈi·ɲɐ"),
    ("bainha", "bɐ·ˈi·ɲɐ"),
    ("ladainha", "lɐ·dɐ·ˈi·ɲɐ"),
    ("tainha", "tɐ·ˈi·ɲɐ"),
    ("cozinha", "ku·ˈzi·ɲɐ"),
    ("vizinha", "vi·ˈzi·ɲɐ"),
    ("sozinho", "su·ˈzi·ɲu"),
    ("farinha", "fɐ·ˈɾi·ɲɐ"),
    ("raia", "ˈʁɐj·ɐ"),
    ("moita", "ˈmoj·tɐ"),
])
def test_european_portuguese_ipa(word, expected, pt):
    assert ipa(word, pt) == expected


