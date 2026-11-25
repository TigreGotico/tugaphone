"""A longer place name that only starts with an alias is not that alias."""

import warnings

import pytest
from orthography2ipa import available_codes

from tugaphone import resolve_lect


@pytest.mark.xfail(
    strict=True,
    reason="tugaphone#357: a tag that starts with the alias pt-BR-x-rio or "
           "pt-PT-x-acores takes that alias's lect")
@pytest.mark.parametrize("tag,acceptable", [
    ("pt-BR-x-rio-grande-do-sul", {"pt-BR-x-sul", "pt-BR"}),
    ("pt-BR-x-rio-grande-do-norte", {"pt-BR"}),
    ("pt-PT-x-acores-terceira", {"pt-PT-x-terceira", "pt-PT"}),
])
def test_longer_place_name_keeps_its_own_lect(tag, acceptable):
    assert acceptable - {"pt-PT", "pt-BR"} <= set(available_codes())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert resolve_lect(tag) in acceptable
