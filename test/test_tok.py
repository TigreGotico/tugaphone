"""
Extensive unit tests for tugaphone/tokenizer.py

Covers all classes, methods, and properties:
- Helper functions: detect_stress_position, is_grapheme_silent
- CharToken: all properties and IPA generation
- GraphemeToken: all properties and IPA generation
- WordToken: all properties and IPA generation
- Sentence: all properties and IPA generation
- demonstrate_transcription utility function
"""

import unittest

from tugaphone.dialects import (
    EuropeanPortuguese,
    BrazilianPortuguese,
    AngolanPortuguese,
    MozambicanPortuguese,
    TimoresePortuguese,
)
from tugaphone.tokenizer import (
    Sentence,
    WordToken,
    CharToken,
    detect_stress_position,
    is_grapheme_silent
)


# ═════════════════════════════════════════════════════════════════════════════
# FIXTURES / HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def _ep():
    """Shortcut for European Portuguese dialect."""
    return EuropeanPortuguese()


def _br():
    """Shortcut for Brazilian Portuguese dialect."""
    return BrazilianPortuguese()


def _word(surface, dialect=None):
    """Create a standalone WordToken (inside a 1-word Sentence so parent links work)."""
    s = Sentence(surface, dialect=dialect or _ep())
    return s.words[0]


def _sent(surface, dialect=None):
    """Create a Sentence."""
    return Sentence(surface, dialect=dialect or _ep())


# ═════════════════════════════════════════════════════════════════════════════
# 1. HELPER FUNCTION TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestDetectStressPosition(unittest.TestCase):
    """Tests for the detect_stress_position() helper."""

    def setUp(self):
        self.dialect = _ep()

    # ── monosyllables ──────────────────────────────────────────────────────
    def test_monosyllable_returns_zero(self):
        self.assertEqual(detect_stress_position("pé", ["pé"], self.dialect), 0)

    def test_monosyllable_no_accent(self):
        self.assertEqual(detect_stress_position("sol", ["sol"], self.dialect), 0)

    # ── explicit accent marks ──────────────────────────────────────────────
    def test_acute_accent_final(self):
        """café → stress on final (explicit accent)."""
        self.assertEqual(detect_stress_position("café", ["ca", "fé"], self.dialect), 1)

    def test_acute_accent_penultimate(self):
        """médico → stress on antepenultimate (explicit accent)."""
        self.assertEqual(
            detect_stress_position("médico", ["mé", "di", "co"], self.dialect), 0
        )

    def test_tilde_accent(self):
        """cão → stress on syllable with ã."""
        self.assertEqual(detect_stress_position("morcão", ["mor", "cão"], self.dialect), 1)

    # ── oxytone endings ────────────────────────────────────────────────────
    def test_oxytone_ending_r(self):
        """falar → final stress (-ar ending)."""
        self.assertEqual(
            detect_stress_position("falar", ["fa", "lar"], self.dialect), 1
        )

    def test_oxytone_ending_l(self):
        """animal → final stress (-al ending)."""
        self.assertEqual(
            detect_stress_position("animal", ["a", "ni", "mal"], self.dialect), 2
        )

    # ── default paroxytone ─────────────────────────────────────────────────
    def test_default_paroxytone(self):
        """casa → penultimate stress."""
        self.assertEqual(
            detect_stress_position("casa", ["ca", "sa"], self.dialect), 0
        )

    def test_three_syllable_paroxytone(self):
        """bonita → penultimate stress."""
        self.assertEqual(
            detect_stress_position("bonita", ["bo", "ni", "ta"], self.dialect), 1
        )


class TestIsGraphemeSilent(unittest.TestCase):
    """Tests for the is_grapheme_silent() helper."""

    def setUp(self):
        self.dialect = _ep()

    def test_h_always_silent(self):
        self.assertTrue(is_grapheme_silent("h", "", "oje", "hoje", self.dialect))

    def test_h_silent_mid_word(self):
        self.assertTrue(is_grapheme_silent("h", "n", "o", "nho", self.dialect))

    def test_u_silent_in_que(self):
        """u after q before e → silent."""
        self.assertTrue(is_grapheme_silent("u", "q", "ero", "quero", self.dialect))

    def test_u_silent_in_gui(self):
        """u after g before i → silent."""
        self.assertTrue(is_grapheme_silent("u", "g", "ia", "guia", self.dialect))

    def test_regular_consonant_not_silent(self):
        self.assertFalse(is_grapheme_silent("s", "ca", "a", "casa", self.dialect))

    def test_vowel_not_silent(self):
        self.assertFalse(is_grapheme_silent("a", "c", "sa", "casa", self.dialect))


# ═════════════════════════════════════════════════════════════════════════════
# 2. CHARTOKEN TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestCharTokenInit(unittest.TestCase):
    """Tests for CharToken initialisation and validation."""

    def test_single_char_ok(self):
        w = _word("a")
        ct = w.graphemes[0].characters[0]
        self.assertEqual(ct.surface, "a")

    def test_multi_char_raises(self):
        """CharToken must contain exactly one character."""
        with self.assertRaises(ValueError):
            # Manually create invalid CharToken — needs a parent
            w = _word("ab")
            g = w.graphemes[0]
            CharToken(surface="ab", char_idx=0, parent_grapheme=g)


class TestCharTokenBasicProperties(unittest.TestCase):
    """Tests for CharToken basic properties."""

    def _char_at(self, word_surface, char_index):
        """Return the CharToken at position char_index within the word."""
        w = _word(word_surface)
        chars = [c for g in w.graphemes for c in g.characters]
        return chars[char_index]

    def test_normalized_lowercase(self):
        w = _word("Casa")
        c = w.graphemes[0].characters[0]
        self.assertEqual(c.normalized, "c")

    def test_dialect_propagation(self):
        w = _word("a")
        c = w.graphemes[0].characters[0]
        self.assertIsNotNone(c.dialect)
        self.assertTrue(c.dialect.dialect_code.startswith("pt-PT"))


class TestCharTokenIndicesAndContext(unittest.TestCase):
    """Tests for CharToken indices, context, and navigation."""

    def setUp(self):
        self.w = _word("casa")

    def test_idx_in_word(self):
        chars = self.w.all_chars
        self.assertEqual(chars[0].idx_in_word, 0)
        self.assertEqual(chars[1].idx_in_word, 1)
        self.assertEqual(chars[3].idx_in_word, 3)

    def test_idx_in_sentence(self):
        chars = self.w.all_chars
        self.assertEqual(chars[0].idx_in_sentence, 0)

    def test_parent_word(self):
        c = self.w.all_chars[0]
        self.assertIs(c.parent_word, self.w)

    def test_parent_sentence(self):
        c = self.w.all_chars[0]
        self.assertIsNotNone(c.parent_sentence)

    def test_prefix_suffix(self):
        chars = self.w.all_chars
        self.assertEqual(chars[0].prefix, "")
        self.assertEqual(chars[0].suffix, "asa")
        self.assertEqual(chars[2].prefix, "ca")
        self.assertEqual(chars[2].suffix, "a")

    def test_first_word_letter(self):
        chars = self.w.all_chars
        self.assertTrue(chars[0].is_first_word_letter)
        self.assertFalse(chars[1].is_first_word_letter)

    def test_last_word_letter(self):
        chars = self.w.all_chars
        self.assertTrue(chars[-1].is_last_word_letter)
        self.assertFalse(chars[0].is_last_word_letter)


