"""pt-PT paraquedas family: the first vowel is the full [a].

The o2i-lexicons pt-PT exceptions carry the Infopédia readings of
paraquedas, paraquedismo and paraquedista (o2i-lexicons #99). The grapheme
rules reduce the unstressed first ⟨a⟩ to [ɐ], so these pass only when the
lexicon path reaches the output.
"""
import pytest

from tugaphone import TugaPhonemizer


@pytest.fixture(scope="module")
def pho():
    return TugaPhonemizer()


@pytest.mark.parametrize("word, ipa", [
    ("paraquedas", "paɾɐˈkɛdɐʃ"),
    ("paraquedismo", "paɾɐkɨˈdiʒmu"),
    ("paraquedista", "paɾɐkɨˈdiʃtɐ"),
    ("paraquedistas", "paɾɐkɨˈdiʃtɐʃ"),
])
def test_paraquedas_family_keeps_full_first_vowel(pho, word, ipa):
    assert pho.phonemize_sentence(word, "pt-PT") == ipa
