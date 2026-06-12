"""Dialect registry: code resolution, listing and phonemizer integration.

Every pinned IPA string in this file was captured by running the phonemizer.
"""

import pytest

from tugaphone.dialects import (EuropeanPortuguese, LisbonPortuguese,
                                BrazilianPortuguese, RioJaneiroPortuguese,
                                SaoPauloPortuguese, AngolanPortuguese,
                                MozambicanPortuguese, TimoresePortuguese)
from tugaphone.regional import (NorthernDialect, PortoDialect, MinhoDialect,
                                BragaDialect, FamalicaoDialect, FafeDialect,
                                TrasMontanoDialect, CoimbraDialect,
                                AlentejoDialect, AlgarveDialect,
                                MadeiraDialect, AzoresDialect)
from tugaphone.registry import (DIALECT_REGISTRY, DialectEntry,
                                normalize_dialect_code, resolve_dialect,
                                get_dialect_inventory, get_regional_transforms,
                                list_dialects)


class TestNormalization:
    def test_casing(self):
        assert normalize_dialect_code("PT-pt-X-PORTO") == "pt-PT-x-porto"

    def test_major(self):
        assert normalize_dialect_code("pt-br") == "pt-BR"

    def test_bare(self):
        assert normalize_dialect_code("PT") == "pt"


class TestResolution:
    @pytest.mark.parametrize("code,inventory", [
        ("pt-PT", EuropeanPortuguese),
        ("pt-BR", BrazilianPortuguese),
        ("pt-AO", AngolanPortuguese),
        ("pt-MZ", MozambicanPortuguese),
        ("pt-TL", TimoresePortuguese),
        ("pt-PT-x-lisbon", LisbonPortuguese),
        ("pt-BR-x-rio-janeiro", RioJaneiroPortuguese),
        ("pt-BR-x-sao-paulo", SaoPauloPortuguese),
    ])
    def test_inventory_codes(self, code, inventory):
        entry = resolve_dialect(code)
        assert entry.code == code
        assert entry.inventory is inventory
        assert isinstance(get_dialect_inventory(code), inventory)

    @pytest.mark.parametrize("code,preset", [
        ("pt-PT-x-north", NorthernDialect),
        ("pt-PT-x-porto", PortoDialect),
        ("pt-PT-x-minho", MinhoDialect),
        ("pt-PT-x-braga", BragaDialect),
        ("pt-PT-x-famalicao", FamalicaoDialect),
        ("pt-PT-x-fafe", FafeDialect),
        ("pt-PT-x-transmontano", TrasMontanoDialect),
        ("pt-PT-x-coimbra", CoimbraDialect),
        ("pt-PT-x-alentejo", AlentejoDialect),
        ("pt-PT-x-algarve", AlgarveDialect),
        ("pt-PT-x-madeira", MadeiraDialect),
        ("pt-PT-x-azores", AzoresDialect),
    ])
    def test_preset_codes(self, code, preset):
        entry = resolve_dialect(code)
        assert entry.transforms is preset
        assert entry.inventory is EuropeanPortuguese
        assert get_regional_transforms(code) is preset

    @pytest.mark.parametrize("alias,canonical", [
        ("pt", "pt-PT"),
        ("pt-PT-x-lisboa", "pt-PT-x-lisbon"),
        ("pt-BR-x-rio", "pt-BR-x-rio-janeiro"),
        ("pt-PT-x-norte", "pt-PT-x-north"),
        ("pt-PT-x-tras-os-montes", "pt-PT-x-transmontano"),
        ("pt-PT-x-central", "pt-PT-x-coimbra"),
        ("pt-PT-x-acores", "pt-PT-x-azores"),
    ])
    def test_aliases(self, alias, canonical):
        assert resolve_dialect(alias).code == canonical

    def test_case_insensitive(self):
        assert resolve_dialect("PT-BR").inventory is BrazilianPortuguese
        assert resolve_dialect("pt-pt-X-PORTO").transforms is PortoDialect

    def test_unknown_private_use_falls_back_to_parent(self):
        entry = resolve_dialect("pt-PT-x-unknown")
        assert entry.code == "pt-PT"
        assert entry.transforms is None

    def test_unknown_language_falls_back_to_default(self):
        assert resolve_dialect("fr").code == "pt-PT"
        assert resolve_dialect("").code == "pt-PT"

    def test_majors_have_no_preset(self):
        for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
            assert get_regional_transforms(code) is None

    def test_fresh_inventory_per_resolution(self):
        assert get_dialect_inventory("pt-PT") is not get_dialect_inventory("pt-PT")


