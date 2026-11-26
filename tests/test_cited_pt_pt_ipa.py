"""Representative pt-PT IPA locked against cited European Portuguese forms.

References: Cruz-Ferreira (1995) "European Portuguese", JIPA 25(2);
Mateus & d'Andrade (2000) *The Phonology of Portuguese*, OUP. The expected
forms carry syllable dots; the output carries none.
"""
import pytest

from tugaphone import phonemize


@pytest.mark.parametrize("word,expected", [
    # ⟨rr⟩ → strong rhotic: the trill [ʀ] (Cruz-Ferreira; Infopédia ˈkaʀu) or the
    # uvular fricative [ʁ], the usual realization (Mateus & d'Andrade 2000)
    ("carro", ("ˈka·ʀu", "ˈka·ʁu")),
    ("casa", "ˈka·zɐ"),          # intervocalic ⟨s⟩ voices to [z]
    # ⟨ch⟩ → /ʃ/, unstressed /e/ → [ɨ]; ⟨ou⟩ is [o] in the standard and [ow] in
    # northern and conservative speech (Mateus & d'Andrade 2000)
    ("chegou", ("ʃɨ·ˈɡow", "ʃɨ·ˈɡo")),
    ("filho", "ˈfi·ʎu"),         # ⟨lh⟩ → /ʎ/
    ("banho", "ˈbɐ·ɲu"),         # ⟨nh⟩ → /ɲ/, Portal da Língua Portuguesa Lisbon bˈɐ|ɲu
])
def test_pt_pt(word, expected):
    accepted = (expected,) if isinstance(expected, str) else expected
    assert phonemize(word, "pt-PT") in {form.replace("·", "") for form in accepted}
