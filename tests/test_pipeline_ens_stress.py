"""An unaccented -ens is paroxytone; -ins, -ons and -uns are oxytone.

An oxytone of more than one syllable in -em or -ens takes an acute
(Acordo Ortográfico 1990, Base VIII, 1.º c: "acém, detém, deténs, ...,
também"), so an unaccented -ens is paroxytone: *homens*, *jovens*. The
pipeline reads these through orthography2ipa. The rows check only where the
primary mark falls: on the first syllable of a two-syllable paroxytone, not on
the first syllable of an oxytone.
"""
import pytest

from tugaphone import TugaPhonemizer

PAROXYTONE = ["homens", "jovens", "nuvens", "ordens"]
OXYTONE = ["jardins", "bombons", "atuns", "armazéns"]


@pytest.fixture(scope="module")
def phonemizer():
    return TugaPhonemizer()


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("word", PAROXYTONE)
def test_unaccented_ens_is_paroxytone(word, lang, phonemizer):
    ipa = phonemizer.phonemize_sentence(word, lang)
    assert ipa.count("ˈ") == 1 and ipa.startswith("ˈ"), ipa


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("word", OXYTONE)
def test_ins_ons_uns_and_accented_ens_are_oxytone(word, lang, phonemizer):
    ipa = phonemizer.phonemize_sentence(word, lang)
    assert ipa.count("ˈ") == 1 and not ipa.startswith("ˈ"), ipa
