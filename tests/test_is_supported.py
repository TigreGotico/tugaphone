"""``is_supported`` answers whether a tag names a tugaphone lect.

A supported tag is one that :func:`resolve_lect` answers with no fallback
warning: a canonical lect, or an alias of one. A tag that only the fallback
answers (another language, a lect in another orthography, an unknown
sub-tag) is not supported.
"""
import warnings

import pytest

from tugaphone import TugaPhonemizer, is_supported, list_dialects
from tugaphone.registry import resolve_lect

SUPPORTED = [
    "pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL", "pt-PT-x-porto", "pt-BR-x-sp",
]
ALIASES = [
    "pt", "PT-pt", "pt_BR", "pt-br-X-SP",
    "pt-PT-x-azores", "pt-PT-x-lisboa", "pt-BR-x-sao-paulo", "pt-BR-x-rio",
    "pt-PT-x-trasosmontes",
]
UNSUPPORTED = [
    "en-US", "es-ES", "en", "gl-ES", "xx-YY", "",
    # Barranquenho and medieval Portuguese have their own orthography.
    "pt-x-barranquenho", "ext-PT-x-barranco", "pt-PT-x-medieval",
    # A sub-tag tugaphone does not know falls back to its parent lect.
    "pt-PT-x-unknown", "pt-BR-x-nowhere",
]


@pytest.mark.parametrize("lang", SUPPORTED + ALIASES)
def test_a_lect_or_its_alias_is_supported(lang):
    assert is_supported(lang) is True
    assert TugaPhonemizer.is_supported(lang) is True


@pytest.mark.parametrize("lang", UNSUPPORTED)
def test_a_tag_only_the_fallback_answers_is_not_supported(lang):
    assert is_supported(lang) is False
    assert TugaPhonemizer.is_supported(lang) is False


def test_every_listed_dialect_is_supported():
    dialects = list_dialects()
    assert {"pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"} <= set(dialects)
    assert [d for d in dialects if not is_supported(d)] == []


@pytest.mark.parametrize("lang", SUPPORTED + ALIASES + UNSUPPORTED)
def test_the_answer_matches_whether_resolution_falls_back(lang):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        resolve_lect(lang)
    fell_back = any("is not a tugaphone lect" in str(w.message) for w in caught)
    assert is_supported(lang) is not fell_back
