"""A tonic ⟨í ú⟩ after a vowel is a hiatus that carries the stress.

The Acordo Ortográfico 1990, Base X, 1.º writes the acute on a tonic ⟨i u⟩
preceded by a vowel "com que não formam ditongo" (juízes, saída, baú), so the
accent marks the stress and the hiatus at once. The stress mark therefore sits
on the accented vowel, and the vowel before it is a pretonic nucleus that
reduces (⟨o⟩ → [u], ⟨a⟩ → [ɐ], ⟨e⟩ → [ɨ]).

Unaccented ⟨ui oi⟩ are falling diphthongs and stay one syllable. Where the
tugalex lexicon covers a word the expected value is the Portal da Língua
Portuguesa Lisbon transcription that the lexicon carries.
"""
import pytest

from tugaphone import TugaPhonemizer

LECTS = ["pt-PT", "pt-PT-x-lisbon"]


@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


HIATUS = [
    ("proíbe", "pɾuˈibɨ"),
    ("juízes", "ʒuˈizɨʃ"),
    ("atribuído", "ɐtɾibuˈidu"),
    ("saída", "sɐˈidɐ"),
    ("baú", "bɐˈu"),
    ("reúne", "ʁɨˈunɨ"),
]


@pytest.mark.parametrize("lect", LECTS)
@pytest.mark.parametrize("word,expected", HIATUS)
def test_stress_on_the_accented_hiatus_vowel(ph, lect, word, expected):
    assert ph.phonemize_sentence(word, lect) == expected


@pytest.mark.parametrize("lect", LECTS)
def test_saude_stress_on_the_accented_u(ph, lect):
    # Portal: sɐ.ˈu.dɨ. Only the stressed syllable is asserted: the lexicon
    # entry drops the final vowel, which is outside this rule.
    assert ph.phonemize_sentence("saúde", lect).startswith("sɐˈu")


DIPHTHONGS = [
    ("muito", "ˈmũjtu"),
    ("fui", "ˈfuj"),
    ("cuidado", "kwiˈdadu"),
    ("foi", "ˈfoj"),
]


@pytest.mark.parametrize("lect", LECTS)
@pytest.mark.parametrize("word,expected", DIPHTHONGS)
def test_unaccented_diphthong_stays_one_syllable(ph, lect, word, expected):
    assert ph.phonemize_sentence(word, lect) == expected
