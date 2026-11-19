"""European Portuguese ⟨ex⟩ before a consonant and the pretonic ⟨a⟩.

Infopédia (pt-PT) writes ⟨ex⟩ + consonant as a vowel plus the palatal glide
and [ʃ]: ``texto ˈtajʃtu``, ``contexto kõˈtajʃtu``, ``sexta ˈsajʃta``,
``pretexto prəˈtajʃtu``, ``extra ˈajʃtra``, ``explicar ajʃpliˈkar``,
``excelente ajʃsəˈlẽt``. The unified lexicon
(``TigreGotico/portuguese-unified-pronunciation-lexicon``, pt-PT rows with an
infopedia_url) transcribes the central vowel [ɐ] as ``a``, so the full form is
[ˈtɐjʃtu]. tugaphone reads these words through the orthography2ipa pt-PT
specs, which drop the glide: the ⟨x⟩ rows of ``pt-PT.json`` hold no ⟨ex⟩ +
consonant context.

The same lexicon writes the pretonic ⟨a⟩ of ``magistratura`` as the reduced
vowel: ``maʒiʃtraˈtura``, with the pt-PT broad symbol ``a`` for [ɐ].
"""
import pytest

from tugaphone import phonemize

LECTS = ["pt-PT", "pt-PT-x-lisbon"]

EX_GLIDE_CAUSE = (
    "orthography2ipa pt-PT.json has no ⟨ex⟩ + consonant rule: the e becomes [ɛ]/[e]/[ɐ] "
    "and ⟨x⟩ becomes [ʃ] with no [j]. Infopédia: texto ˈtajʃtu. "
    "TigreGotico/tugaphone#135"
)


ex_glide = pytest.mark.xfail(strict=True, reason=EX_GLIDE_CAUSE)


@pytest.mark.parametrize("lect", LECTS)
@pytest.mark.parametrize("word, expected", [
    pytest.param("texto", "ˈtɐjʃtu", marks=ex_glide),
    pytest.param("textos", "ˈtɐjʃtuʃ", marks=ex_glide),
    pytest.param("contexto", "kõˈtɐjʃtu", marks=ex_glide),
    pytest.param("pretexto", "pɾɨˈtɐjʃtu", marks=ex_glide),
    pytest.param("sexta", "ˈsɐjʃtɐ", marks=ex_glide),
])
def test_medial_ex_before_consonant_has_the_glide(lect, word, expected):
    assert phonemize(word, lect) == expected


@pytest.mark.parametrize("lect", LECTS)
@pytest.mark.parametrize("word", [
    pytest.param("extra", marks=ex_glide),
    pytest.param("explicar", marks=ex_glide),
    pytest.param("excelente", marks=ex_glide),
    pytest.param("exterior", marks=ex_glide),
])
def test_initial_ex_before_consonant_has_the_glide(lect, word):
    assert phonemize(word, lect).lstrip("ˈ").startswith("ɐjʃ")


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
    # Infopédia: magistratura maʒiʃtraˈtura, barato baˈratu, palavra paˈlavra, natureza natuˈreza
    assert phonemize(word, lect) == expected