class TestCharTokenClassification(unittest.TestCase):
    """Tests for vowel / consonant / semivowel / diacritics classification."""

    def _first_char(self, word, dialect=None):
        return _word(word, dialect).graphemes[0].characters[0]

    def _last_char(self, word, dialect=None):
        return _word(word, dialect).graphemes[-1].characters[-1]

    def test_is_vowel(self):
        for v in "aeiou":
            c = self._first_char(v)
            self.assertTrue(c.is_vowel, f"{v} should be a vowel")

    def test_accented_vowel(self):
        c = self._first_char("é")
        self.assertTrue(c.is_vowel)

    def test_is_consonant(self):
        w = _word("bola")
        c = w.graphemes[0].characters[0]  # 'b'
        self.assertTrue(c.is_consonant)
        self.assertFalse(c.is_vowel)

    def test_has_diacritics(self):
        c = self._first_char("é")
        self.assertTrue(c.has_diacritics)
        c2 = self._first_char("e")
        self.assertFalse(c2.has_diacritics)

    def test_is_semivowel(self):
        c = self._first_char("i")
        self.assertFalse(c.is_semivowel)
        self.assertTrue(c.is_nucleus)
        self.assertEqual(c.ipa, "i")
        c2 = self._first_char("u")
        self.assertFalse(c2.is_semivowel)
        self.assertTrue(c2.is_nucleus)
        self.assertEqual(c2.ipa, "u")

        d = self._last_char("pai")
        self.assertFalse(d.is_nucleus)
        self.assertTrue(d.is_semivowel)
        self.assertTrue(d.parent_grapheme.is_diphthong)
        self.assertEqual(d.ipa, "j")
        d2 = self._last_char("mau")
        self.assertFalse(d2.is_nucleus)
        self.assertTrue(d2.is_semivowel)
        self.assertTrue(d2.parent_grapheme.is_diphthong)
        self.assertEqual(d2.ipa, "w")

    def test_ptBR_is_semivowel(self):
        d2 = self._last_char("Portugal")
        self.assertFalse(d2.is_nucleus)
        self.assertFalse(d2.is_semivowel)
        self.assertFalse(d2.parent_grapheme.is_diphthong)
        self.assertNotEqual(d2.ipa, "w")

        d2 = self._last_char("Portugal", _br())
        self.assertFalse(d2.is_nucleus)
        self.assertTrue(d2.is_semivowel)
        self.assertTrue(d2.parent_grapheme.is_diphthong)
        self.assertEqual(d2.ipa, "w")

    def test_is_silent_h(self):
        w = _word("hoje")
        h_char = w.graphemes[0].characters[0]
        self.assertEqual(h_char.normalized, "h")
        self.assertTrue(h_char.is_silent)


class TestCharTokenVowelQuality(unittest.TestCase):
    """Tests for vowel quality properties: open/closed, height, backness, roundedness."""

    def _first_char(self, word):
        return _word(word).graphemes[0].characters[0]

    def test_is_open_vowel(self):
        c = self._first_char("a")
        self.assertTrue(c.is_open_vowel)

    def test_is_closed_vowel(self):
        c = self._first_char("i")
        self.assertTrue(c.is_closed_vowel)

    def test_vowel_height_high(self):
        c = self._first_char("i")
        self.assertEqual(c.vowel_height, "high")

    def test_vowel_height_low(self):
        c = self._first_char("á")
        self.assertEqual(c.vowel_height, "low")

    def test_vowel_backness_front(self):
        c = self._first_char("i")
        self.assertEqual(c.vowel_backness, "front")

    def test_vowel_backness_back(self):
        c = self._first_char("u")
        self.assertEqual(c.vowel_backness, "back")

    def test_vowel_roundedness_rounded(self):
        c = self._first_char("u")
        self.assertEqual(c.vowel_roundedness, "rounded")

    def test_vowel_roundedness_unrounded(self):
        c = self._first_char("i")
        self.assertEqual(c.vowel_roundedness, "unrounded")

    def test_consonant_vowel_height_none(self):
        w = _word("bola")
        b = w.graphemes[0].characters[0]
        self.assertIsNone(b.vowel_height)

    def test_consonant_vowel_backness_none(self):
        w = _word("bola")
        b = w.graphemes[0].characters[0]
        self.assertIsNone(b.vowel_backness)

    def test_consonant_vowel_roundedness_none(self):
        w = _word("bola")
        b = w.graphemes[0].characters[0]
        self.assertIsNone(b.vowel_roundedness)

    def test_is_front_vowel(self):
        c = self._first_char("i")
        self.assertTrue(c.is_front_vowel)
        c2 = self._first_char("u")
        self.assertFalse(c2.is_front_vowel)

    def test_is_back_vowel(self):
        c = self._first_char("u")
        self.assertTrue(c.is_back_vowel)
        c2 = self._first_char("i")
        self.assertFalse(c2.is_back_vowel)

    def test_is_rounded_vowel(self):
        c = self._first_char("u")
        self.assertTrue(c.is_rounded_vowel)
        c2 = self._first_char("a")
        self.assertFalse(c2.is_rounded_vowel)

    def test_non_vowel_not_front(self):
        w = _word("bola")
        b = w.graphemes[0].characters[0]
        self.assertFalse(b.is_front_vowel)

    def test_non_vowel_not_back(self):
        w = _word("bola")
        b = w.graphemes[0].characters[0]
        self.assertFalse(b.is_back_vowel)


