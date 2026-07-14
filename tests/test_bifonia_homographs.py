"""Meaning-based heterophone disambiguation via bifonia.

bifonia resolves which reading a heterophonic homograph carries and marks it with
the open/closed-vowel diacritic the phonemizer reads, so the same spelling maps to
the correct vowel from context — something a part-of-speech table cannot do when
both readings share a part of speech (sede thirst/seat are both nouns).
"""
import pytest

from tugaphone import TugaPhonemizer


@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


def _clean(ipa: str) -> str:
    return ipa.replace("·", "").replace("ˈ", "")


def test_sede_thirst_is_closed_seat_is_open(ph):
    thirst = _clean(ph.phonemize_sentence("Tinha tanta sede que bebi água."))
    seat = _clean(ph.phonemize_sentence("A sede da empresa fica em Lisboa."))
    assert "sedɨ" in thirst      # closed e — thirst
    assert "sɛdɨ" in seat        # open ɛ — seat (headquarters)


def test_forma_mould_is_closed_shape_is_open(ph):
    mould = _clean(ph.phonemize_sentence("Untou a forma com manteiga."))
    shape = _clean(ph.phonemize_sentence("Resolveu o problema desta forma."))
    assert "fo" in mould         # closed o — mould (fôrma)
    assert "fɔ" in shape         # open ɔ — shape


def test_acordo_noun_is_closed_verb_is_open(ph):
    noun = _clean(ph.phonemize_sentence("O acordo de paz foi assinado."))
    verb = _clean(ph.phonemize_sentence("Eu acordo cedo todos os dias."))
    assert "koɾ" in noun         # closed o — agreement (noun)
    assert "kɔɾ" in verb         # open ɔ — I wake (verb)


def test_gosto_noun_is_closed_verb_is_open(ph):
    verb = _clean(ph.phonemize_sentence("Gosto muito de ti."))
    noun = _clean(ph.phonemize_sentence("O gosto é amargo."))
    assert "ɡɔʃ" in verb         # open ɔ — I like (verb)
    assert "ɡoʃ" in noun         # closed o — taste (noun)
