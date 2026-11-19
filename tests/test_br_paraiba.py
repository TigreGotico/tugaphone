"""Paraibano Portuguese, ``pt-BR-x-paraiba``.

Each reading is written by hand from the source orthography2ipa cites for the
lect, not captured from the phonemizer. Hora, Henrique & Amorim (2018) describe
João Pessoa: /t d/ stay stops before [i] (p. 280), and coda /S/ is alveolar,
as in "ca[s]ca" and "doi[s]", except for [ʃ ʒ] before [t d] (p. 283). João
Pessoa listeners hear "me[ʒ]mo" as the speech of another place (p. 284).
"""
import warnings

import pytest

from tugaphone import TugaPhonemizer
from tugaphone.registry import is_supported, list_dialects, resolve_lect


@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


@pytest.mark.parametrize("code", ["pt-BR-x-paraiba", "pt-BR-x-pb", "PT-br-X-PARAIBA"])
def test_the_lect_resolves_without_a_fallback(code):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert resolve_lect(code) == "pt-BR-x-paraiba"
    assert is_supported(code)


def test_the_lect_is_listed():
    assert "pt-BR-x-paraiba" in list_dialects()


@pytest.mark.parametrize("word,ipa", [
    ("tia", "ˈtiɐ"),
    ("noite", "ˈnojti"),
    ("casca", "ˈkaskɐ"),
    ("dois", "ˈdojs"),
    ("mesmo", "ˈmezmu"),
    ("texto", "ˈteʃtu"),
])
def test_paraiba_reading(ph, word, ipa):
    assert ph.phonemize_sentence(word, "pt-BR-x-paraiba") == ipa


def test_desde_has_a_palatal_coda_before_the_stop(ph):
    # p. 283 gives [ʒ] before [d]. After that [ʒ] the /d/ before [i] is an
    # affricate 56.4% of the time (Gráfico 6, p. 293), so only the coda is pinned.
    assert ph.phonemize_sentence("desde", "pt-BR-x-paraiba").startswith("ˈdeʒd")
