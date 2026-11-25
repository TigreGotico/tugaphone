"""Azores island sub-tags reach the island lect, not the generic Azores lect."""

import warnings

import pytest
from orthography2ipa import available_codes

from tugaphone import is_supported, list_dialects, resolve_lect

CENTRAL_GROUP = ["terceira", "faial", "pico", "sao-jorge", "graciosa"]


def test_island_lects_are_listed():
    assert {"pt-PT-x-sao-miguel", "pt-PT-x-terceira"} <= set(available_codes())
    assert {"pt-PT-x-sao-miguel", "pt-PT-x-terceira"} <= set(list_dialects())


@pytest.mark.parametrize("prefix", ["acores", "azores"])
@pytest.mark.parametrize("suffix", ["", "-foo"])
def test_sao_miguel_reaches_its_lect(prefix, suffix):
    tag = f"pt-PT-x-{prefix}-sao-miguel{suffix}"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert resolve_lect(tag) == "pt-PT-x-sao-miguel"


@pytest.mark.parametrize("prefix", ["acores", "azores"])
@pytest.mark.parametrize("island", CENTRAL_GROUP)
@pytest.mark.parametrize("suffix", ["", "-foo"])
def test_central_group_reaches_terceira(prefix, island, suffix):
    tag = f"pt-PT-x-{prefix}-{island}{suffix}"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert resolve_lect(tag) == "pt-PT-x-terceira"


@pytest.mark.parametrize("island", CENTRAL_GROUP + ["sao-miguel"])
def test_island_tag_is_supported(island):
    assert is_supported(f"pt-PT-x-azores-{island}")
