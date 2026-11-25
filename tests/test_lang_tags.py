"""Language tags reach a lect through linguatag, in every spelling."""
import warnings

import pytest

from tugaphone import is_supported, resolve_lect
from tugaphone.codeswitch import _contact_engine


@pytest.mark.parametrize("tag,lect", [
    ("pt_PT_x_azores", "pt-PT-x-acores"),
    ("PT_BR_X_FLUMINENSE", "pt-BR-x-fluminen"),
    ("pt-x-porto", "pt-PT-x-porto"),
    ("pt_x_porto", "pt-PT-x-porto"),
    ("  PT-X-PORTO ", "pt-PT-x-porto"),
    ("pt_PT-x-lisboa", "pt-PT-x-lisbon"),
])
def test_a_named_lect_in_any_spelling_resolves_without_a_warning(tag, lect):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert resolve_lect(tag) == lect
    assert is_supported(tag)


@pytest.mark.parametrize("tag,lect", [
    ("pt_BR_x_unknown", "pt-BR"),
    ("pt-US", "pt-BR"),
    ("pt-419", "pt-BR"),
])
def test_an_unnamed_tag_takes_the_nearest_lect_and_warns(tag, lect):
    with pytest.warns(UserWarning, match="is not a tugaphone lect"):
        assert resolve_lect(tag) == lect
    assert not is_supported(tag)


@pytest.mark.parametrize("contact,tag", [
    ("es", "es-ES"), ("fr", "fr-FR"), ("en", "en-GB"),
])
def test_a_contact_language_reads_its_default_region(contact, tag):
    assert _contact_engine(contact).lang == tag


@pytest.mark.xfail(strict=True, reason="TigreGotico/linguatag#69: every private-use subtag drops at once; "
                   "RFC 4647 §3.4 removes one subtag at a time")
def test_an_unnamed_subtag_after_a_lect_keeps_the_lect():
    with pytest.warns(UserWarning, match="is not a tugaphone lect"):
        assert resolve_lect("pt-BR-x-sp-foo") == "pt-BR-x-sp"


@pytest.mark.xfail(strict=True, reason="TigreGotico/tugaphone#346: the alias table reads the whole tag only")
@pytest.mark.parametrize("tag,lect", [
    ("pt-PT-x-lisboa-foo", "pt-PT-x-lisbon"),
    ("pt-BR-x-sao-paulo-foo", "pt-BR-x-sp"),
])
def test_an_unnamed_subtag_after_an_alias_keeps_its_lect(tag, lect):
    with pytest.warns(UserWarning, match="is not a tugaphone lect"):
        assert resolve_lect(tag) == lect


def test_normalize_dialect_code_is_deprecated_and_keeps_its_value():
    from tugaphone.registry import normalize_dialect_code
    with pytest.warns(DeprecationWarning, match="removed in tugaphone"):
        assert normalize_dialect_code("PT-pt-X-PORTO") == "pt-PT-x-porto"
