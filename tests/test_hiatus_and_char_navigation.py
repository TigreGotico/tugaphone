"""NL-TDD: vocalic hiatus detection (#47) and cross-grapheme char navigation (#49).

Expectations are hand-derived from Portuguese orthography, not read back from
the tokenizer: a hiatus is two vowels split across neighbouring syllables
(sa.í.da), a diphthong is two vowels in one syllable/grapheme (pai, mui.to).
"""

import pytest

from tugaphone.dialects import EuropeanPortuguese
from tugaphone.tokenizer import Sentence


def _word(surface):
    return Sentence(surface, dialect=EuropeanPortuguese()).words[0]


def _vowel_graphemes(surface):
    return [g for g in _word(surface).graphemes if g.is_vowel_grapheme]


class TestVocalicHiatus:
    @pytest.mark.parametrize("word", [
        "saída",   # sa.í.da
        "país",    # pa.ís
        "raiz",    # ra.iz
        "ciúme",   # ci.ú.me
        "moinho",  # mo.i.nho
        "saúde",   # sa.ú.de
        "caiu",    # ca.iu -> here "iu" stays one grapheme (diphthong within
                   # the second syllable) but "a" and "i" straddle the split
        "baú",     # ba.ú
    ])
    def test_hiatus_present(self, word):
        assert any(g.is_vocalic_hiatus for g in _vowel_graphemes(word)), \
            f"expected a hiatus vowel in {word!r}"

    @pytest.mark.parametrize("word", [
        "pai",
        "mãe",
        "muito",
        "quatro",
        "chuva",
        "cai",
        "seis",
        "touro",
    ])
    def test_no_hiatus(self, word):
        assert not any(g.is_vocalic_hiatus for g in _vowel_graphemes(word)), \
            f"did not expect a hiatus vowel in {word!r}"


class TestCharNavigationAcrossGraphemes:
    def test_chave_h_next_char_crosses_into_next_grapheme(self):
        # "chave" -> graphemes "ch", "a", "v", "e"
        w = _word("chave")
        ch = w.graphemes[0]
        assert ch.surface == "ch"
        h = ch.characters[1]
        assert h.surface == "h"
        assert h.next_char is not None
        assert h.next_char.normalized == "a"
        assert h.next_char.parent_grapheme is w.graphemes[1]

    def test_carro_a_next_char_crosses_into_rr_grapheme(self):
        # "carro" -> graphemes "c", "a", "rr", "o"
        w = _word("carro")
        a = w.graphemes[1]
        assert a.surface == "a"
        assert a.characters[-1].next_char is not None
        assert a.characters[-1].next_char.normalized == "r"
        assert a.characters[-1].next_char.parent_grapheme is w.graphemes[2]
        assert a.characters[-1].next_char.char_idx == 0

    def test_carro_rr_prev_char_crosses_into_a_grapheme(self):
        w = _word("carro")
        rr = w.graphemes[2]
        assert rr.surface == "rr"
        first_r = rr.characters[0]
        assert first_r.prev_char is not None
        assert first_r.prev_char.normalized == "a"
        assert first_r.prev_char.parent_grapheme is w.graphemes[1]

    def test_first_char_of_word_has_no_prev_char(self):
        w = _word("carro")
        first = w.graphemes[0].characters[0]
        assert first.prev_char is None

    def test_last_char_of_word_has_no_next_char(self):
        w = _word("carro")
        last = w.graphemes[-1].characters[-1]
        assert last.next_char is None

    def test_prev_next_letter_helpers_unchanged(self):
        # _prev_letter/_next_letter already spanned boundaries via prefix/suffix;
        # they must keep returning the same letters now that prev_char/next_char
        # do the crossing directly.
        w = _word("chave")
        h = w.graphemes[0].characters[1]
        assert h._next_letter == "a"
        a = w.graphemes[1]
        assert a.characters[0]._prev_letter == "h"
