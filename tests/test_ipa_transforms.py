"""Regression tests for the IPA post-processing transforms.

Each transform has the signature ``(word: str, phonemes: str) -> str`` and
returns a transformed IPA string. The cases below pin the correctness bugs
#9, #10, #11 and #12 from the project TODO.
"""
from tugaphone.ipa_transforms import (
    retain_ou_diphthong,
    palatal_affrication_ch,
    conservative_o_nasal_retention,
    epenthetic_j_before_palatal,
)


class TestRetainOuDiphthong:
    """Bug #9: the bogus ``'boa' -> 'bˈowɐ'`` fixed mapping is removed; only
    words spelled with an <ou> grapheme get the /ow/ diphthong, and the <ô>
    guard runs first."""

    def test_boa_is_unchanged(self):
        # 'boa' has no <ou> grapheme and must not gain an /ow/ diphthong
        assert retain_ou_diphthong("boa", "bˈoɐ") == "bˈoɐ"

    def test_word_initial_ou_restores_diphthong(self):
        assert retain_ou_diphthong("ouro", "ˈoɾu") == "ˈowɾu"

    def test_ou_elsewhere_promotes_tonic_o(self):
        assert retain_ou_diphthong("pouco", "pˈoku") == "pˈowku"

    def test_circumflex_o_left_unchanged(self):
        # <ô> spellings are genuine monophthongs, never diphthongized
        assert retain_ou_diphthong("pôr", "pˈoɾ") == "pˈoɾ"

    def test_word_without_ou_unchanged(self):
        assert retain_ou_diphthong("gato", "ˈgatu") == "ˈgatu"


class TestPalatalAffricationCh:
    """Bug #11: only the <ch>-derived /ʃ/ is affricated; any other /ʃ/ (e.g. a
    syllable-final /s/ realized as [ʃ] in EP) is left untouched."""

    def test_ch_word_affricates_first_sh_only(self):
        # 'chaves' [ˈʃavɨʃ]: first ʃ from <ch>, final ʃ from coda -s
        assert palatal_affrication_ch("chaves", "ˈʃavɨʃ") == "ˈtʃavɨʃ"

    def test_single_ch_single_sh(self):
        assert palatal_affrication_ch("chave", "ˈʃavɨ") == "ˈtʃavɨ"

    def test_no_ch_no_change(self):
        # 'casas' has a final -s -> [ʃ] but no <ch>; must stay fricative
        assert palatal_affrication_ch("casas", "ˈkazɐʃ") == "ˈkazɐʃ"

    def test_two_ch_affricates_two(self):
        assert palatal_affrication_ch("chichi", "ʃiʃi") == "tʃitʃi"


class TestConservativeONasalRetention:
    """Bug #10: the final-nasal ending is sliced by its matched length, not by
    a hardcoded codepoint count, so combining diacritics do not corrupt the
    output."""

    def test_merged_nasal_diphthong_becomes_o(self):
        assert conservative_o_nasal_retention("pão", "pˈɐ̃w") == "pˈõ"

    def test_espeak_variant_ending(self):
        assert conservative_o_nasal_retention("irmão", "iɾmˈɐ̃ʊ̃") == "iɾmˈõ"

    def test_non_ao_word_unchanged(self):
        assert conservative_o_nasal_retention("gato", "ˈgatu") == "ˈgatu"


class TestEpentheticJBeforePalatal:
    """Bug #12: epenthesis fires on both stressed and unstressed vowels before
    a palatal consonant."""

    def test_unstressed_vowel_triggers(self):
        # 'bolacha' [bulaʃɐ]: unstressed 'a' before ʃ must gain [j]
        assert epenthetic_j_before_palatal("bolacha", "bulaʃɐ") == "bulajʃɐ"

    def test_stressed_vowel_triggers(self):
        assert epenthetic_j_before_palatal("velho", "vˈɛʎu") == "vˈɛjʎu"

    def test_no_double_j(self):
        assert epenthetic_j_before_palatal("x", "vˈajʎu") == "vˈajʎu"

    def test_non_palatal_following_no_change(self):
        assert epenthetic_j_before_palatal("gato", "ˈgatu") == "ˈgatu"
