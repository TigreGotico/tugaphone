"""Dialect registry: code resolution, listing and phonemizer integration.

A dialect is an orthography2ipa lect code. Every pinned IPA string was captured
by running the phonemizer.
"""

import pytest
from orthography2ipa import resolve

from tugaphone.registry import (normalize_dialect_code, resolve_lect,
                                resolve_dialect, PACKAGED_LEXICON_LECTS, lexicon_region,
                                list_dialects,
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
        assert resolve_lect(alias) == resolve(lect)

    @pytest.mark.parametrize("code", [
        "pt-PT-x-trasosmontes", "pt-BR-x-fluminense", "roa-x-galaicopt",
        "ext-PT-x-barrancos",
    ])
    def test_a_key_orthography2ipa_renamed_still_names_its_dialect(self, code):
        # orthography2ipa keeps the old key of a renamed spec as an exact
        # alias, so the old key must not fall back to the parent variety.
        assert resolve_lect(code) == resolve(code)
        assert resolve(code) in list_dialects()

    def test_case_insensitive(self):
        assert resolve_lect("PT-BR") == "pt-BR"
        assert resolve_lect("pt-pt-X-PORTO") == "pt-PT-x-porto"

    def test_unknown_private_use_falls_back_to_parent(self):
        assert resolve_lect("pt-PT-x-unknown") == "pt-PT"

    def test_unknown_language_falls_back_to_default(self):
        assert resolve_lect("fr") == "pt-PT"
        assert resolve_lect("") == "pt-PT"


class TestPackagedLexiconLects:
    def test_only_the_national_lects_take_a_packaged_lexicon(self):
        # A sub-lect would take its parent's forms over its own spec's phonology.
        assert PACKAGED_LEXICON_LECTS == {"pt-PT", "pt-BR"}

    @pytest.mark.parametrize("lect", ["pt-PT", "pt-PT-x-lisbon", "pt-BR", "pt-TL"])
    def test_lexicon_region_is_deprecated_and_names_no_region(self, lect):
        from tugaphone.version import VERSION_MAJOR

        with pytest.warns(DeprecationWarning, match=f"removed in tugaphone {VERSION_MAJOR + 1}.0.0"):
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
        # No word of the sentence is in a lexicon, so each lect gives the
        # output of the bare orthography2ipa G2P for that lect.
        ("pt-PT", "ʃuˈvew ˈmũj̃tu ˈõtɐ̃j̃ a ˈnojtɨ"),
        ("pt-BR", "ʃoˈvew ˈmũj̃tu ˈõtẽj̃ a ˈnojt͡ʃi"),
        ("pt-AO", "ʃoˈvew ˈmũj̃tʊ ˈõtẽj̃ a ˈnojtɨ"),
        ("pt-MZ", "ʃoˈvew ˈmũj̃tu ˈõtẽ a ˈnojte"),
        ("pt-TL", "ʃoˈvew ˈmũj̃to ˈõtẽj̃ a ˈnojte"),
        # Porto "ontem" keeps the close-mid nucleus of the nasal -em diphthong [ẽj̃].
        ("pt-PT-x-porto", "ʃuˈbew ˈmũj̃tu ˈwõtẽj̃ a ˈnojtɨ"),
    ])
    def test_dialect_output(self, pho, code, expected):
        import unicodedata
        got = unicodedata.normalize("NFC", pho.phonemize_sentence(self.SENTENCE, code))
        assert got == unicodedata.normalize("NFC", expected)

    def test_regional_dialect_kwarg_deprecated_and_ignored(self, pho):
        with pytest.deprecated_call():
            out = pho.phonemize_sentence("gato", "pt-PT", regional_dialect=object())
        assert out == pho.phonemize_sentence("gato", "pt-PT")

    def test_unrecognised_tag_matches_default(self, pho):
        assert (pho.phonemize_sentence(self.SENTENCE, "pt-PT-x-nowhere")
                == pho.phonemize_sentence(self.SENTENCE, "pt-PT"))
