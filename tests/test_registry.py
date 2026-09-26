"""Dialect registry: code resolution, listing and phonemizer integration.

A dialect is an orthography2ipa lect code. Every pinned IPA string was captured
by running the phonemizer.
"""

import pytest

from tugaphone.registry import (normalize_dialect_code, resolve_lect,
                                resolve_dialect, lexicon_region, list_dialects,
                                get_dialect_inventory)


class TestNormalization:
    def test_casing(self):
        assert normalize_dialect_code("PT-pt-X-PORTO") == "pt-PT-x-porto"

    def test_major(self):
        assert normalize_dialect_code("pt-br") == "pt-BR"

    def test_bare(self):
        assert normalize_dialect_code("PT") == "pt"

    def test_private_use_subtags_stay_lowercase(self):
        assert normalize_dialect_code("pt-BR-X-SP") == "pt-BR-x-sp"


class TestResolution:
    @pytest.mark.parametrize("code", [
        "pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL",
        "pt-PT-x-lisbon", "pt-PT-x-porto", "pt-BR-x-sp", "pt-BR-x-rj",
        "pt-CV", "pt-GW", "pt-ST", "pt-MO", "pt-UY",
    ])
    def test_canonical_codes_resolve_to_self(self, code):
        assert resolve_lect(code) == code

    @pytest.mark.parametrize("alias,lect", [
        ("pt", "pt-PT"),
        ("pt-PT-x-lisboa", "pt-PT-x-lisbon"),
        ("pt-BR-x-rio", "pt-BR-x-rj"),
        ("pt-BR-x-rio-janeiro", "pt-BR-x-rj"),
        ("pt-BR-x-sao-paulo", "pt-BR-x-sp"),
        ("pt-PT-x-norte", "pt-PT-x-minho"),
        ("pt-PT-x-tras-os-montes", "pt-PT-x-trasosmontes"),
        ("pt-PT-x-transmontano", "pt-PT-x-trasosmontes"),
        ("pt-PT-x-central", "pt-PT-x-coimbra"),
        ("pt-PT-x-azores", "pt-PT-x-acores"),
    ])
    def test_legacy_aliases(self, alias, lect):
        assert resolve_lect(alias) == lect

    def test_case_insensitive(self):
        assert resolve_lect("PT-BR") == "pt-BR"
        assert resolve_lect("pt-pt-X-PORTO") == "pt-PT-x-porto"

    def test_unknown_private_use_falls_back_to_parent(self):
        assert resolve_lect("pt-PT-x-unknown") == "pt-PT"

    def test_unknown_language_falls_back_to_default(self):
        assert resolve_lect("fr") == "pt-PT"
        assert resolve_lect("") == "pt-PT"


class TestLexiconRegion:
    @pytest.mark.parametrize("lect,region", [
        ("pt-PT", "lbx"), ("pt-PT-x-lisbon", "lbx"),
        ("pt-BR", "rjx"), ("pt-BR-x-sp", "spx"),
        ("pt-AO", "lda"), ("pt-MZ", "mpx"), ("pt-TL", "dli"),
    ])
    def test_lexicon_overlaid_lects(self, lect, region):
        assert lexicon_region(lect) == region

    @pytest.mark.parametrize("lect", [
        "pt-PT-x-porto", "pt-PT-x-madeira", "pt-BR-x-caipira", "pt-CV",
    ])
    def test_pure_lattice_lects_have_no_lexicon(self, lect):
        # Overlaying the Lisbon lexicon on a Porto lect would overwrite the
        # spec's phonology with Lisbon forms — these lects are lattice-only.
        assert lexicon_region(lect) is None


class TestListDialects:
    def test_covers_the_portuguese_family(self):
        codes = list_dialects()
        assert codes == sorted(codes)
        for expected in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL",
                         "pt-PT-x-porto", "pt-BR-x-sp", "pt-CV"]:
            assert expected in codes
        # aliases are not canonical codes
        assert "pt" not in codes and "pt-PT-x-lisboa" not in codes

    def test_plugin_exposes_registry(self):
        from tugaphone.plugin import TugaphoneG2PPlugin
        assert TugaphoneG2PPlugin().language_codes == list_dialects()

    def test_resolve_dialect_deprecated(self):
        with pytest.deprecated_call():
            assert resolve_dialect("pt-BR") == "pt-BR"


@pytest.fixture(scope="module")
def pho():
    from tugaphone import TugaPhonemizer
    return TugaPhonemizer()


class TestPhonemizerIntegration:
    SENTENCE = "Choveu muito ontem à noite."

    @pytest.mark.parametrize("code,expected", [
        # "à" is a function word: the pan-pt clitic rule destresses it while
        # keeping its open /a/ quality (proclitic to "noite").
        ("pt-PT", "ʃuˈvew ˈmũjtu ˈõtɐ̃j a ˈnojt"),
        ("pt-BR", "ʃoˈvew ˈmwĩtʊ ˈõtẽj a ˈnojtʃɪ"),
        ("pt-AO", "ʃoˈvew ˈmũjntʊ ˈõntẽj a ˈnojtɨ"),
        ("pt-MZ", "ʃoˈvew ˈmũjtu ˈõtẽj a ˈnɔjtɨ"),
        ("pt-TL", "ʃoˈvew ˈmujtʊ ˈõntɐ̃j a ˈnojtʰ"),
        # Porto "ontem" carries the nasal -em diphthong [ɐ̃j̃].
        ("pt-PT-x-porto", "ʃuˈbew ˈmujtu ˈwõtɐ̃j̃ a ˈnojtɨ"),
    ])
    def test_dialect_output(self, pho, code, expected):
        import unicodedata
        got = unicodedata.normalize("NFC", pho.phonemize_sentence(self.SENTENCE, code))
        assert got == unicodedata.normalize("NFC", expected)

    def test_lexicon_overlay_differs_across_regions(self, pho):
        assert pho.phonemize_sentence("noite", "pt-BR") == "ˈnojtʃɪ"
        assert pho.phonemize_sentence("noite", "pt-BR-x-sp") == "ˈnojti"

    def test_regional_dialect_kwarg_deprecated_and_ignored(self, pho):
        with pytest.deprecated_call():
            out = pho.phonemize_sentence("gato", "pt-PT", regional_dialect=object())
        assert out == pho.phonemize_sentence("gato", "pt-PT")

    def test_unrecognised_tag_matches_default(self, pho):
        assert (pho.phonemize_sentence(self.SENTENCE, "pt-PT-x-nowhere")
                == pho.phonemize_sentence(self.SENTENCE, "pt-PT"))
