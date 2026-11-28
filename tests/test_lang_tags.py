"""Language tags reach a lect through linguatag, in every spelling."""
import warnings

import pytest

from linguatag import closest_lang, with_default_region
from orthography2ipa import resolve

from tugaphone import is_supported, resolve_lect
from tugaphone.registry import _ALIASES, list_dialects
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


def test_an_unnamed_subtag_after_a_lect_keeps_the_lect():
    with pytest.warns(UserWarning, match="is not a tugaphone lect"):
        assert resolve_lect("pt-BR-x-sp-foo") == "pt-BR-x-sp"


@pytest.mark.parametrize("tag,lect", [
    ("pt-PT-x-lisboa-foo", "pt-PT-x-lisbon"),
    ("pt-BR-x-sao-paulo-foo", "pt-BR-x-sp"),
])
def test_an_unnamed_subtag_after_an_alias_keeps_its_lect(tag, lect):
    with pytest.warns(UserWarning, match="is not a tugaphone lect"):
        assert resolve_lect(tag) == lect


@pytest.mark.parametrize("alias", sorted(_ALIASES))
def test_every_alias_keeps_its_lect_after_unnamed_subtags(alias):
    for tag in (f"{alias}-foo", f"{alias}-foo-bar"):
        with pytest.warns(UserWarning, match="is not a tugaphone lect"):
            lect = resolve_lect(tag)
        assert lect == resolve(_ALIASES[alias])
        assert lect in list_dialects()


@pytest.mark.parametrize("tag", [
    "pt-PT-x-porto-foo", "pt-BR-x-sp-foo", "pt-PT-x-unknown-foo", "pt-US-x-foo", "pt-419-x-foo",
])
def test_a_tag_that_truncation_leaves_unnamed_takes_the_nearest_lect(tag):
    nearest = closest_lang(with_default_region(tag), list_dialects(), lects="standard")
    with pytest.warns(UserWarning, match="is not a tugaphone lect"):
        assert resolve_lect(tag) == nearest
