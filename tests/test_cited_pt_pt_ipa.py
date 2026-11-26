"""Representative pt-PT IPA locked against cited European Portuguese forms.

References: Cruz-Ferreira (1995) "European Portuguese", JIPA 25(2);
Mateus & d'Andrade (2000) *The Phonology of Portuguese*, OUP. The expected
forms carry syllable dots; the output carries none.
"""
import pytest

from tugaphone import phonemize


@pytest.mark.parametrize("word,expected", [
    pytest.param("carro", "ˈka·ʀu", marks=pytest.mark.xfail(strict=True, reason=
        "the pt-PT spec reads ⟨rr⟩ as the fricative [ʁ]; the cited form has the trill [ʀ]")),  # ⟨rr⟩ → strong rhotic
    ("casa", "ˈka·zɐ"),          # intervocalic ⟨s⟩ voices to [z]
    pytest.param("chegou", "ʃɨ·ˈɡow", marks=pytest.mark.xfail(strict=True, reason=
        "the pt-PT spec reduces final ⟨ou⟩ to [o]; the cited form keeps the diphthong [ow]")),  # ⟨ch⟩ → /ʃ/, unstressed /e/ → [ɨ]
    ("filho", "ˈfi·ʎu"),         # ⟨lh⟩ → /ʎ/
    ("banho", "ˈbɐ·ɲu"),         # ⟨nh⟩ → /ɲ/, Portal da Língua Portuguesa Lisbon bˈɐ|ɲu
])
def test_pt_pt(word, expected):
    assert phonemize(word, "pt-PT") == expected.replace("·", "")
