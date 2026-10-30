"""An inflected form keeps the [w] of the word it inflects.

A plural adds -s (*linguiça*, *linguiças*), a word in -im makes its plural
in -ins (*pinguim*, *pinguins*), an adjective in -o has a feminine in -a
(*tranquilo*, *tranquila*), and a verb conjugates on its stem (*aguentar*,
*aguentou*). None of that touches the ⟨qu gu⟩ onset, so each form reads
the u as its lemma does. The lemma readings are the Infopédia forms in the
unified gold (``TigreGotico/portuguese-unified-pronunciation-lexicon``):
*linguiça* ``lĩˈɡwisɐ``, *pinguim* ``pĩˈɡwĩ``, *aguentar* ``ɐɡwẽˈtar``,
*frequente* ``frəˈkwẽt``. The Acordo Ortográfico 1990 (Base XIV, 1.º) lists
*tranquilo* and *linguista* with a pronounced u.

A word that only shares the first letters of a listed verb is not one of
its forms: Infopédia gives *argueiro* ``ɐrˈɡɐjru`` and *equipa* ``eˈkipɐ``
with a silent u.
"""
import pytest

from tugaphone.registry import get_dialect_inventory
from tugaphone.tokenizer import Sentence, pronounces_qu_gu_u


@pytest.fixture(scope="module")
def pt():
    inv = get_dialect_inventory("pt-PT")
    object.__setattr__(inv, "IRREGULAR_WORDS", {})
    return inv


def onset(word, inv):
    ipa = Sentence(word, dialect=inv).ipa.strip()
    for ch in "ˈˌ·":
        ipa = ipa.replace(ch, "")
    return ipa


@pytest.mark.parametrize("word,glide", [
    ("linguiças", "ɡw"), ("pinguins", "ɡw"), ("tranquila", "kw"),
    ("tranquilos", "kw"), ("linguistas", "ɡw"), ("aguentou", "ɡw"),
    ("aguentamos", "ɡw"), ("frequentes", "kw"), ("frequentou", "kw"),
    ("cinquentas", "kw"), ("antiguidades", "ɡw"),
])
def test_inflected_form_keeps_the_glide(word, glide, pt):
    assert glide in onset(word, pt), onset(word, pt)


@pytest.mark.parametrize("word,consonant", [("argueiro", "ɡ"), ("equipa", "k")])
def test_shared_prefix_is_not_a_form(word, consonant, pt):
    out = onset(word, pt)
    assert consonant + "w" not in out and consonant + "u" not in out, out
    assert not pronounces_qu_gu_u(word)
