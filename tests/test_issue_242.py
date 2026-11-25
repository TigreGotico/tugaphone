"""pt-PT paraquedas opens its first ⟨a⟩: [paɾɐˈkɛdɐʃ].

The Acordo Ortográfico de 1945 writes the compound with a hyphen and an acute
accent on its first element, in its list of hyphenated compounds: "conta-gotas,
deita-gatos, finca-pé, guarda-chuva, pára-quedas, porta-bandeira". Base 18 gives
the accent its function: "Emprega-se o acento agudo nas palavras que, tendo vogal
tónica aberta, sejam homógrafas de palavras sem acentuação própria. Assim se
diferençam: pára, flexão de parar, e para, preposição". AO1990 Base XV 1 writes
the compound as one word, "paraquedas", and the Vocabulário Ortográfico do
Português (VOP) lists "para-quedas" as its variant. The first element keeps the
open vowel of the verb form pára, so the first ⟨a⟩ is not reduced to [ɐ].
"""
from tugaphone import phonemize


def test_paraquedas_reads_its_first_a_open():
    assert phonemize("paraquedas", "pt-PT") == "paɾɐˈkɛdɐʃ"
