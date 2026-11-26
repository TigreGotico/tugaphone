"""An atonic function word takes no stress mark on the rules path.

A monosyllable in the spec's ``stress.cliticless_words`` (an article, a
pronoun, a preposition or the conjunction *que*) leans on the next word and
has no stress of its own. Infopédia writes these words without a stress mark
and stressed monosyllables with one. Each gold below is the Infopédia (pt-PT)
transcription in the unified gold
(``TigreGotico/portuguese-unified-pronunciation-lexicon``). Infopédia writes
the reduced vowel as ə; this file writes it as ɨ, as the pt-PT spec does.
*dá* is not in that gold. Its acute accent marks the stressed vowel.
"""
import pytest

from tugaphone import phonemize

MARKS = "ˈˌ"


def ipa(text):
    return phonemize(text, "pt-PT").strip()


@pytest.mark.parametrize("word,gold", [
    ("que", "kɨ"), ("se", "sɨ"), ("de", "dɨ"), ("lhe", "ʎɨ"),
    ("me", "mɨ"), ("te", "tɨ"), ("o", "u")])
def test_function_word_has_no_stress_mark(word, gold):
    assert ipa(word) == gold


@pytest.mark.parametrize("word,gold", [
    ("quê", "ˈke"), ("pé", "ˈpɛ"), ("mar", "ˈmaɾ"), ("bom", "ˈbõ"),
    ("sol", "ˈsoɫ"), ("dá", "ˈda")])
def test_stressed_monosyllable_keeps_its_mark(word, gold):
    # only the mark is compared; the vowel quality is not under test here
    assert ipa(word)[0] == gold[0] == "ˈ"


# Each row gives, word by word, whether the word carries a stress mark.
@pytest.mark.parametrize("sentence,marked", [
    ("eu sei que vens", [True, True, False, True]),
    ("o que é que queres", [False, False, True, False, True]),
])
def test_sentence_marks_only_the_stressed_words(sentence, marked):
    words = ipa(sentence).split()
    assert len(words) == len(marked), words
    assert [w[0] in MARKS for w in words] == marked, words
