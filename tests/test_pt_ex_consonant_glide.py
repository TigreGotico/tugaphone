"""European Portuguese ⟨ex⟩ before a consonant and the pretonic ⟨a⟩.

A spec's ⟨e⟩ before ⟨x⟩ plus a consonant takes the diphthong of that spec's
⟨ei⟩. pt-PT writes [ej]: texto ˈtejʃtu, explicar ejʃpliˈkaɾ, like deixar
dejˈʃaɾ. pt-PT-x-lisbon writes [ɐj] in every position, as it does for ⟨ei⟩:
texto ˈtɐjʃtu, deixar dɐjˈʃaɾ. The other pt-PT lects inherit [ej].

Sources: Leite de Vasconcellos, Esquisse d'une dialectologie portugaise (1901),
§56-g p. 109 and §44j p. 92; Cruz-Ferreira (1999: 128) in Handbook of the
International Phonetic Association. Infopédia writes [ɐj]; that carries the
Lisbon assumption and does not settle the pt-PT norm.

The pretonic ⟨a⟩ is the reduced vowel: magistratura mɐʒiʃtɾɐˈtuɾɐ, barato
bɐˈɾatu, palavra pɐˈlavɾɐ, natureza nɐtuˈɾezɐ.
"""
import pytest

from tugaphone import phonemize

LECTS = ["pt-PT", "pt-PT-x-lisbon"]


@pytest.mark.parametrize("word, expected", [
    ("texto", "ˈtejʃtu"),
    ("textos", "ˈtejʃtuʃ"),
    ("contexto", "kõˈtejʃtu"),
    ("pretexto", "pɾɨˈtejʃtu"),
    ("sexta", "ˈsejʃtɐ"),
])
def test_pt_pt_medial_ex_before_consonant_takes_the_ei_diphthong(word, expected):
    assert phonemize(word, "pt-PT") == expected


@pytest.mark.parametrize("word, expected", [
    ("texto", "ˈtɐjʃtu"),
    ("textos", "ˈtɐjʃtuʃ"),
    ("contexto", "kõˈtɐjʃtu"),
    ("pretexto", "pɾɨˈtɐjʃtu"),
    ("sexta", "ˈsɐjʃtɐ"),
])
def test_lisbon_medial_ex_before_consonant_takes_the_ei_diphthong(word, expected):
    assert phonemize(word, "pt-PT-x-lisbon") == expected


@pytest.mark.parametrize("lect, diphthong", [
    ("pt-PT", "ej"),
    ("pt-PT-x-lisbon", "ɐj"),
])
def test_ex_diphthong_equals_the_ei_diphthong(lect, diphthong):
    assert phonemize("deixar", lect) == "d" + diphthong + "ˈʃaɾ"
    assert diphthong in phonemize("texto", lect)


@pytest.mark.parametrize("lect, word, prefix", [
    ("pt-PT", "extra", "ejʃt"),
    ("pt-PT", "explicar", "ejʃp"),
    ("pt-PT", "excelente", "ejʃs"),
    ("pt-PT", "exterior", "ejʃt"),
    ("pt-PT-x-lisbon", "extra", "ɐjʃt"),
    ("pt-PT-x-lisbon", "explicar", "ɐjʃp"),
    ("pt-PT-x-lisbon", "excelente", "ɐjʃs"),
    ("pt-PT-x-lisbon", "exterior", "ɐjʃt"),
])
def test_initial_ex_before_consonant_takes_the_ei_diphthong(lect, word, prefix):
    assert phonemize(word, lect).lstrip("ˈ").startswith(prefix)


@pytest.mark.parametrize("lect", LECTS)
@pytest.mark.parametrize("word", ["exame", "exato", "exalar", "exibir", "exumar", "exhalar", "sexo"])
def test_ex_before_a_vowel_or_h_takes_no_glide(lect, word):
    """The rule covers ⟨x⟩ plus a consonant only: ⟨x⟩ before a vowel or ⟨h⟩ keeps a plain vowel."""
    ipa = phonemize(word, lect)
    assert "ej" not in ipa and "ɐj" not in ipa

@pytest.mark.parametrize("lect", LECTS)
def test_texto_and_textos_share_the_vowel(lect):
    assert phonemize("texto", lect)[:3] == phonemize("textos", lect)[:3]


@pytest.mark.parametrize("lect", LECTS)
@pytest.mark.parametrize("word, expected", [
    ("magistratura", "mɐʒiʃtɾɐˈtuɾɐ"),
    ("barato", "bɐˈɾatu"),
    ("palavra", "pɐˈlavɾɐ"),
    ("natureza", "nɐtuˈɾezɐ"),
    ("temperatura", "tẽpɨɾɐˈtuɾɐ"),
])
def test_pretonic_a_is_reduced(lect, word, expected):
    # Infopédia: mɐʒiʃtrɐˈturɐ, bɐˈratu, pɐˈlavrɐ, nɐtuˈrezɐ, tẽpərɐˈturɐ
    assert phonemize(word, lect) == expected