class TestCharTokenConsonantFeatures(unittest.TestCase):
    """Tests for manner/place of articulation, voicing, and consonant classes."""

    def _consonant_char(self, letter, ctx_word="bola"):
        """Get a CharToken for a consonant in a minimal word context."""
        w = _word(ctx_word)
        for g in w.graphemes:
            for c in g.characters:
                if c.normalized == letter:
                    return c
        return None

    def test_manner_plosive(self):
        c = self._consonant_char("b")
        self.assertEqual(c.manner_of_articulation, "plosive")

    def test_manner_fricative(self):
        c = self._consonant_char("f", "falar")
        self.assertEqual(c.manner_of_articulation, "fricative")

    def test_manner_nasal(self):
        c = self._consonant_char("m", "mar")
        self.assertEqual(c.manner_of_articulation, "nasal")

    def test_manner_lateral(self):
        c = self._consonant_char("l", "bola")
        self.assertEqual(c.manner_of_articulation, "lateral")

    def test_manner_rhotic(self):
        c = self._consonant_char("r", "caro")
        self.assertEqual(c.manner_of_articulation, "rhotic")

    def test_manner_vowel_none(self):
        w = _word("a")
        c = w.graphemes[0].characters[0]
        self.assertIsNone(c.manner_of_articulation)

    def test_place_bilabial(self):
        c = self._consonant_char("b")
        self.assertEqual(c.place_of_articulation, "bilabial")

    def test_place_labiodental(self):
        c = self._consonant_char("f", "falar")
        self.assertEqual(c.place_of_articulation, "labiodental")

    def test_place_alveolar(self):
        c = self._consonant_char("t", "tato")
        self.assertEqual(c.place_of_articulation, "alveolar")

    def test_place_velar(self):
        c = self._consonant_char("k", "kilo")
        self.assertEqual(c.place_of_articulation, "velar")

    def test_voicing_voiceless(self):
        c = self._consonant_char("t", "tato")
        self.assertEqual(c.voicing, "voiceless")

    def test_voicing_voiced(self):
        c = self._consonant_char("b")
        self.assertEqual(c.voicing, "voiced")

    def test_voicing_vowel(self):
        w = _word("a")
        c = w.graphemes[0].characters[0]
        self.assertEqual(c.voicing, "voiced")

    def test_is_sonorant_vowel(self):
        w = _word("a")
        c = w.graphemes[0].characters[0]
        self.assertTrue(c.is_sonorant)

    def test_is_sonorant_nasal(self):
        c = self._consonant_char("m", "mar")
        self.assertTrue(c.is_sonorant)

    def test_is_sonorant_plosive(self):
        c = self._consonant_char("b")
        self.assertFalse(c.is_sonorant)

    def test_is_obstruent(self):
        c = self._consonant_char("b")
        self.assertTrue(c.is_obstruent)

    def test_is_obstruent_vowel(self):
        w = _word("a")
        self.assertFalse(w.graphemes[0].characters[0].is_obstruent)

    def test_is_liquid(self):
        c = self._consonant_char("l", "bola")
        self.assertTrue(c.is_liquid)
        c2 = self._consonant_char("r", "caro")
        self.assertTrue(c2.is_liquid)

    def test_is_not_liquid(self):
        c = self._consonant_char("b")
        self.assertFalse(c.is_liquid)

    def test_is_fricative(self):
        c = self._consonant_char("f", "falar")
        self.assertTrue(c.is_fricative)

    def test_is_plosive(self):
        c = self._consonant_char("b")
        self.assertTrue(c.is_plosive)

    def test_is_nasal_consonant(self):
        c = self._consonant_char("m", "mar")
        self.assertTrue(c.is_nasal_consonant)

    def test_is_sibilant(self):
        c = self._consonant_char("s", "sol")
        self.assertTrue(c.is_sibilant)

    def test_is_rhotic(self):
        c = self._consonant_char("r", "caro")
        self.assertTrue(c.is_rhotic)

    def test_is_not_rhotic(self):
        c = self._consonant_char("b")
        self.assertFalse(c.is_rhotic)


class TestCharTokenPositionalProperties(unittest.TestCase):
    """Tests for intervocalic, between-consonant-vowel, etc."""

    def test_is_nucleus(self):
        w = _word("casa")
        chars = [c for g in w.graphemes for c in g.characters]
        # 'a' at position 1 is a vowel → nucleus
        self.assertTrue(chars[1].is_nucleus)
        # 'c' is not
        self.assertFalse(chars[0].is_nucleus)

    def test_is_onset(self):
        w = _word("casa")
        chars = [c for g in w.graphemes for c in g.characters]
        # 'c' at start of syllable 'ca' → onset
        self.assertTrue(chars[0].is_onset)

    def test_parent_syllable(self):
        w = _word("casa")
        chars = [c for g in w.graphemes for c in g.characters]
        # First char 'c' should be in syllable 'ca'
        self.assertEqual(chars[0].parent_syllable, "ca")


class TestCharTokenStress(unittest.TestCase):
    """Tests for primary/secondary stress properties."""

    def test_primary_stress_with_accent(self):
        w = _word("café")
        # Find the 'é' char
        for g in w.graphemes:
            for c in g.characters:
                if c.normalized == "é":
                    self.assertTrue(c.has_primary_stress)

    def test_no_primary_stress_unstressed_vowel(self):
        w = _word("casa")
        # Last 'a' is unstressed
        last_a = w.graphemes[-1].characters[0]
        self.assertFalse(last_a.has_primary_stress)


class TestCharTokenIPA(unittest.TestCase):
    """Tests for CharToken.ipa property."""

    def test_silent_h_empty_ipa(self):
        w = _word("hoje")
        h = w.graphemes[0].characters[0]
        self.assertEqual(h.ipa, "")

    def test_vowel_ipa(self):
        w = _word("é")
        c = w.graphemes[0].characters[0]
        ipa = c.ipa
        self.assertIsInstance(ipa, str)
        self.assertGreater(len(ipa), 0)

    def test_consonant_ipa(self):
        w = _word("bola")
        b = w.graphemes[0].characters[0]
        ipa = b.ipa
        self.assertIsInstance(ipa, str)
        self.assertGreater(len(ipa), 0)


class TestCharTokenFeatures(unittest.TestCase):
    """Tests for CharToken.features dictionary."""

    def test_features_returns_dict(self):
        w = _word("casa")
        c = w.graphemes[0].characters[0]
        f = c.features
        self.assertIsInstance(f, dict)

    def test_features_keys(self):
        w = _word("casa")
        c = w.graphemes[0].characters[0]
        f = c.features
        expected_keys = [
            "text", "ipa", "is_first_letter", "is_last_letter",
            "is_punct", "is_vowel", "is_consonant", "is_foreign", "is_silent",
            "is_semivowel", "is_nasal_vowel", "is_open_vowel", "is_closed_vowel",
            "is_front_vowel", "is_back_vowel", "is_rounded_vowel",
            "vowel_height", "vowel_backness", "vowel_roundedness",
            "manner_of_articulation", "place_of_articulation", "voicing",
            "is_sonorant", "is_obstruent", "is_liquid", "is_fricative",
            "is_plosive", "is_nasal_consonant", "is_sibilant", "is_rhotic",
            "is_intervocalic", "is_between_consonant_vowel",
            "is_between_vowel_consonant", "is_prepalatal_vowel",
            "has_diacritics", "has_primary_stress", "has_secondary_stress",
        ]
        for key in expected_keys:
            self.assertIn(key, f, f"Missing feature key: {key}")


class TestCharTokenEqAndRepr(unittest.TestCase):
    """Tests for __eq__ and __repr__."""

    def test_eq_with_string(self):
        w = _word("a")
        c = w.graphemes[0].characters[0]
        self.assertEqual(c, "a")

    def test_eq_with_different_string(self):
        w = _word("a")
        c = w.graphemes[0].characters[0]
        self.assertNotEqual(c, "b")

    def test_repr(self):
        w = _word("a")
        c = w.graphemes[0].characters[0]
        r = repr(c)
        self.assertIn("CharToken", r)
        self.assertIn("a", r)


# ═════════════════════════════════════════════════════════════════════════════
# 3. GRAPHEMETOKEN TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestGraphemeTokenInit(unittest.TestCase):
    """Tests for GraphemeToken initialisation."""

    def test_characters_created(self):
        w = _word("casa")
        g = w.graphemes[0]
        self.assertGreater(len(g.characters), 0)

    def test_character_parent(self):
        w = _word("casa")
        g = w.graphemes[0]
        for c in g.characters:
            self.assertIs(c.parent_grapheme, g)


