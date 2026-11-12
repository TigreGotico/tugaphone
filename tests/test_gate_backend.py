"""The sentence-gate backend switches each tugaphone stage off on its own.

The expected words are Infopédia's readings, as the pt-PT sentence set cites
them, so no expected value is read back from tugaphone.
"""
import pytest

from tests.gate_backend import STAGES, TugaphoneBackend
from tugaphone import phonemize

# Infopédia: "para" the verb is [ˈpaɾɐ], the preposition [ˈpɐɾɐ] (bifonia's
# sense table); "três" is [ˈtɾeʃ], which tugaphone keeps at the end of a sentence;
# "comboio" is [kõˈbɔju].
STOPS = "O carro para aqui."
DIGIT = "Aqui é a porta 3."
LEXICAL = "O comboio é rápido."


def ipa(backend, text, lang="pt-PT"):
    return backend.phonemize(text, lang)[0][0].split()


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("text", [STOPS, DIGIT, LEXICAL, "O Sr. Costa foi ao museu.",
                                  "Foi a 25 de abril de 1974."])
def test_the_full_backend_is_the_shipped_path(text, lang):
    assert TugaphoneBackend().phonemize(text, lang) == [[phonemize(text, lang)]]


def test_mark_off_reads_para_as_the_preposition():
    full = TugaphoneBackend()
    assert "ˈpaɾɐ" in ipa(full, STOPS)
    assert "ˈpɐɾɐ" in ipa(full.without("mark"), STOPS)
    assert "ˈpaɾɐ" not in ipa(full.without("mark"), STOPS)


def test_expand_off_drops_the_digit():
    full = TugaphoneBackend()
    assert "ˈtɾeʃ" in ipa(full, DIGIT)
    assert "ˈtɾeʃ" not in ipa(full.without("expand"), DIGIT)


def test_lexicon_off_loses_the_lexicon_vowel():
    full = TugaphoneBackend()
    assert "kõˈbɔju" in ipa(full, LEXICAL)
    assert "kõˈbɔju" not in ipa(full.without("lexicon"), LEXICAL)


@pytest.mark.parametrize("stage,text", [("mark", DIGIT), ("mark", LEXICAL),
                                        ("expand", STOPS), ("expand", LEXICAL),
                                        ("lexicon", STOPS), ("lexicon", DIGIT)])
def test_a_stage_off_leaves_what_it_does_not_own(stage, text):
    full = TugaphoneBackend()
    assert ipa(full.without(stage), text) == ipa(full, text)


def test_without_returns_a_new_backend():
    full = TugaphoneBackend()
    off = full.without("mark").without("expand")
    assert off.disabled == {"mark", "expand"}
    assert full.disabled == frozenset()
    assert "ˈpaɾɐ" in ipa(full, STOPS)


def test_an_unknown_stage_raises():
    with pytest.raises(ValueError, match="no stage 'homographs'; its stages are lexicon, expand, mark"):
        TugaphoneBackend().without("homographs")


def test_the_stages_are_the_pipeline_fields_tugaphone_fills():
    from tugaphone import pipeline

    filled = {name for name in STAGES if getattr(pipeline("pt-PT"), name)}
    assert filled == set(STAGES)
