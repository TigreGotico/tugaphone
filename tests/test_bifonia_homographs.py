"""Meaning-based heterophone disambiguation via bifonia.

bifonia resolves which reading a heterophonic homograph carries and marks it with
the open/closed-vowel diacritic the phonemizer reads, so the same spelling maps to
the correct vowel from context — something a part-of-speech table cannot do when
both readings share a part of speech (sede thirst/seat are both nouns).
"""
import pytest

from tugaphone import TugaPhonemizer, list_dialects, phonemize


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


# Brazilian Portuguese has a closed stressed mid vowel in every sense of these
# words (Wiktionary, Brazil: soma /ˈsõ.mɐ/, aceno /aˈsẽ.nu/, abono /aˈbõ.nu/,
# domo /ˈdõ.mu/), where European Portuguese opens it in the verb (soma
# /ˈsɔ.mɐ/, aceno /ɐˈsɛ.nu/, abono /ɐˈbɔ.nu/, domo /ˈdɔ.mu/). Wiktionary has no
# entry for empeno or desempeno; they follow the other -enar verbs (condeno,
# Brazil /kõˈdẽ.nu/, Portugal /kõˈdɛ.nu/). bifonia carries these as pt-BR lect
# overrides, so they reach the engine only when the lect is passed through.
_BRAZILIAN_LECTS = [code for code in list_dialects() if code.startswith("pt-BR")]


@pytest.mark.parametrize("lect", _BRAZILIAN_LECTS)
@pytest.mark.parametrize("sentence, closed, open_", [
    ("Ele soma os números.", ("ˈsom", "ˈsõm"), "ˈsɔm"),
    ("Eu aceno da janela.", ("ˈsen", "ˈsẽn"), "ˈsɛn"),
    ("Eu abono a falta.", ("ˈbon", "ˈbõn"), "ˈbɔn"),
    ("Eu domo o cavalo.", ("ˈdom", "ˈdõm"), "ˈdɔm"),
    ("Eu empeno a madeira.", ("ˈpen", "ˈpẽn"), "ˈpɛn"),
    ("Eu desempeno a barra.", ("ˈpen", "ˈpẽn"), "ˈpɛn"),
])
def test_brazilian_lects_keep_the_stressed_vowel_closed(lect, sentence, closed, open_):
    ipa = phonemize(sentence, lect).replace("·", "")
    assert open_ not in ipa
    assert any(form in ipa for form in closed), ipa


@pytest.mark.parametrize("sentence, open_", [
    ("Ele soma os números.", "ˈsɔm"),
    ("Eu aceno da janela.", "ˈsɛn"),
    ("Eu abono a falta.", "ˈbɔn"),
    ("Eu domo o cavalo.", "ˈdɔm"),
    ("Eu empeno a madeira.", "ˈpɛn"),
    ("Eu desempeno a barra.", "ˈpɛn"),
])
def test_european_verb_reading_stays_open(sentence, open_):
    assert open_ in phonemize(sentence, "pt-PT").replace("·", "")
