"""NL-TDD tests for the curated English loanword lexicon (:mod:`tugaphone.codeswitch`).

Loans in ``tugaphone/data/loanwords.json`` (ported from logus2k/tts_eu_pt,
Apache-2.0 — see the ``codeswitch`` module docstring) route to the English
contact path even when the orthographic heuristic and the Markov detector's
conservative margin would otherwise keep them Portuguese, because they carry
no non-native letter/digraph and their foreign statistical fit is only
marginally better than Portuguese. ``airbag`` is the canonical example: no
``k w y`` letter, no English digraph, not in the hand-picked stopword list —
the heuristic alone never flags it, but it is a common European-Portuguese
tech/consumer loan pronounced with English phonology.
"""
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.codeswitch import is_known_loanword


@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


# ---------------------------------------------------------------------------
# Lexicon membership.
# ---------------------------------------------------------------------------

def test_known_loanwords_flagged():
    for w in ["online", "software", "site", "airbag", "mainframe", "kit"]:
        assert is_known_loanword(w)


def test_lookup_is_case_insensitive():
    assert is_known_loanword("AIRBAG")
    assert is_known_loanword("Software")
    assert is_known_loanword("Online.")   # punctuation stripped like any token


def test_lookup_is_whole_word_not_substring():
    # "site" is a loanword; a token that merely contains it as a substring
    # must not match.
    assert is_known_loanword("site")
    assert not is_known_loanword("sitex")
    assert not is_known_loanword("multisite")  # substring, not the whole word


def test_unrelated_word_not_flagged():
    assert not is_known_loanword("cachorro")
    assert not is_known_loanword("português")


# ---------------------------------------------------------------------------
# Collision safety: a Portuguese word that also happens to be common English
# spelling must never be hijacked by the lexicon. Every one of the 774
# upstream entries was checked against tugalex's regional pronunciation
# dictionary; any hit (``cover``, ``face``, ``for``, ``gin``, ``java``,
# ``media``, ``metal``, ``pixel``, ``polo``, ``remix``, ``sugar``, ``xerox``,
# ...) was dropped from the shipped lexicon rather than forced to English.
# ---------------------------------------------------------------------------

_TUGALEX_COLLISIONS = [
    "boxers", "cheddar", "cover", "durex", "face", "for", "gin", "hindi",
    "java", "luge", "media", "metal", "pixel", "polo", "remix", "sugar",
    "xerox",
]


@pytest.mark.parametrize("word", _TUGALEX_COLLISIONS)
def test_tugalex_collisions_excluded_from_lexicon(word):
    assert not is_known_loanword(word)


def test_portuguese_sentence_with_english_spelled_words_unchanged(ph):
    # "for" (subjunctive of "ser") and "media" ("média", diacritic dropped)
    # both exist as ordinary Portuguese words; a sentence using them must
    # phonemize identically under contact="auto" and contact="none" — the
    # lexicon must never hijack them onto the English route.
    s = "se ele for a festa eu levo a media do jogo"
    auto = ph.phonemize_sentence(s, "pt-PT", contact="auto")
    none = ph.phonemize_sentence(s, "pt-PT", contact="none")
    assert auto == none


# ---------------------------------------------------------------------------
# Mixed Portuguese/loanword sentences.
# ---------------------------------------------------------------------------

def test_estou_online(ph):
    # "online" is in the pre-existing stopword list too, so this already
    # worked before the lexicon; kept here as the baseline mixed-sentence
    # case the others are compared against.
    auto = ph.phonemize_sentence("Estou online.", "pt-PT", contact="auto")
    none = ph.phonemize_sentence("Estou online.", "pt-PT", contact="none")
    assert auto != none
    assert auto.startswith("eʃˈto")   # "estou" stays Portuguese-transcribed
    for bad in ("ɹ", "ɒ", "ʌ", "θ", "h", "ː"):
        assert bad not in auto


def test_instalei_o_software_ontem(ph):
    auto = ph.phonemize_sentence("Instalei o software ontem.", "pt-PT", contact="auto")
    none = ph.phonemize_sentence("Instalei o software ontem.", "pt-PT", contact="none")
    assert auto != none
    for bad in ("ɹ", "ɒ", "ʌ", "θ", "h", "ː"):
        assert bad not in auto


def test_o_site_esta_em_baixo(ph):
    auto = ph.phonemize_sentence("O site está em baixo.", "pt-PT", contact="auto")
    none = ph.phonemize_sentence("O site está em baixo.", "pt-PT", contact="none")
    assert auto != none
    for bad in ("ɹ", "ɒ", "ʌ", "θ", "h", "ː"):
        assert bad not in auto


def test_comprei_um_airbag_novo(ph):
    # The load-bearing case: "airbag" carries no non-Portuguese letter, no
    # English digraph and is not in the hand-picked stopword list, so the
    # orthographic heuristic on its own never flags it — only the lexicon
    # (or the detector's statistical fit, when available) does.
    assert is_known_loanword("airbag")
    auto = ph.phonemize_sentence("Comprei um airbag novo.", "pt-PT", contact="auto")
    none = ph.phonemize_sentence("Comprei um airbag novo.", "pt-PT", contact="none")
    assert auto != none
    for bad in ("ɹ", "ɒ", "ʌ", "θ", "h", "ː"):
        assert bad not in auto
    # "novo" (Portuguese) stays the same on both sides of "airbag".
    assert auto.split()[0] == none.split()[0]        # "comprei"
    assert auto.split()[-1] == none.split()[-1]       # "novo."


# ---------------------------------------------------------------------------
# Packaging: the data file must actually ship (a broken wheel that drops it
# must fail loudly, not silently disable the feature).
# ---------------------------------------------------------------------------

def test_packaged_data_file_loads_with_expected_size():
    from tugaphone.codeswitch import _loanwords

    words = _loanwords()
    assert len(words) > 600
    assert "airbag" in words
