"""A forced word keeps the context of the words around it.

The engine joins the plain runs and the forced words back into one sentence
for the homograph marks, so the expansion of a plain run must keep the spaces
at its ends. A ``<phoneme>`` tag changes how its own word is read and nothing
else: every other word reads as it does in the same sentence without the tag.
"""
import pytest

from tugaphone.lattice_core import phonemize

CASES = [
    # "jogo" after the article "o" is the noun, closed [o]; the forced word
    # starts the sentence.
    ('<phoneme ph="ˈʒoɡu">jogo</phoneme> o jogo 2 vezes.',
     "jogo o jogo 2 vezes.", 2),
    # "força" after the article "a" is the noun, closed [o]; the forced word
    # sits in the middle of the sentence.
    ('Ela viu <phoneme ph="ˈfoɾsɐ">força</phoneme> a força dele.',
     "Ela viu força a força dele.", 4),
]


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("tagged, plain, index", CASES)
def test_forced_word_keeps_the_reading_of_its_neighbours(tagged, plain, index, lang):
    expected = phonemize(plain, lang).split()
    got = phonemize(tagged, lang).split()
    assert len(got) == len(expected)
    assert got[index] == expected[index]
