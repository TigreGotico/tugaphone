"""Tests for tugaphone.pipeline: the orthography2ipa Pipeline tugaphone runs.

Expected values come from the packaged lexicon, a plain G2P on hand-marked or
hand-spelled text, and tugaphone.phonemize, never from pipeline() itself.
"""
import pytest
from orthography2ipa import G2P, packaged_lexicon

import tugaphone

SENTENCES = [
    "O gato dorme no sofá.",
    "Tenho 3 gatos e 21 cadelas desde 1999.",
    "A sede do partido fica no Porto.",
    "O guarda-chuva ficou no pára-choques.",
    "Ele colhe a colher de sopa.",
    "Eu jogo o jogo.",
]


@pytest.mark.parametrize("lect", tugaphone.list_dialects())
def test_engine_on_pipeline_matches_phonemize(lect):
    engine = G2P(lect, pipeline=tugaphone.pipeline(lect))
    for sentence in SENTENCES:
        assert engine.transcribe(sentence) == tugaphone.phonemize(sentence, lect)


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
def test_lexicon_word_takes_lexicon_value(lect):
    lexicon = packaged_lexicon(lect, patches=True)
    plain = G2P(lect)
    engine = G2P(lect, pipeline=tugaphone.pipeline(lect))
    words = [w for w in sorted(lexicon)[:300] if plain.transcribe_word(w) != lexicon[w]]
    assert len(words) > 20
    for word in words:
        assert engine.transcribe_word(word) == lexicon[word]


def test_numbers_are_spelled_out():
    engine = G2P("pt-PT", pipeline=tugaphone.pipeline("pt-PT"))
    assert engine.transcribe("3 gatos") == engine.transcribe("três gatos")
    assert engine.transcribe("21 cadelas") == engine.transcribe("vinte e uma cadelas")


@pytest.mark.parametrize("sentence, marked", [
    ("Eu jogo o jogo.", "Eu jógo o jôgo."),
    ("Eu gosto do gosto.", "Eu gósto do gôsto."),
    ("Eu seco o pano seco.", "Eu séco o pano sêco."),
])
def test_homographs_are_marked(sentence, marked):
    engine = G2P("pt-PT", pipeline=tugaphone.pipeline("pt-PT"))
    assert engine.transcribe(sentence) == G2P("pt-PT").transcribe(marked)


@pytest.mark.parametrize("code", ["br", "gl", "es", "pt", "pt_PT", "xx-YY"])
def test_code_outside_list_dialects_raises(code):
    with pytest.raises(ValueError, match="list_dialects"):
        tugaphone.pipeline(code)


def test_lect_without_packaged_lexicon_has_empty_lexicon():
    assert tugaphone.pipeline("pt-AO").lexicon == {}
    assert tugaphone.pipeline("pt-PT-x-porto").lexicon == {}


def test_each_call_returns_a_new_lexicon():
    first, second = tugaphone.pipeline("pt-PT"), tugaphone.pipeline("pt-PT")
    assert first.lexicon == second.lexicon
    assert first.lexicon is not second.lexicon
