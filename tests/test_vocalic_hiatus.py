"""Vocalic hiatus (#47).

Expectations are hand-derived from Portuguese orthography: a hiatus is two
vowels split across neighbouring syllables (sa.í.da), a diphthong is two
vowels in one syllable (pai, mui.to). In the IPA a hiatus is a nucleus, a
stress mark, then a second nucleus. A diphthong has a glide [j w] and no
mark between its two parts.
"""
import re
import unicodedata

import pytest

from tugaphone import phonemize

HIATUS = re.compile("[aɐeɛəɨioɔuʊ]̃?ˈ[aɐeɛəɨioɔuʊ]")


@pytest.mark.parametrize("word", [
    "saída",   # sa.í.da
    "país",    # pa.ís
    "raiz",    # ra.iz
    "ciúme",   # ci.ú.me
    "moinho",  # mo.i.nho
    "saúde",   # sa.ú.de
    "caiu",    # ca.iu: "a" and "i" straddle the split
    "baú",     # ba.ú
])
def test_hiatus_present(word):
    out = unicodedata.normalize("NFD", phonemize(word, "pt-PT"))
    assert HIATUS.search(out), f"expected a hiatus in {word!r}, got {out}"


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
def test_no_hiatus(word):
    out = unicodedata.normalize("NFD", phonemize(word, "pt-PT"))
    assert not HIATUS.search(out), f"did not expect a hiatus in {word!r}, got {out}"
