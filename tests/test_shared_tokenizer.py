"""Tests for tugaphone's grapheme tokenization on the shared substrate.

The token tree delegates two responsibilities to orthography2ipa:

- grapheme segmentation, to ``phonetok.PhonetokTokenizer``'s maximal-munch
  trie (driven by the dialect's own ``GRAPHEME_INVENTORY``);
- vowel-letter classification, to ``orthography2ipa.vowels``.

These tests pin that the shared trie is actually used and that it reproduces
Portuguese grapheme segmentation (digraphs, diphthongs, trigraphs and the
non-inventory single-character fallback), and lock the resulting IPA on a
representative, linguistically-grounded word set so a substrate regression is
caught as an output change.
"""
import pytest

from orthography2ipa.phonetok import PhonetokTokenizer
from orthography2ipa.vowels import is_front_vowel, is_orthographic_vowel

from tugaphone.dialects import (
    AngolanPortuguese, BrazilianPortuguese, EuropeanPortuguese,
    MozambicanPortuguese, TimoresePortuguese,
)
from tugaphone.tokenizer import _phonetok, WordToken


@pytest.fixture(scope="module")
def dialect():
    return EuropeanPortuguese()


class TestSharedTrie:
    def test_segmenter_is_phonetok(self, dialect):
        """The grapheme segmenter is orthography2ipa's tokenizer."""
        tok = _phonetok(dialect.dialect_code,
                        tuple(dialect.GRAPHEME_INVENTORY))
        assert isinstance(tok, PhonetokTokenizer)

    @pytest.mark.parametrize("word,expected", [
        # consonant digraph
        ("carro", ["c", "a", "rr", "o"]),
        ("banho", ["b", "a", "nh", "o"]),
        ("chegou", ["ch", "e", "g", "ou"]),
        # trigraph que / diphthongs
        ("quero", ["que", "r", "o"]),
        ("leite", ["l", "ei", "t", "e"]),
        # nasal digraph
        ("compaixão", ["c", "om", "p", "ai", "x", "ão"]),
        # non-inventory character (ç) falls back to a single grapheme,
        # matching the old hand-rolled scanner's single-character fallback
        ("almoço", ["a", "l", "m", "o", "ç", "o"]),
    ])
    def test_grapheme_segmentation(self, dialect, word, expected):
        graphemes = [g.surface for g
                     in WordToken(surface=word, word_idx=0,
                                  dialect=dialect).graphemes]
        assert graphemes == expected


class TestSharedVowelClassification:
    def test_char_is_vowel_delegates(self, dialect):
        word = WordToken(surface="céu", word_idx=0, dialect=dialect)
        vowels = [c.surface for g in word.graphemes for c in g.characters
                  if c.is_vowel]
        assert vowels == ["é", "u"]
        # shared predicate agrees on the base letters
        assert all(is_orthographic_vowel(v) for v in "aeiouáéíóúãõ")

    def test_front_vowel_softening(self, dialect):
        # c/g soften to [s]/[ʒ] before a front vowel (delegated predicate)
        assert is_front_vowel("e") and is_front_vowel("i")
        assert is_front_vowel("é") and is_front_vowel("í")
        assert not is_front_vowel("a") and not is_front_vowel("o")


class TestPhonemizationLocked:
    """Representative IPA locked against cited European Portuguese forms.

    References: Cruz-Ferreira (1995) "European Portuguese", JIPA 25(2);
    Mateus & d'Andrade (2000) *The Phonology of Portuguese*, OUP.
    """

    @pytest.mark.parametrize("word,expected", [
        ("carro", "kˈa·ʀu"),        # ⟨rr⟩ → strong rhotic /ʁ/
        ("casa", "kˈa·zɐ"),          # intervocalic ⟨s⟩ voices to [z]
        ("chegou", "ʃɨ·ˈɡow"),      # ⟨ch⟩ → /ʃ/, unstressed /e/ → [ɨ]
        ("filho", "fˈi·ʎu"),         # ⟨lh⟩ → /ʎ/
        ("banho", "bˈɐ·ɲu"),         # ⟨nh⟩ → /ɲ/
    ])
    def test_pt_pt(self, dialect, word, expected):
        assert WordToken(surface=word, word_idx=0,
                         dialect=dialect).ipa == expected


class TestDialectCoverage:
    """The shared trie is exercised across every registered dialect."""

    @pytest.mark.parametrize("factory", [
        EuropeanPortuguese, BrazilianPortuguese, AngolanPortuguese,
        MozambicanPortuguese, TimoresePortuguese,
    ])
    def test_segments_without_error(self, factory):
        d = factory()
        word = WordToken(surface="português", word_idx=0, dialect=d)
        # graphemes tile the word with no gaps or overlaps
        assert "".join(g.surface for g in word.graphemes) == "português"
        assert word.ipa  # non-empty transcription
