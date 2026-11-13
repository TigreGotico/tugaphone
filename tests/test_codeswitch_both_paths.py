"""Routing invariants that must hold under either code-switch classifier.

The keep-list in :mod:`tugaphone.langdetect` is the single source of truth for
"this token is Portuguese, do not route it out". The statistical detector and
the orthographic fallback both consult it, so these tests run under both via the
``classifier`` fixture.
"""
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.codeswitch import _CONTACT_STOPWORDS, _classify, is_contact_word
from tugaphone.langdetect import PORTUGUESE_KEEP, fold_diacritics, is_keep_word


@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


NATIVE_SENTENCES = [
    "por que este livro e para mim",
    "as casas",
    "como esta a tua mae",
    "no dia em que ele for",
    "quero mais um",
]


@pytest.mark.parametrize("sentence", NATIVE_SENTENCES)
def test_native_sentence_unchanged_by_contact_routing(ph, classifier, sentence):
    auto = ph.phonemize_sentence(sentence, "pt-PT", contact="auto")
    none = ph.phonemize_sentence(sentence, "pt-PT", contact="none")
    assert auto == none


def test_keep_list_wins_every_contact_stopword_homograph(classifier):
    # The contact stopword lists stay complete for the languages they document,
    # so they overlap the keep-list ("por" is Spanish, "mais" is French). Every
    # such homograph must still resolve to Portuguese.
    overlap = {w for w in _CONTACT_STOPWORDS if is_keep_word(w)}
    assert overlap, "expected the lists to overlap"
    for word in sorted(overlap):
        assert not is_contact_word(word), word
        assert _classify(word, "en") is None, word


@pytest.mark.parametrize("word", ["mae", "nao", "voce", "irma", "avo", "esta"])
def test_unaccented_keep_words_stay_portuguese(classifier, word):
    assert is_keep_word(word)
    assert not is_contact_word(word)
    assert _classify(word, "en") is None


def test_future_subjunctive_of_ser_stays_portuguese(classifier):
    for word in ["for", "fores", "formos", "forem"]:
        assert _classify(word, "en") is None, word


def test_fold_keeps_the_cedilla():
    # ç is a native Portuguese letter, so folding leaves it alone.
    assert fold_diacritics("faça") == "faça"
    assert fold_diacritics("mãe") == "mae"


def test_keep_list_covers_the_future_subjunctive():
    assert {"for", "fores", "formos", "forem"} <= PORTUGUESE_KEEP
