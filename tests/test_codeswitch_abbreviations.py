"""Abbreviations stay on the Portuguese path under code-switching.

The normalizer expands an abbreviation and reads a Roman numeral after a
part-of-work noun from its neighbours. After its noun, a numeral up to ten is
an ordinal and from eleven on a cardinal, for kings, popes, centuries and
chapters (Silveira Bueno, quoted by Migalhas "Gramatigalhas: Numeral";
Ciberdúvidas 14284), so "Cap. XII" is "capítulo doze". Code-switch routing
splits the text into words before the normalizer runs, so a routed
abbreviation reaches the contact lattice unexpanded and the numeral after it
loses its noun.
"""
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.codeswitch import split_runs
from tugaphone.text_normalization import normalize_orthography

SENTENCE = "Tenho 23 anos, Sr. Silva; li o Cap. XII."
# The sentence as a reader says it, written out by hand.
SPOKEN = "Tenho vinte e três anos, Senhor Silva; li o capítulo doze."

ABBREVIATIONS = [
    "Cap.", "cap.", "Art.", "art.", "Pág.", "pág.", "Av.", "R.", "Dr.",
    "Eng.", "Srs.", "Exmo.", "Ex.mo", "vs.", "D.", "S.",
]


@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("contact", ["none", "en", "auto"])
def test_chapter_numeral_reads_as_spoken(ph, lect, contact):
    expected = ph.phonemize_sentence(SPOKEN, lect, contact="none")
    assert ph.phonemize_sentence(SENTENCE, lect, contact=contact) == expected


@pytest.mark.parametrize("contact", ["en", "auto"])
@pytest.mark.parametrize("token", ABBREVIATIONS)
def test_abbreviation_stays_portuguese(classifier, contact, token):
    assert split_runs(f"{token},", contact) == [(None, f"{token},")]


@pytest.mark.parametrize("text,expected", [
    ("li o Cap. XII.", "li o Capítulo Doze."),
    ("Cap. 3 descreve", "Capítulo 3 descreve"),
    ("Art. 5 da lei", "Artigo 5 da lei"),
    ("Fig. 2 mostra", "Figura 2 mostra"),
    ("Séc. XIX", "Século Dezanove"),
    ("o N.º 4", "o número 4"),
])
def test_capitalised_abbreviation_expands(text, expected):
    assert normalize_orthography(text) == expected
