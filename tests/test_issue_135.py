"""pt-PT texto keeps its [j] glide and magistratura reduces its pretonic ⟨a⟩.

pt-PT writes ⟨e⟩ before ⟨x⟩ plus a consonant as [ej], like ⟨ei⟩ in deixar:
texto [ˈtejʃtu]. pt-PT-x-lisbon writes [ɐj] in every position: texto [ˈtɐjʃtu],
the value that the report of tugaphone#135 expects. Sources: Leite de
Vasconcellos, Esquisse d'une dialectologie portugaise (1901), §56-g p. 109 and
§44j p. 92; Cruz-Ferreira (1999: 128) in the Handbook of the International
Phonetic Association. Singular and plural read the same vowel.

The pretonic ⟨a⟩ of magistratura is the reduced vowel, as in Infopédia's
[mɐʒiʃtrɐˈturɐ].
"""
import pytest

from tugaphone import phonemize


@pytest.mark.parametrize("lect, texto, textos", [
    ("pt-PT", "ˈtejʃtu", "ˈtejʃtuʃ"),
    ("pt-PT-x-lisbon", "ˈtɐjʃtu", "ˈtɐjʃtuʃ"),
])
def test_texto_keeps_the_glide_in_singular_and_plural(lect, texto, textos):
    assert phonemize("texto", lect) == texto
    assert phonemize("textos", lect) == textos


@pytest.mark.parametrize("lect", ["pt-PT", "pt-PT-x-lisbon"])
def test_magistratura_reduces_its_pretonic_a(lect):
    assert phonemize("magistratura", lect) == "mɐʒiʃtɾɐˈtuɾɐ"
