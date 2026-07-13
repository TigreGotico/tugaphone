"""Dialect and regional quality tests.

One gold case per regional preset (testing the preset's documented
signature feature), plus cross-dialect phoneme-level sanity checks.
"""
import re
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.dialects import (
    EuropeanPortuguese,
    BrazilianPortuguese,
    AngolanPortuguese,
    MozambicanPortuguese,
    TimoresePortuguese,
)
from tugaphone.regional import (
    CoimbraDialect,
    MinhoDialect,
    BragaDialect,
    FamalicaoDialect,
    TrasMontanoDialect,
    PortoDialect,
    FafeDialect,
)
from tugaphone.ipa_transforms import (
    retain_ou_diphthong,
    retain_ei_diphthong,
    nasal_vowel_raising,
    open_vowel_preference,
    betacism,
    rhotic_realization,
    palatal_affrication_ch,
    initial_z_devoicing,
    final_nasal_denasalization,
    nasal_diphthongization_e,
    rising_diphthong_o,
    conservative_o_nasal_retention,
    nasal_glide_palatalization,
    epenthetic_j_before_palatal,
)


def strip_markers(s: str) -> str:
    return re.sub(r"[ˈˌ·]", "", s)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pho():
    return TugaPhonemizer()


def phonemize(pho, word, dialect, regional=None):
    return strip_markers(
        pho.phonemize_sentence(word, dialect.dialect_code, regional_dialect=regional)
    )


def rules_only(pho, word, dialect_cls):
    """Phonemize using G2P cascade only (no lexicon lookup)."""
    from tugaphone.tokenizer import Sentence
    d = dialect_cls(IRREGULAR_WORDS={"\x00": ""})
    s = Sentence(word, dialect=d)
    return strip_markers(s.ipa)


# ---------------------------------------------------------------------------
# Regional preset gold cases (one signature feature per preset)
# ---------------------------------------------------------------------------

class TestRegionalPresetsSignatureFeatures:
    """Each test exercises the documented hallmark of its preset."""

    def test_coimbra_ou_diphthong_retained(self, pho):
        """Coimbra retains <ou> as [ow], counteracting Lisbon monophthongization."""
        ep = EuropeanPortuguese()
        out = CoimbraDialect.apply_ipa("touro", "tˈowɾu")
        assert "ow" in out, f"Expected 'ow' in {out!r}"

    def test_minho_vowel_centralization_reduced(self, pho):
        """Minho resists ɨ; centralized /ɨ/ between consonants → [e]: 'bɨtɨ' → 'betɨ'."""
        # The transform only fires when ɨ is flanked by consonants on BOTH sides
        out = MinhoDialect.apply_ipa("bete", "bɨtɨ")
        # First ɨ (between b and t) → e; second ɨ (word-final) is out of scope
        assert out.startswith("be"), f"Expected 'be' at start in {out!r}"

    def test_braga_nasal_glide_palatalized(self, pho):
        """Braga: nasal glide gains palatal [ɲ] appendix — 'mãe' [mˈɐ̃jɲ]."""
        out = BragaDialect.apply_ipa("mãe", "mˈɐ̃j")
        assert "ɲ" in out, f"Expected ɲ appendix in {out!r}"

    def test_famalicao_nasal_o_retention(self, pho):
        """Famalicão: tonic nasalized [ˈɐ̃w] retained as [ˈõ] — 'pão' stays round."""
        out = FamalicaoDialect.apply_ipa("pão", "pˈɐ̃w")
        assert "õ" in out, f"Expected õ in {out!r}"

    def test_trasmontano_ch_affrication(self, pho):
        """Transmontano: <ch> affricated to [tʃ] — 'chaves' [tʃˈavɨʃ]."""
        out = TrasMontanoDialect.apply_ipa("chaves", "ʃˈavɨʃ")
        assert "tʃ" in out, f"Expected tʃ in {out!r}"

    def test_porto_rising_diphthong_o(self, pho):
        """Porto: tonic close [ˈo] → [ˈwo] rising diphthong — 'porto' [pˈwoɾtu]
        (Cintra 1971:684 "[o] em [wo]"; o2i PT_PORTO_DIPHTHONGISE_O)."""
        out = PortoDialect.apply_ipa("porto", "pˈoɾtu")
        assert "wo" in out, f"Expected 'wo' in {out!r}"

    def test_fafe_nasal_diphthongization_e(self, pho):
        """Fafe: /ẽ/ before consonant → [eĩ] — 'gente' [ˈʒẽtɨ] → [ˈʒeĩtɨ]."""
        # The engine produces NFD-decomposed e + combining tilde (U+0303)
        e_tilde_nfd = "ẽ"  # NFD: e + combining tilde
        phonemes = f"ˈʒ{e_tilde_nfd}tɨ"
        out = FafeDialect.apply_ipa("gente", phonemes)
        assert "eĩ" in out, f"Expected eĩ in {out!r}"