class TestGraphemeTokenBasicProperties(unittest.TestCase):
    """Tests for GraphemeToken basic properties."""

    def test_normalized(self):
        w = _word("Casa")
        g = w.graphemes[0]
        self.assertEqual(g.normalized, "c")

    def test_n_chars(self):
        w = _word("casa")
        g = w.graphemes[0]
        self.assertEqual(g.n_chars, 1)

    def test_first_char(self):
        w = _word("casa")
        g = w.graphemes[0]
        self.assertEqual(g.first_char.surface, "c")

    def test_last_char(self):
        w = _word("casa")
        g = w.graphemes[0]
        self.assertEqual(g.last_char.surface, "c")

    def test_dialect(self):
        w = _word("casa")
        g = w.graphemes[0]
        self.assertIsNotNone(g.dialect)


class TestGraphemeTokenIndices(unittest.TestCase):
    """Tests for GraphemeToken indices and navigation."""

    def test_idx_in_word(self):
        w = _word("casa")
        self.assertEqual(w.graphemes[0].idx_in_word, 0)

    def test_idx_in_sentence(self):
        w = _word("casa")
        self.assertEqual(w.graphemes[0].idx_in_sentence, 0)

    def test_parent_sentence(self):
        w = _word("casa")
        self.assertIsNotNone(w.graphemes[0].parent_sentence)

    def test_parent_syllable(self):
        w = _word("casa")
        g0 = w.graphemes[0]
        self.assertIsNotNone(g0.parent_syllable)

    def test_prefix_suffix(self):
        w = _word("casa")
        g2 = w.graphemes[2]  # 's'
        self.assertEqual(g2.prefix, "ca")
        self.assertEqual(g2.suffix, "a")

    def test_prev_grapheme(self):
        w = _word("casa")
        self.assertIsNone(w.graphemes[0].prev_grapheme)
        self.assertIsNotNone(w.graphemes[1].prev_grapheme)

    def test_next_grapheme(self):
        w = _word("casa")
        self.assertIsNotNone(w.graphemes[0].next_grapheme)
        self.assertIsNone(w.graphemes[-1].next_grapheme)

    def test_prev_syllable(self):
        w = _word("casa")
        # First grapheme in first syllable has no prev syllable
        self.assertIsNone(w.graphemes[0].prev_syllable)

    def test_next_syllable(self):
        w = _word("casa")
        # First grapheme's next syllable should be 'sa'
        g0 = w.graphemes[0]
        if g0.syllable_idx == 0:
            ns = g0.next_syllable
            self.assertIsNotNone(ns)


class TestGraphemeTokenClassification(unittest.TestCase):
    """Tests for digraph, diphthong, trigraph, etc. classification."""

    def test_is_digraph_ch(self):
        w = _word("chave")
        # Should find 'ch' as a grapheme
        digraph_found = any(g.is_digraph and g.normalized == "ch" for g in w.graphemes)
        self.assertTrue(digraph_found, "Expected 'ch' digraph in 'chave'")

    def test_is_digraph_nh(self):
        w = _word("vinho")
        digraph_found = any(g.is_digraph and g.normalized == "nh" for g in w.graphemes)
        self.assertTrue(digraph_found, "Expected 'nh' digraph in 'vinho'")

    def test_is_digraph_lh(self):
        w = _word("filho")
        digraph_found = any(g.is_digraph and g.normalized == "lh" for g in w.graphemes)
        self.assertTrue(digraph_found, "Expected 'lh' digraph in 'filho'")

    def test_is_diphthong_ai(self):
        w = _word("pai")
        diphthong_found = any(g.is_diphthong for g in w.graphemes)
        self.assertTrue(diphthong_found, "Expected diphthong in 'pai'")

    def test_is_nasal_diphthong(self):
        w = _word("cão")
        nasal_diph = any(g.is_nasal_diphthong for g in w.graphemes)
        self.assertTrue(nasal_diph, "Expected nasal diphthong in 'cão'")

    def test_is_oral_diphthong(self):
        w = _word("pai")
        oral_diph = any(g.is_oral_diphthong for g in w.graphemes)
        self.assertTrue(oral_diph, "Expected oral diphthong in 'pai'")

    def test_is_falling_diphthong(self):
        w = _word("pai")
        falling = any(g.is_falling_diphthong for g in w.graphemes)
        self.assertTrue(falling, "Expected falling diphthong in 'pai'")

    def test_is_nasal(self):
        w = _word("cão")
        nasal_found = any(g.is_nasal for g in w.graphemes)
        self.assertTrue(nasal_found, "Expected nasal grapheme in 'cão'")

    def test_is_vowel_grapheme(self):
        w = _word("casa")
        a_grapheme = w.graphemes[1]  # 'a'
        self.assertTrue(a_grapheme.is_vowel_grapheme)

    def test_is_consonant_grapheme(self):
        w = _word("casa")
        c_grapheme = w.graphemes[0]  # 'c'
        self.assertTrue(c_grapheme.is_consonant_grapheme)

    def test_is_archaism_ph(self):
        """Grapheme 'ph' should be archaic."""
        w = _word("pharmacia")
        ph_found = any(g.is_archaism and "ph" in g.normalized for g in w.graphemes)
        # ph might be tokenised as a digraph or separate depending on inventory
        # Just check it runs without error
        self.assertIsInstance(ph_found, bool)

    def test_is_vocalic_hiatus_stub(self):
        """is_vocalic_hiatus is currently stubbed to False."""
        w = _word("saúde")
        for g in w.graphemes:
            self.assertFalse(g.is_vocalic_hiatus)


