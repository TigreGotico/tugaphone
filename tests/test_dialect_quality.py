"""Dialect quality tests.

Each dialect's signature phonological feature is produced by its orthography2ipa
lect spec — the grapheme table and ``allophone_rules`` — reached through the
lect code. These assert the lattice pipeline preserves the documented hallmark
of each variety.
"""
import re
import pytest

from tugaphone import TugaPhonemizer


def strip_markers(s: str) -> str:
    return re.sub(r"[ˈˌ·]", "", s)


@pytest.fixture(scope="module")
def pho():
    return TugaPhonemizer()


def say(pho, word, lect):
    return strip_markers(pho.phonemize_sentence(word, lect))


class TestNorthernSignatures:
    """Northern European Portuguese hallmarks from the lect specs."""

    def test_porto_rising_diphthong_o(self, pho):
        # Cintra 1971:684 "[o] em [wo]"; o2i PT_PORTO_DIPHTHONGISE_O.
        assert "wo" in say(pho, "porto", "pt-PT-x-porto")

    def test_porto_betacism(self, pho):
        # Northern /v/ → [b]; o2i PT_PORTO_BETACISM.
        assert "b" in say(pho, "vaca", "pt-PT-x-porto")
        assert "v" not in say(pho, "vaca", "pt-PT-x-porto")

    def test_trasmontano_ch_affrication(self, pho):
        # <ch> → [tʃ]; o2i pt-PT-x-trasosmontes grapheme delta.
        assert "tʃ" in say(pho, "chaves", "pt-PT-x-trasosmontes")

    def test_trasmontano_apico_alveolar_sibilant(self, pho):
        # Four-sibilant apico-alveolar [s̺]; Cintra's diagnostic isogloss.
        assert "s̺" in say(pho, "chaves", "pt-PT-x-trasosmontes")


class TestBrazilianPhonology:
    def test_t_palatalization_before_i(self, pho):
        assert "tʃ" in say(pho, "tia", "pt-BR")

    def test_d_palatalization_before_i(self, pho):
        assert "dʒ" in say(pho, "dia", "pt-BR")

    def test_final_te_palatalized(self, pho):
        out = say(pho, "abacate", "pt-BR")
        assert "tʃ" in out and "ɪ" in out

    def test_coda_l_vocalization(self, pho):
        assert say(pho, "brasil", "pt-BR").endswith("w")


class TestAfricanAndAsianRhotic:
    @pytest.mark.parametrize("lect", ["pt-AO", "pt-MZ", "pt-TL"])
    def test_no_uvular_r(self, pho, lect):
        out = say(pho, "rua", lect)
        assert "ʁ" not in out and out.startswith("r")


class TestTimoresePhonology:
    def test_unstressed_a_is_schwa(self, pho):
        # Tetum-influenced schwa system.
        assert "ə" in say(pho, "aba", "pt-TL")


class TestInsularPhonology:
    def test_madeira_lateral_palatalisation(self, pho):
        # o2i MAD_L_PALATALISATION.
        assert "ʎ" in say(pho, "quilha", "pt-PT-x-madeira")