class TestListDialects:
    def test_sorted_canonical_no_aliases(self):
        codes = list_dialects()
        assert codes == sorted(codes)
        assert "pt-PT" in codes and "pt-PT-x-porto" in codes
        assert "pt" not in codes and "pt-PT-x-lisboa" not in codes
        assert len(codes) == len(DIALECT_REGISTRY)

    def test_plugin_exposes_registry(self):
        from tugaphone.plugin import TugaphoneG2PPlugin
        assert TugaphoneG2PPlugin().language_codes == list_dialects()

    def test_entries_are_frozen(self):
        entry = resolve_dialect("pt-PT")
        with pytest.raises(Exception):
            entry.code = "other"
        assert isinstance(entry, DialectEntry)


@pytest.fixture(scope="module")
def pho():
    from tugaphone import TugaPhonemizer
    return TugaPhonemizer()


class TestPhonemizerIntegration:
    SENTENCE = "Choveu muito ontem à noite."

    def test_preset_code_equals_manual_kwarg(self, pho):
        via_code = pho.phonemize_sentence(self.SENTENCE, "pt-PT-x-porto")
        via_kwarg = pho.phonemize_sentence(self.SENTENCE, "pt-PT",
                                           regional_dialect=PortoDialect)
        assert via_code == via_kwarg
        assert via_code == "ʃu·ˈbew mˈũj·tu ˈõ·tẽ ˈa nˈoj·tɨ ˈ···"

    def test_explicit_kwarg_overrides_code(self, pho):
        override = pho.phonemize_sentence(self.SENTENCE, "pt-PT-x-porto",
                                          regional_dialect=AzoresDialect)
        pure = pho.phonemize_sentence(self.SENTENCE, "pt-PT-x-azores")
        assert override == pure

    def test_city_inventory_differs_from_major(self, pho):
        assert pho.phonemize_sentence("noite", "pt-BR") == "nˈoj·tʃɪ"
        assert pho.phonemize_sentence("noite", "pt-BR-x-sao-paulo") == "nˈoj·tʃi"

    @pytest.mark.parametrize("code,expected", [
        ("pt-PT", "ʃu·ˈvew mˈũj·tu ˈõ·tẽ ˈa nˈoj·tɨ ˈ···"),
        ("pt-BR", "ʃo·ˈvew mwˈĩ·tʊ ˈõ·tẽ ˈa nˈoj·tʃɪ ˈ···"),
        ("pt-AO", "ʃo·ˈvew mˈũjn·tʊ ˈõ·tẽ ˈa nˈoj·tɨ ˈ···"),
        ("pt-MZ", "ʃu·ˈvew mˈũj·tu ˈõ·tẽ ˈa nˈɔj·tɨ ˈ···"),
        ("pt-TL", "ʃo·ˈvew mˈuj·tʊ ˈõ·tẽ ˈa nˈojtʰ ˈ···"),
    ])
    def test_major_dialect_output_unchanged(self, pho, code, expected):
        assert pho.phonemize_sentence(self.SENTENCE, code) == expected

    def test_unrecognised_tag_matches_default(self, pho):
        assert (pho.phonemize_sentence(self.SENTENCE, "pt-PT-x-nowhere")
                == pho.phonemize_sentence(self.SENTENCE, "pt-PT"))