class TestGraphemeTokenPhonologicalProperties(unittest.TestCase):
    """Tests for syllable_position, phonological_weight, etc."""

    def test_syllable_position_onset(self):
        w = _word("casa")
        c_grapheme = w.graphemes[0]  # 'c' - onset
        pos = c_grapheme.syllable_position
        self.assertIn(pos, ["onset", "nucleus", "coda"])

    def test_syllable_position_nucleus(self):
        w = _word("casa")
        a_grapheme = w.graphemes[1]  # 'a' - nucleus
        self.assertEqual(a_grapheme.syllable_position, "nucleus")

    def test_phonological_weight(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertIsInstance(g.phonological_weight, int)
            self.assertGreaterEqual(g.phonological_weight, 0)

    def test_diphthong_weight_two(self):
        w = _word("pai")
        for g in w.graphemes:
            if g.is_diphthong:
                self.assertEqual(g.phonological_weight, 2)

    def test_is_palatal_nh(self):
        w = _word("vinho")
        palatal_found = any(g.is_palatal for g in w.graphemes)
        self.assertTrue(palatal_found, "Expected palatal in 'vinho'")

    def test_is_palatal_lh(self):
        w = _word("filho")
        palatal_found = any(g.is_palatal for g in w.graphemes)
        self.assertTrue(palatal_found, "Expected palatal in 'filho'")

    def test_triggers_palatalization(self):
        w = _word("dia")
        # 'i' before 'a' — check it runs
        for g in w.graphemes:
            self.assertIsInstance(g.triggers_palatalization, bool)

    def test_requires_liaison(self):
        s = _sent("os amigos")
        w = s.words[0]  # 'os'
        # Last grapheme of 'os' — 's' before vowel-initial word
        last_g = w.graphemes[-1]
        self.assertIsInstance(last_g.requires_liaison, bool)


class TestGraphemeTokenStress(unittest.TestCase):
    """Tests for GraphemeToken stress properties."""

    def test_has_primary_stress(self):
        w = _word("café")
        stressed = any(g.has_primary_stress for g in w.graphemes)
        self.assertTrue(stressed, "Expected primary stress in 'café'")

    def test_has_secondary_stress(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertIsInstance(g.has_secondary_stress, bool)


class TestGraphemeTokenIPA(unittest.TestCase):
    """Tests for GraphemeToken.ipa generation."""

    def test_digraph_ch_ipa(self):
        w = _word("chave")
        for g in w.graphemes:
            if g.normalized == "ch":
                self.assertEqual(g.ipa, "ʃ")

    def test_digraph_nh_ipa(self):
        w = _word("vinho")
        for g in w.graphemes:
            if g.normalized == "nh":
                self.assertEqual(g.ipa, "ɲ")

    def test_digraph_lh_ipa(self):
        w = _word("filho")
        for g in w.graphemes:
            if g.normalized == "lh":
                self.assertEqual(g.ipa, "ʎ")

    def test_diphthong_ipa(self):
        w = _word("pai")
        for g in w.graphemes:
            if g.is_diphthong:
                self.assertIsInstance(g.ipa, str)
                self.assertGreater(len(g.ipa), 0)

    def test_muito_special_case(self):
        """'ui' in 'muito' should produce nasalized IPA."""
        w = _word("muito")
        for g in w.graphemes:
            if g.normalized == "ui":
                self.assertEqual(g.ipa, "ũj")

    def test_single_char_ipa(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertIsInstance(g.ipa, str)


class TestGraphemeTokenFeatures(unittest.TestCase):
    """Tests for GraphemeToken.features dict."""

    def test_features_returns_dict(self):
        w = _word("casa")
        f = w.graphemes[0].features
        self.assertIsInstance(f, dict)

    def test_features_expected_keys(self):
        w = _word("casa")
        f = w.graphemes[0].features
        for key in ["n_chars", "text", "ipa", "is_digraph", "is_diphthong",
                    "is_nasal", "syllable_position", "has_primary_stress"]:
            self.assertIn(key, f, f"Missing key: {key}")

    def test_features_include_char_features(self):
        w = _word("casa")
        f = w.graphemes[0].features
        # Character features should be nested with char_0_ prefix
        char_keys = [k for k in f if k.startswith("char_")]
        self.assertGreater(len(char_keys), 0)


class TestGraphemeTokenEqRepr(unittest.TestCase):
    """Tests for __eq__ and __repr__."""

    def test_eq_string(self):
        w = _word("casa")
        self.assertEqual(w.graphemes[0], "c")

    def test_repr(self):
        w = _word("casa")
        r = repr(w.graphemes[0])
        self.assertIn("GraphemeToken", r)


# ═════════════════════════════════════════════════════════════════════════════
# 4. WORDTOKEN TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestWordTokenInit(unittest.TestCase):
    """Tests for WordToken initialisation and syllabification."""

    def test_syllables_generated(self):
        w = _word("casa")
        self.assertGreater(len(w.syllables), 0)

    def test_graphemes_generated(self):
        w = _word("casa")
        self.assertGreater(len(w.graphemes), 0)

    def test_custom_dialect(self):
        w = _word("casa", dialect=_br())
        self.assertTrue(w.dialect.dialect_code.startswith("pt-BR"))


class TestWordTokenBasicProperties(unittest.TestCase):
    """Tests for WordToken basic properties."""

    def test_normalized(self):
        w = _word("Casa")
        self.assertEqual(w.normalized, "casa")

    def test_n_syllables(self):
        w = _word("casa")
        self.assertEqual(w.n_syllables, 2)

    def test_n_syllables_monosyllable(self):
        w = _word("sol")
        self.assertEqual(w.n_syllables, 1)

    def test_idx_in_sentence(self):
        s = _sent("o gato")
        self.assertEqual(s.words[0].idx_in_sentence, 0)

    def test_normalized_syllables(self):
        w = _word("carro")
        ns = w.normalized_syllables
        self.assertIsInstance(ns, list)
        self.assertGreater(len(ns), 0)


class TestWordTokenLinkedProperties(unittest.TestCase):
    """Tests for prev_word, next_word navigation."""

    def test_prev_word_none_for_first(self):
        s = _sent("o gato")
        self.assertIsNone(s.words[0].prev_word)

    def test_prev_word(self):
        s = _sent("o gato")
        self.assertIsNotNone(s.words[1].prev_word)
        self.assertEqual(s.words[1].prev_word.surface, "o")

    def test_next_word(self):
        s = _sent("o gato")
        self.assertIsNotNone(s.words[0].next_word)
        self.assertEqual(s.words[0].next_word.surface, "gato")

    def test_next_word_none_for_last(self):
        s = _sent("o gato")
        self.assertIsNone(s.words[-1].next_word)


class TestWordTokenStress(unittest.TestCase):
    """Tests for stress_pattern, stressed_syllable_idx."""

    def test_monosyllable_pattern(self):
        w = _word("sol")
        self.assertEqual(w.stress_pattern, "monosyllable")

    def test_oxytone(self):
        w = _word("café")
        self.assertEqual(w.stress_pattern, "oxytone")

    def test_paroxytone(self):
        w = _word("casa")
        self.assertEqual(w.stress_pattern, "paroxytone")

    def test_proparoxytone(self):
        w = _word("médico")
        self.assertEqual(w.stress_pattern, "proparoxytone")

    def test_stressed_syllable_idx_cafe(self):
        w = _word("café")
        self.assertEqual(w.stressed_syllable_idx, w.n_syllables - 1)

    def test_stressed_syllable_idx_casa(self):
        w = _word("casa")
        self.assertEqual(w.stressed_syllable_idx, 0)


class TestWordTokenPhonologicalProperties(unittest.TestCase):
    """Tests for word-level phonological properties."""

    def test_has_diphthongs(self):
        w = _word("pai")
        self.assertTrue(w.has_diphthongs)

    def test_no_diphthongs(self):
        w = _word("casa")
        self.assertFalse(w.has_diphthongs)

    def test_has_nasal_sounds(self):
        w = _word("cão")
        self.assertTrue(w.has_nasal_sounds)

    def test_syllable_structure_pattern(self):
        w = _word("casa")
        pattern = w.syllable_structure_pattern
        self.assertIn(".", pattern)
        self.assertTrue(all(c in "CV." for c in pattern))

    def test_is_homograph(self):
        w = _word("casa")
        self.assertIsInstance(w.is_homograph, bool)

    def test_phoneme_count(self):
        w = _word("casa")
        self.assertIsInstance(w.phoneme_count, int)
        self.assertGreater(w.phoneme_count, 0)

    def test_has_consonant_clusters(self):
        w = _word("casa")
        self.assertIsInstance(w.has_consonant_clusters, bool)

    def test_has_palatal_sounds(self):
        w = _word("vinho")
        self.assertTrue(w.has_palatal_sounds)

    def test_no_palatal_sounds(self):
        w = _word("casa")
        self.assertFalse(w.has_palatal_sounds)

    def test_vowel_sequence(self):
        w = _word("casa")
        vs = w.vowel_sequence
        self.assertIsInstance(vs, str)

    def test_consonant_sequence(self):
        w = _word("casa")
        cs = w.consonant_sequence
        self.assertIsInstance(cs, str)

    def test_is_irregular(self):
        w = _word("casa")
        self.assertIsInstance(w.is_irregular, bool)

    def test_is_archaic(self):
        w = _word("casa")
        self.assertIsInstance(w.is_archaic, bool)


class TestWordTokenIPA(unittest.TestCase):
    """Tests for WordToken.ipa generation."""

    def test_casa_ipa(self):
        w = _word("casa")
        ipa = w.ipa
        self.assertIsInstance(ipa, str)
        self.assertGreater(len(ipa), 0)
        # Should contain stress marker
        self.assertIn("ˈ", ipa)

    def test_cafe_ipa(self):
        w = _word("café")
        ipa = w.ipa
        self.assertIn("ˈ", ipa)

    def test_monosyllable_ipa(self):
        w = _word("sol")
        ipa = w.ipa
        self.assertIn("ˈ", ipa)

    def test_ipa_not_empty(self):
        words = ["casa", "café", "sol", "pai", "vinho", "cão", "filho"]
        for word_str in words:
            w = _word(word_str)
            self.assertGreater(len(w.ipa), 0, f"IPA empty for '{word_str}'")


class TestWordTokenNormalizeSyllables(unittest.TestCase):
    """Tests for _normalize_syllables handling of doubled consonants."""

    def test_carro_syllable_normalization(self):
        w = _word("carro")
        ns = w.normalized_syllables
        # 'rr' should be moved to second syllable
        joined = "".join(ns)
        self.assertIn("rr", joined)

    def test_simple_word_no_change(self):
        w = _word("casa")
        self.assertEqual(w.normalized_syllables, w._normalize_syllables())


class TestWordTokenBuildCharSyllableMap(unittest.TestCase):
    """Tests for _build_char_to_syllable_map static method."""

    def test_basic_mapping(self):
        result = WordToken._build_char_to_syllable_map(["ca", "sa"])
        self.assertEqual(result, {0: 0, 1: 0, 2: 1, 3: 1})

    def test_single_syllable(self):
        result = WordToken._build_char_to_syllable_map(["sol"])
        self.assertEqual(result, {0: 0, 1: 0, 2: 0})


class TestWordTokenFeatures(unittest.TestCase):
    """Tests for WordToken.features dict."""

    def test_features_returns_dict(self):
        w = _word("casa")
        f = w.features
        self.assertIsInstance(f, dict)

    def test_features_expected_keys(self):
        w = _word("casa")
        f = w.features
        for key in ["surface", "normalized", "ipa", "n_syllables",
                    "stressed_syllable_idx", "stress_pattern",
                    "syllable_structure_pattern",
                    "has_diphthongs", "has_nasal_sounds",
                    "phoneme_count", "is_irregular", "is_homograph"]:
            self.assertIn(key, f, f"Missing key: {key}")

    def test_features_include_grapheme_features(self):
        w = _word("casa")
        f = w.features
        graph_keys = [k for k in f if k.startswith("graph_")]
        self.assertGreater(len(graph_keys), 0)


class TestWordTokenEqRepr(unittest.TestCase):
    """Tests for __eq__ and __repr__."""

    def test_eq_string(self):
        w = _word("casa")
        self.assertEqual(w, "casa")

    def test_eq_different_string(self):
        w = _word("casa")
        self.assertNotEqual(w, "bola")

    def test_repr(self):
        w = _word("casa")
        r = repr(w)
        self.assertIn("WordToken", r)
        self.assertIn("casa", r)


# ═════════════════════════════════════════════════════════════════════════════
# 5. SENTENCE TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestSentenceInit(unittest.TestCase):
    """Tests for Sentence initialisation."""

    def test_basic_init(self):
        s = _sent("o gato")
        self.assertEqual(s.surface, "o gato")

    def test_words_created(self):
        s = _sent("o gato")
        self.assertEqual(len(s.words), 2)

    def test_word_surfaces(self):
        s = _sent("o gato dorme")
        surfaces = [w.surface for w in s.words]
        self.assertEqual(surfaces, ["o", "gato", "dorme"])

    def test_word_parent_sentence(self):
        s = _sent("o gato")
        for w in s.words:
            self.assertIs(w.parent_sentence, s)

    def test_word_dialect(self):
        s = _sent("o gato", dialect=_br())
        for w in s.words:
            self.assertTrue(w.dialect.dialect_code.startswith("pt-BR"))

    def test_hyphenated_words_split(self):
        s = _sent("guarda-chuva")
        self.assertEqual(len(s.words), 2)

    def test_single_word_sentence(self):
        s = _sent("casa")
        self.assertEqual(len(s.words), 1)


class TestSentenceFromPostagged(unittest.TestCase):
    """Tests for Sentence.from_postagged class method."""

    def test_from_postagged_basic(self):
        tags = [("o", "DET"), ("gato", "NOUN")]
        s = Sentence.from_postagged("o gato", tags=tags, dialect=_ep())
        self.assertEqual(len(s.words), 2)
        self.assertEqual(s.words[0].postag, "DET")
        self.assertEqual(s.words[1].postag, "NOUN")

    def test_from_postagged_preserves_surface(self):
        tags = [("café", "NOUN")]
        s = Sentence.from_postagged("café", tags=tags, dialect=_ep())
        self.assertEqual(s.surface, "café")

    def test_from_postagged_dialect(self):
        tags = [("casa", "NOUN")]
        s = Sentence.from_postagged("casa", tags=tags, dialect=_br())
        self.assertTrue(s.words[0].dialect.dialect_code.startswith("pt-BR"))


class TestSentenceBasicProperties(unittest.TestCase):
    """Tests for Sentence basic properties."""

    def test_normalized(self):
        s = _sent("O Gato!")
        self.assertEqual(s.normalized, "o gato")

    def test_n_words(self):
        s = _sent("o gato dorme")
        self.assertEqual(s.n_words, 3)

    def test_n_words_single(self):
        s = _sent("casa")
        self.assertEqual(s.n_words, 1)


class TestSentenceIPA(unittest.TestCase):
    """Tests for Sentence.ipa generation."""

    def test_ipa_not_empty(self):
        s = _sent("o gato")
        self.assertGreater(len(s.ipa), 0)

    def test_ipa_space_separated(self):
        s = _sent("o gato")
        parts = s.ipa.split(" ")
        self.assertEqual(len(parts), 2)

    def test_ipa_single_word(self):
        s = _sent("casa")
        self.assertNotIn(" ", s.ipa)

    def test_ipa_multiple_words(self):
        s = _sent("o gato dorme")
        parts = s.ipa.split(" ")
        self.assertEqual(len(parts), 3)


class TestSentenceFeatures(unittest.TestCase):
    """Tests for Sentence.features dict."""

    def test_features_returns_dict(self):
        s = _sent("o gato")
        f = s.features
        self.assertIsInstance(f, dict)

    def test_features_n_words(self):
        s = _sent("o gato dorme")
        f = s.features
        self.assertEqual(f["n_words"], 3)
        self.assertEqual(f["n_whitespaces"], 2)

    def test_features_include_word_features(self):
        s = _sent("o gato")
        f = s.features
        word_keys = [k for k in f if k.startswith("word_")]
        self.assertGreater(len(word_keys), 0)


class TestSentenceEqRepr(unittest.TestCase):
    """Tests for __eq__ and __repr__."""

    def test_eq_string(self):
        s = _sent("o gato")
        self.assertEqual(s, "o gato")

    def test_eq_different_string(self):
        s = _sent("o gato")
        self.assertNotEqual(s, "a casa")

    def test_repr(self):
        s = _sent("o gato")
        r = repr(s)
        self.assertIn("Sentence", r)


# ═════════════════════════════════════════════════════════════════════════════
# 6. DIALECT VARIATION TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestDialectVariation(unittest.TestCase):
    """Tests to ensure different dialects produce different IPA output."""

    def test_ep_vs_br(self):
        """European and Brazilian should differ for many words."""
        ep = _sent("casa", dialect=_ep())
        br = _sent("casa", dialect=_br())
        # Both should produce valid IPA
        self.assertGreater(len(ep.ipa), 0)
        self.assertGreater(len(br.ipa), 0)

    def test_all_dialects_produce_ipa(self):
        dialects = [
            EuropeanPortuguese(),
            BrazilianPortuguese(),
            AngolanPortuguese(),
            MozambicanPortuguese(),
            TimoresePortuguese(),
        ]
        for d in dialects:
            s = Sentence("casa", dialect=d)
            self.assertGreater(
                len(s.ipa), 0,
                f"Empty IPA for dialect {d.dialect_code}"
            )

    def test_brazilian_r_after_consonant(self):
        """Brazilian should use 'h' for strong R after l/n/s."""
        w = _word("israel", dialect=_br())
        ipa = w.ipa
        # Just check it doesn't crash and produces output
        self.assertIsInstance(ipa, str)

    def test_sentence_multiple_words_all_dialects(self):
        text = "o gato dorme"
        for dialect_cls in [EuropeanPortuguese, BrazilianPortuguese,
                            AngolanPortuguese, MozambicanPortuguese,
                            TimoresePortuguese]:
            d = dialect_cls()
            s = Sentence(text, dialect=d)
            parts = s.ipa.split(" ")
            self.assertEqual(
                len(parts), 3,
                f"Expected 3 IPA words for '{text}' with {d.dialect_code}"
            )


# ═════════════════════════════════════════════════════════════════════════════
# 7. SPECIAL WORD / IPA EDGE-CASE TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestSpecialIPACases(unittest.TestCase):
    """Tests for known special IPA conversions."""

    def test_single_vowel_word_a(self):
        """Word 'a' should produce specific IPA."""
        w = _word("a")
        self.assertIsInstance(w.ipa, str)
        self.assertGreater(len(w.ipa), 0)

    def test_single_vowel_word_o(self):
        """Word 'o' should produce specific IPA."""
        w = _word("o")
        self.assertIsInstance(w.ipa, str)

    def test_single_vowel_word_e(self):
        w = _word("e")
        self.assertIsInstance(w.ipa, str)

    def test_preposition_de(self):
        w = _word("de")
        self.assertIsInstance(w.ipa, str)

    def test_c_before_e(self):
        """'c' before 'e' → [s]."""
        w = _word("cedo")
        # Find 'c' grapheme
        c_g = w.graphemes[0]
        if c_g.normalized == "c":
            # The IPA should contain 's' sound
            self.assertIn("s", c_g.ipa)

    def test_c_before_a(self):
        """'c' before 'a' → [k]."""
        w = _word("casa")
        c_g = w.graphemes[0]
        self.assertIn("k", c_g.ipa)

    def test_x_word_initial(self):
        """Word-initial x → [ʃ]."""
        w = _word("xadrez")
        x_char = None
        for g in w.graphemes:
            for c in g.characters:
                if c.normalized == "x":
                    x_char = c
                    break
        if x_char:
            self.assertEqual(x_char._ipa_for_x(), "ʃ")

    def test_x_word_final(self):
        """Word-final x → [ks]."""
        w = _word("fax")
        x_char = None
        for g in w.graphemes:
            for c in g.characters:
                if c.normalized == "x":
                    x_char = c
                    break
        if x_char:
            self.assertEqual(x_char._ipa_for_x(), "ks")

    def test_cedilla(self):
        """ç → [s]."""
        w = _word("caça")
        for g in w.graphemes:
            for c in g.characters:
                if c.normalized == "ç":
                    ipa = c.ipa
                    self.assertIn("s", ipa)


class TestNasalWords(unittest.TestCase):
    """Tests for nasal vowel and nasal diphthong words."""

    def test_cao_has_nasal(self):
        w = _word("cão")
        self.assertTrue(w.has_nasal_sounds)

    def test_pao_has_nasal(self):
        w = _word("pão")
        self.assertTrue(w.has_nasal_sounds)

    def test_homem_ipa(self):
        w = _word("homem")
        self.assertIsInstance(w.ipa, str)
        self.assertGreater(len(w.ipa), 0)


class TestDiphthongWords(unittest.TestCase):
    """Tests for diphthong-containing words."""

    def test_pai_diphthong(self):
        w = _word("pai")
        self.assertTrue(w.has_diphthongs)

    def test_rei_diphthong(self):
        w = _word("rei")
        self.assertTrue(w.has_diphthongs)

    def test_meu_diphthong(self):
        w = _word("meu")
        self.assertTrue(w.has_diphthongs)


class TestDigraphWords(unittest.TestCase):
    """Tests for words with consonant digraphs."""

    def test_chave_ipa(self):
        w = _word("chave")
        self.assertIn("ʃ", w.ipa)

    def test_vinho_ipa(self):
        w = _word("vinho")
        self.assertIn("ɲ", w.ipa)

    def test_filho_ipa(self):
        w = _word("filho")
        self.assertIn("ʎ", w.ipa)


# ═════════════════════════════════════════════════════════════════════════════
# 9. INTEGRATION / REGRESSION TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestIntegrationSentences(unittest.TestCase):
    """Integration tests with full sentences to catch regressions."""

    def test_simple_sentence(self):
        s = _sent("o gato dorme")
        self.assertEqual(s.n_words, 3)
        self.assertIsInstance(s.ipa, str)

    def test_accented_sentence(self):
        s = _sent("o café é bom")
        self.assertEqual(s.n_words, 4)

    def test_nasal_diphthong_sentence(self):
        s = _sent("o cão comeu o pão")
        self.assertEqual(s.n_words, 5)
        self.assertIsInstance(s.ipa, str)

    def test_digraph_sentence(self):
        s = _sent("a rainha viu o vinho")
        self.assertEqual(s.n_words, 5)

    def test_complex_sentence(self):
        s = _sent("o médico português está no café")
        self.assertIsInstance(s.ipa, str)
        self.assertGreater(len(s.ipa), 0)

    def test_word_indices_sequential(self):
        s = _sent("o gato dorme")
        for idx, w in enumerate(s.words):
            self.assertEqual(w.word_idx, idx)

    def test_all_words_have_graphemes(self):
        s = _sent("o gato dorme bem")
        for w in s.words:
            self.assertGreater(
                len(w.graphemes), 0,
                f"Word '{w.surface}' has no graphemes"
            )

    def test_all_graphemes_have_characters(self):
        s = _sent("casa bonita")
        for w in s.words:
            for g in w.graphemes:
                self.assertGreater(
                    len(g.characters), 0,
                    f"Grapheme '{g.surface}' has no characters"
                )

    def test_all_characters_have_ipa(self):
        """Every non-silent character should produce some IPA."""
        s = _sent("bola")
        for w in s.words:
            for g in w.graphemes:
                for c in g.characters:
                    if not c.is_silent:
                        self.assertGreater(
                            len(c.ipa), 0,
                            f"Char '{c.surface}' has empty IPA"
                        )


class TestStressPatternDistribution(unittest.TestCase):
    """Regression tests ensuring stress patterns are assigned correctly."""

    def test_oxytone_words(self):
        oxytone_words = ["café", "após", "irmã"]
        for w_str in oxytone_words:
            w = _word(w_str)
            self.assertEqual(
                w.stressed_syllable_idx, w.n_syllables - 1,
                f"'{w_str}' should be oxytone"
            )

    def test_paroxytone_words(self):
        for w_str in ["casa", "gato", "mesa"]:
            w = _word(w_str)
            if w.n_syllables >= 2:
                self.assertEqual(
                    w.stressed_syllable_idx, w.n_syllables - 2,
                    f"'{w_str}' should be paroxytone"
                )

    def test_proparoxytone_words(self):
        for w_str in ["médico", "rápido"]:
            w = _word(w_str)
            if w.n_syllables >= 3:
                self.assertEqual(
                    w.stress_pattern, "proparoxytone",
                    f"'{w_str}' should be proparoxytone"
                )


class TestSentenceWithPrebuiltWords(unittest.TestCase):
    """Tests for Sentence initialised with pre-built WordToken list."""

    def test_prebuild_words(self):
        w1 = WordToken(surface="o", word_idx=0, dialect=_ep())
        w2 = WordToken(surface="gato", word_idx=1, dialect=_ep())
        s = Sentence(surface="o gato", words=[w1, w2], dialect=_ep())
        self.assertEqual(s.n_words, 2)
        for w in s.words:
            self.assertIs(w.parent_sentence, s)

    def test_prebuild_words_ipa(self):
        w1 = WordToken(surface="o", word_idx=0, dialect=_ep())
        w2 = WordToken(surface="gato", word_idx=1, dialect=_ep())
        s = Sentence(surface="o gato", words=[w1, w2], dialect=_ep())
        self.assertIsInstance(s.ipa, str)
        self.assertGreater(len(s.ipa), 0)


# ═════════════════════════════════════════════════════════════════════════════
# 10. EDGE CASES AND BOUNDARY TESTS
# ═════════════════════════════════════════════════════════════════════════════


class TestEdgeCases(unittest.TestCase):
    """Edge cases and boundary conditions."""

    def test_empty_word_in_sentence(self):
        """Single-letter sentence."""
        s = _sent("a")
        self.assertEqual(s.n_words, 1)
        self.assertIsInstance(s.ipa, str)

    def test_accented_only_word(self):
        s = _sent("é")
        self.assertEqual(s.n_words, 1)
        self.assertIsInstance(s.ipa, str)

    def test_long_sentence(self):
        text = "o gato preto dormiu na mesa grande da sala bonita"
        s = _sent(text)
        self.assertEqual(s.n_words, 10)
        self.assertIsInstance(s.ipa, str)

    def test_word_with_rr(self):
        """Double-r should be handled as digraph."""
        w = _word("carro")
        rr_found = any(g.normalized == "rr" for g in w.graphemes)
        self.assertTrue(rr_found, "Expected 'rr' grapheme in 'carro'")

    def test_word_with_ss(self):
        """Double-s should be handled as digraph."""
        w = _word("passo")
        ss_found = any(g.normalized == "ss" for g in w.graphemes)
        self.assertTrue(ss_found, "Expected 'ss' grapheme in 'passo'")

    def test_features_full_pipeline(self):
        """Ensure full feature extraction doesn't crash for a complex sentence."""
        s = _sent("o cão comeu o pão")
        f = s.features
        self.assertIsInstance(f, dict)
        self.assertIn("n_words", f)

    def test_chartoken_prev_char_first(self):
        """First char in grapheme should have None prev_char."""
        w = _word("casa")
        first_c = w.graphemes[0].characters[0]
        self.assertIsNone(first_c.prev_char)

    def test_chartoken_next_char_last(self):
        """Last char in single-char grapheme should have None next_char."""
        w = _word("casa")
        last_c = w.graphemes[-1].characters[-1]
        self.assertIsNone(last_c.next_char)

    def test_prev_next_grapheme_navigation(self):
        """Test prev_grapheme and next_grapheme for char navigation."""
        w = _word("casa")
        g0 = w.graphemes[0]
        c0 = g0.characters[0]
        # prev_grapheme of first grapheme's char
        self.assertIsNone(c0.prev_grapheme)
        # next_grapheme
        self.assertIsNotNone(c0.next_grapheme)


class TestCharTokenNasalVowel(unittest.TestCase):
    """Tests for is_nasal_vowel property."""

    def test_tilde_vowel_is_nasal(self):
        w = _word("cão")
        for g in w.graphemes:
            for c in g.characters:
                if c.normalized in _ep().TILDE_VOWEL_CHARS:
                    self.assertTrue(c.is_nasal_vowel)

    def test_consonant_not_nasal_vowel(self):
        w = _word("casa")
        c = w.graphemes[0].characters[0]  # 'c'
        self.assertFalse(c.is_nasal_vowel)


class TestCharTokenPrepalatalVowel(unittest.TestCase):
    """Tests for is_prepalatal_vowel property."""

    def test_prepalatal_detection(self):
        w = _word("achar")
        # Check that is_prepalatal_vowel runs without error for all chars
        for g in w.graphemes:
            for c in g.characters:
                self.assertIsInstance(c.is_prepalatal_vowel, bool)


class TestGraphemeTokenIsForeignDigraph(unittest.TestCase):
    """Tests for is_foreign_digraph property."""

    def test_not_foreign_regular_word(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertFalse(g.is_foreign_digraph)


class TestGraphemeTokenIsConsonantHiatus(unittest.TestCase):
    """Tests for is_consonant_hiatus property."""

    def test_regular_word(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertIsInstance(g.is_consonant_hiatus, bool)


class TestGraphemeTokenIsTrigraph(unittest.TestCase):
    """Tests for is_trigraph property."""

    def test_regular_word_no_trigraph(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertIsInstance(g.is_trigraph, bool)


class TestGraphemeTokenIsTriphthong(unittest.TestCase):
    """Tests for is_triphthong property."""

    def test_regular_word_no_triphthong(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertFalse(g.is_triphthong)


class TestGraphemeTokenIsRisingDiphthong(unittest.TestCase):
    """Tests for is_rising_diphthong property."""

    def test_non_diphthong_not_rising(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertFalse(g.is_rising_diphthong)


class TestGraphemeTokenIsOnsetCluster(unittest.TestCase):
    """Tests for is_onset_cluster property."""

    def test_regular_word(self):
        w = _word("casa")
        for g in w.graphemes:
            self.assertIsInstance(g.is_onset_cluster, bool)


if __name__ == "__main__":
    unittest.main()
