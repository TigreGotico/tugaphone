"""The u of ⟨qu gu⟩ in the words that pronounce it is [w] in tugaphone.phonemize.

Priberam gives the pronunciation |güen| for aguentar and |àgüí| for sagui,
with "Grafia anterior ao Acordo Ortográfico de 1990: agüentar" and "sagüi":
the trema marked the [w], and the Acordo Ortográfico 1990 (Base XIV, 1.º)
removed the mark, not the sound. VOLP (ABL) writes aguentar. A verb form
keeps the onset of its stem.
"""
import pytest

from tugaphone import phonemize

GLIDE_WORDS = [
    ("aguentar", "ɡw"), ("aguenta", "ɡw"), ("aguento", "ɡw"),
    ("aguentamos", "ɡw"), ("frequenta", "kw"), ("frequento", "kw"),
    ("sagui", "ɡw"),
]
PASSING = {("pt-PT", "aguentar")}


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("word,glide", GLIDE_WORDS)
def test_pronounced_u_is_a_glide(lect, word, glide, request):
    if (lect, word) not in PASSING:
        request.applymarker(pytest.mark.xfail(
            strict=True, reason="o2i has no rule for the pronounced u of "
            "qu/gu; only a lexicon row gives [w] (tugaphone #382)"))
    assert glide in phonemize(word, lect)