# ---------------------------------------------------------------------------
# Cross-dialect phoneme-level sanity checks
# ---------------------------------------------------------------------------

class TestBrazilianPhonology:
    """Key pt-BR phonological features that the rule cascade must implement."""

    def test_t_palatalization_before_i(self, pho):
        """t → tʃ before [i]: 'tia' [ˈtʃia]."""
        out = phonemize(pho, "tia", BrazilianPortuguese())
        assert "tʃ" in out, f"Expected tʃ in {out!r}"

    def test_d_palatalization_before_i(self, pho):
        """d → dʒ before [i]: 'dia' [ˈdʒia]."""
        out = phonemize(pho, "dia", BrazilianPortuguese())
        assert "dʒ" in out, f"Expected dʒ in {out!r}"

    def test_final_te_palatalized(self, pho):
        """Final '-te' → [tʃɪ]: 'abacate' ends in tʃɪ."""
        out = phonemize(pho, "abacate", BrazilianPortuguese())
        assert "tʃ" in out, f"Expected tʃ in {out!r}"
        assert "ɪ" in out, f"Expected final ɪ in {out!r}"

    def test_coda_l_vocalization(self, pho):
        """Coda /l/ → [w]: 'Brasil' [bɾaˈziw]."""
        out = phonemize(pho, "brasil", BrazilianPortuguese())
        assert out.endswith("w"), f"Expected final w in {out!r}"

    def test_unstressed_a_not_reduced(self, pho):
        """Unstressed /a/ stays [a], not reduced to [ɐ]: 'casa' (rules-only) has no ɐ."""
        out = rules_only(pho, "casa", BrazilianPortuguese)
        assert "ɐ" not in out, f"Unexpected ɐ in BR 'casa': {out!r}"

    def test_strong_r_is_h(self, pho):
        """Word-initial strong R → [h]: 'rampa' (rules-only) starts with h."""
        out = rules_only(pho, "rampa", BrazilianPortuguese)
        assert out.startswith("h"), f"Expected initial h in BR 'rampa': {out!r}"


class TestAngolanPhonology:
    """Key pt-AO phonological features."""

    def test_unstressed_a_not_reduced(self, pho):
        """AO: unstressed /a/ stays [a] — Bantu substrate resists reduction (rules-only)."""
        out = rules_only(pho, "casa", AngolanPortuguese)
        assert "ɐ" not in out, f"Unexpected ɐ in AO 'casa': {out!r}"

    def test_no_uvular_r(self, pho):
        """AO: no uvular [ʁ]; word-initial R → alveolar [r]."""
        out = phonemize(pho, "rua", AngolanPortuguese())
        assert "ʁ" not in out, f"Unexpected ʁ in AO 'rua': {out!r}"
        assert out.startswith("r"), f"Expected initial r in AO 'rua': {out!r}"


class TestMozambicanPhonology:
    """Key pt-MZ phonological features."""

    def test_unstressed_e_not_centralized(self, pho):
        """MZ: unstressed /e/ stays [e], not [ɨ]."""
        out = phonemize(pho, "pedir", MozambicanPortuguese())
        assert "ɨ" not in out, f"Unexpected ɨ in MZ 'pedir': {out!r}"

    def test_no_uvular_r(self, pho):
        """MZ: no uvular [ʁ]; word-initial R → alveolar [r]."""
        out = phonemize(pho, "rua", MozambicanPortuguese())
        assert "ʁ" not in out, f"Unexpected ʁ in MZ 'rua': {out!r}"


class TestTimoresePhonology:
    """Key pt-TL phonological features."""

    def test_unstressed_a_is_schwa(self, pho):
        """TL: unstressed /a/ → [ə] (Tetum-influenced schwa system)."""
        out = phonemize(pho, "aba", TimoresePortuguese())
        assert "ə" in out, f"Expected ə in TL 'aba': {out!r}"

    def test_unstressed_e_not_centralized(self, pho):
        """TL: unstressed /e/ stays [e], not [ɨ]."""
        out = phonemize(pho, "pedir", TimoresePortuguese())
        assert "ɨ" not in out, f"Unexpected ɨ in TL 'pedir': {out!r}"

    def test_no_uvular_r(self, pho):
        """TL: no uvular [ʁ]; word-initial R → alveolar [r]."""
        out = phonemize(pho, "rua", TimoresePortuguese())
        assert "ʁ" not in out, f"Unexpected ʁ in TL 'rua': {out!r}"
