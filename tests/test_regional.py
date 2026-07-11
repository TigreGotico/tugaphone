"""Regression tests for the regional accent (RegionalTransforms) layer."""
import pytest

from tugaphone.regional import (
    RegionalTransforms,
    CoimbraDialect,
    MinhoDialect,
    BragaDialect,
    FamalicaoDialect,
    TrasMontanoDialect,
    PortoDialect,
    FafeDialect,
    RULE_MAP,
)
from tugaphone.ipa_transforms import rising_diphthong_o

ALL_PRESETS = [
    CoimbraDialect, MinhoDialect, BragaDialect, FamalicaoDialect,
    TrasMontanoDialect, PortoDialect, FafeDialect,
]


class TestAsDict:
    """Bug #8: as_dict must serialize every configured rule (lossless), not
    silently drop rules that lack a name mapping."""

    def test_serializes_all_ipa_rules(self):
        d = PortoDialect.as_dict
        # every rule on the preset must appear in the serialized output
        assert len(d["ipa_rules"]) == len(PortoDialect.ipa_rules)
        assert d["ipa_rules"][0] == "rising_diphthong_o"

    @pytest.mark.parametrize("preset", ALL_PRESETS)
    def test_round_trip_is_lossless(self, preset):
        clone = RegionalTransforms.from_dict(preset.as_dict)
        assert clone.ipa_rules == preset.ipa_rules
        assert clone.morpheme_rules == preset.morpheme_rules

    def test_unmapped_rule_raises_instead_of_dropping(self):
        def bogus_rule(word, phonemes, postag="NOUN"):
            return phonemes

        rt = RegionalTransforms(ipa_rules=[rising_diphthong_o, bogus_rule])
        # the unregistered rule must surface as an error, not vanish silently
        with pytest.raises(ValueError):
            _ = rt.as_dict


class TestFromDict:
    def test_unknown_rule_name_raises(self):
        with pytest.raises(ValueError):
            RegionalTransforms.from_dict({"ipa_rules": ["does_not_exist"]})

    def test_empty_config(self):
        rt = RegionalTransforms.from_dict({})
        assert rt.ipa_rules == []
        assert rt.morpheme_rules == []


class TestApplyIpa:
    def test_porto_applies_rules_in_order(self):
        # rising_diphthong_o turns tonic close ˈo into ˈwo (Cintra 1971:684)
        out = PortoDialect.apply_ipa("porto", "pˈoɾtu")
        assert "ˈwo" in out

    @pytest.mark.parametrize("preset", ALL_PRESETS)
    def test_all_preset_rules_are_registered(self, preset):
        # guards against a preset referencing a rule missing from RULE_MAP
        registered = set(RULE_MAP.values())
        for rule in preset.ipa_rules:
            assert rule in registered, rule.__name__
