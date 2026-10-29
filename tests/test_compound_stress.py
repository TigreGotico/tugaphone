"""A hyphenated compound is one prosodic word with one primary stress.

Each element of a compound by juxtaposition keeps its own stress, and the
last one is the strongest: "pelo fato de ter cada radical o seu acento
tônico, sendo o último o mais forte e o que nos orienta na classificação
da posição do acento nas palavras compostas" (Bechara, *Moderna Gramática
Portuguesa*, p. 340, quoted in Ciberdúvidas, resposta 28042). So the last
element takes the primary mark ``ˈ`` and every earlier element takes the
secondary mark ``ˌ``, as the Portal da Língua Portuguesa writes
*guarda-chuva* ``gwˌaɾ|dɐ|ʃˈu|vɐ``.

A clitic joined by a hyphen is not a compound element. An enclitic
pronoun, an article or a preposition has no stress of its own and leans
on its host: *fala-se* is one prosodic word ``[ˈfalas]`` (Toneli 2011,
citing Vigário 2003). It takes no mark at all, neither ``ˈ`` nor ``ˌ``.
In mesoclisis the future or conditional ending after the pronoun is the
last stressed element, as the Portal writes *vê-lo-emos*
``vˌe|lu|ˈe|muʃ``.

Each expected row names its source. A row is a list with one entry per
hyphen element: ``(mark, syllable)`` gives the mark and the 0-based
syllable of that element it stands before, and ``None`` means no mark.
"""
import pytest

from tugaphone.registry import get_dialect_inventory
from tugaphone.tokenizer import Sentence

P, S = "ˈ", "ˌ"


def _rules_only(dialect_code):
    inv = get_dialect_inventory(dialect_code)
    object.__setattr__(inv, "IRREGULAR_WORDS", {})
    return inv


@pytest.fixture(scope="module")
def inventories():
    return {code: _rules_only(code) for code in ("pt-PT", "pt-BR")}


def element_marks(ipa):
    """One entry per space-separated element: (mark, syllable) or None."""
    out = []
    for element in ipa.split():
        marks = [(ch, element[:i].count("·"))
                 for i, ch in enumerate(element) if ch in (P, S)]
        assert len(marks) <= 1, f"{element!r} carries two marks"
        out.append(marks[0] if marks else None)
    return out


PT_PT = [
    # Portal da Língua Portuguesa, Lisbon
    ("guarda-chuva", [(S, 0), (P, 0)]),     # gwˌaɾ|dɐ|ʃˈu|vɐ
    ("pisca-pisca", [(S, 0), (P, 0)]),      # pˌiʃ|kɐ|pˈiʃ|kɐ
    ("couve-flor", [(S, 0), (P, 0)]),       # kˌo|vɨ|flˈoɾ
    ("segunda-feira", [(S, 1), (P, 0)]),    # sɨ|gˌũ|dɐ|fˈɐj|ɾɐ
    ("guarda-noturno", [(S, 0), (P, 1)]),   # gwˌaɾ|dɐ|nɔ|tˈuɾ|nu
    ("norte-americano", [(S, 0), (P, 3)]),  # nˌɔɾ|tɨ|ɐ|mɨ|ɾi|kˈɐ|nu
    ("pé-de-meia", [(S, 0), None, (P, 0)]),  # pˌɛ|dɨ|mˈɐj|ɐ
    ("bem-me-quer", [(S, 0), None, (P, 0)]),  # bˌɐ̃j|mɨ|kˈɛɾ
    ("vê-lo-emos", [(S, 0), None, (P, 0)]),  # vˌe|lu|ˈe|muʃ
    # Infopédia: one primary, on the last element; the article is atonic
    ("lobo-da-alsácia", [(S, 0), None, (P, 1)]),  # lobudaɫˈsasjɐ
    # Infopédia: pronominal verbs, the enclitic is atonic
    ("amancebar-se", [(P, 3), None]),       # ɐmɐ̃səˈbars
    ("atreves-te", [(P, 1), None]),         # ɐˈtrɛvəʃt
    # Enclisis and mesoclisis (Acordo Ortográfico 1990, Base VIII, 1.º b:
    # dá-la(s), fá-lo(s)-ás): the pronoun is atonic, the verb keeps the
    # stress, and in mesoclisis the ending is the last stressed element.
    ("chamo-me", [(P, 0), None]),
    ("dá-lo", [(P, 0), None]),
    ("fá-lo-ia", [(S, 0), None, (P, 0)]),
]

PT_BR = [
    # Portal da Língua Portuguesa, Rio de Janeiro
    ("guarda-chuva", [(S, 0), (P, 0)]),     # gwˌaɦ|dɐ|ʃˈu|vɐ
    ("pé-de-meia", [(S, 0), None, (P, 0)]),  # pˌɛ|dʒi|mˈej|ɐ
    ("bem-me-quer", [(S, 0), None, (P, 0)]),  # bˌẽj|mi|kˈɛɾ
    ("vê-lo-emos", [(S, 0), None, (P, 0)]),  # vˌe|lʊ|ˈẽ|mʊʃ
]


@pytest.mark.parametrize("word,expected", PT_PT)
def test_compound_marks_pt_pt(word, expected, inventories):
    ipa = Sentence(word, dialect=inventories["pt-PT"]).ipa
    assert element_marks(ipa) == expected, ipa


@pytest.mark.parametrize("word,expected", PT_BR)
def test_compound_marks_pt_br(word, expected, inventories):
    ipa = Sentence(word, dialect=inventories["pt-BR"]).ipa
    assert element_marks(ipa) == expected, ipa


@pytest.mark.parametrize("word,_", PT_PT)
def test_compound_has_one_primary(word, _, inventories):
    ipa = Sentence(word, dialect=inventories["pt-PT"]).ipa
    assert ipa.count(P) == 1, ipa


def test_space_separated_words_keep_their_own_primary(inventories):
    """Only the hyphen joins a compound: two words keep two primaries."""
    ipa = Sentence("guarda chuva", dialect=inventories["pt-PT"]).ipa
    assert element_marks(ipa) == [(P, 0), (P, 0)], ipa


def test_compound_inside_a_sentence(inventories):
    """The compound rule stops at the whitespace around the compound."""
    ipa = Sentence("guarda-chuva amarelo", dialect=inventories["pt-PT"]).ipa
    assert element_marks(ipa) == [(S, 0), (P, 0), (P, 2)], ipa
