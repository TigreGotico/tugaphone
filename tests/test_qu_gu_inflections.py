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

from tugaphone import phonemize


def onset(word):
    ipa = phonemize(word, "pt-PT").strip()
    for ch in "ˈˌ":
        ipa = ipa.replace(ch, "")
    return ipa


@pytest.mark.parametrize("word,glide", [
    ("linguiças", "ɡw"),
    pytest.param("pinguins", "ɡw", marks=pytest.mark.xfail(strict=True, reason=(
        "the plural pinguins loses the [w] of pinguim: the u reads as silent"))),
    ("tranquila", "kw"),
    ("tranquilos", "kw"), ("linguistas", "ɡw"), ("aguentou", "ɡw"),
    ("aguentamos", "ɡw"), ("frequentes", "kw"), ("frequentou", "kw"),
    ("cinquentas", "kw"), ("antiguidades", "ɡw"),
])
def test_inflected_form_keeps_the_glide(word, glide):
    assert glide in onset(word), onset(word)


@pytest.mark.parametrize("word,consonant", [("argueiro", "ɡ"), ("equipa", "k")])
def test_shared_prefix_is_not_a_form(word, consonant):
    out = onset(word)
    assert consonant + "w" not in out and consonant + "u" not in out, out
