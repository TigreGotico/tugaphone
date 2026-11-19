"""European Portuguese ⟨ex⟩ before a consonant and the pretonic ⟨a⟩.

Infopédia (pt-PT) writes ⟨ex⟩ + consonant with a central vowel, the palatal
glide and [ʃ]: texto ˈtɐjʃtu, contexto kõˈtɐjʃtu, pretexto prəˈtɐjʃtu,
sexta ˈsɐjʃtɐ, extra ˈɐjʃtrɐ, explicar ɐjʃpliˈkar, excelente ɐjʃsəˈlẽt(ə),
exterior ɐjʃtəˈrjor. These are the ``ipa`` values of
orthography2ipa/.benchmark_cache/infopedia_pt_ipa.jsonl, the cached Infopédia
dictionary rows. tugaphone reads these words through the orthography2ipa pt-PT
spec, whose ⟨x⟩ rows hold no ⟨ex⟩ + consonant context, so the glide is lost.

The Lisbon dictionary of the Portal da Língua Portuguesa, read through tugalex
(``TugaLexicon().get_phonemes(word, "lbx")``), disagrees for medial ⟨ex⟩: texto
tˈɐʃ·tu, contexto kõ·tˈɐʃ·tu, pretexto pɾɨ·tˈɐʃ·tu, sexta sˈɐʃ·tɐ, with no
glide. The pt-PT-x-lisbon spec produces that on purpose: the rule
LX_STRESSED_E_PREPALATAL gives [ɐ] before a palatal (Cunha & Cintra, Nova
Gramática do Português Contemporâneo, 7th ed., p. 49). The Lisbon rows below
pin that output. The same dictionary gives extra ˈiʃ·tɾɐ, and for word-initial
⟨ex⟩ it gives ɐjʃ·pli·kˈaɾ, ɐjʃ·sɨ·lˈẽt and ɐjʃ·tɨ·ɾjˈoɾ.

Infopédia writes the pretonic ⟨a⟩ as the reduced vowel: magistratura
mɐʒiʃtrɐˈturɐ, barato bɐˈratu, palavra pɐˈlavrɐ, natureza nɐtuˈrezɐ,
temperatura tẽpərɐˈturɐ.
"""
import pytest

from tugaphone import phonemize

LECTS = ["pt-PT", "pt-PT-x-lisbon"]

EX_GLIDE_CAUSE = (
    "orthography2ipa pt-PT.json has no ⟨ex⟩ + consonant rule: ⟨x⟩ becomes [ʃ] with no [j] "
    "and the vowel is not [ɐ]. Infopédia: texto ˈtɐjʃtu. TigreGotico/tugaphone#135"
)
ex_glide = pytest.mark.xfail(strict=True, reason=EX_GLIDE_CAUSE)


@pytest.mark.parametrize("word, expected", [
    pytest.param("texto", "ˈtɐjʃtu", marks=ex_glide),
    pytest.param("textos", "ˈtɐjʃtuʃ", marks=ex_glide),
    pytest.param("contexto", "kõˈtɐjʃtu", marks=ex_glide),
    pytest.param("pretexto", "pɾɨˈtɐjʃtu", marks=ex_glide),
    pytest.param("sexta", "ˈsɐjʃtɐ", marks=ex_glide),
])
def test_pt_pt_medial_ex_before_consonant_has_the_glide(word, expected):
    assert phonemize(word, "pt-PT") == expected


@pytest.mark.parametrize("word, expected", [
    ("texto", "ˈtɐʃtu"),
    ("textos", "ˈtɐʃtuʃ"),
    ("contexto", "kõˈtɐʃtu"),
    ("pretexto", "pɾɨˈtɐʃtu"),
    ("sexta", "ˈsɐʃtɐ"),
])
def test_lisbon_medial_ex_has_no_glide(word, expected):
    # Portal da Língua Portuguesa Lisbon dictionary: texto tˈɐʃ·tu, pretexto pɾɨ·tˈɐʃ·tu, sexta sˈɐʃ·tɐ
    assert phonemize(word, "pt-PT-x-lisbon") == expected


@pytest.mark.parametrize("lect, word, prefix", [
    pytest.param("pt-PT", "extra", "ɐjʃt", marks=ex_glide),
    pytest.param("pt-PT", "explicar", "ɐjʃp", marks=ex_glide),
    pytest.param("pt-PT", "excelente", "ɐjʃs", marks=ex_glide),
    pytest.param("pt-PT", "exterior", "ɐjʃt", marks=ex_glide),
    pytest.param("pt-PT-x-lisbon", "explicar", "ɐjʃp", marks=ex_glide),
    pytest.param("pt-PT-x-lisbon", "excelente", "ɐjʃs", marks=ex_glide),
    pytest.param("pt-PT-x-lisbon", "exterior", "ɐjʃt", marks=ex_glide),
])
def test_initial_ex_before_consonant_has_the_glide(lect, word, prefix):
    assert phonemize(word, lect).lstrip("ˈ").startswith(prefix)


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
