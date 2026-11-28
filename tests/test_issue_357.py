"""A longer place name that only starts with an alias is not that alias."""

import warnings

import pytest
from orthography2ipa import available_codes

from tugaphone import resolve_lect


def test_expected_lects_are_listed():
    assert {"pt-BR-x-sul", "pt-PT-x-terceira"} <= set(available_codes())


@pytest.mark.parametrize("tag,acceptable", [
    ("pt-BR-x-rio-grande-do-sul", {"pt-BR-x-sul", "pt-BR"}),
    ("pt-BR-x-rio-grande-do-norte", {"pt-BR"}),
    ("pt-PT-x-acores-terceira", {"pt-PT-x-terceira", "pt-PT"}),
])
def test_longer_place_name_keeps_its_own_lect(tag, acceptable):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert resolve_lect(tag) in acceptable
