"""A place name that only starts with pt-BR-x-rio is not Rio de Janeiro."""

import pytest

from tugaphone import is_supported, resolve_lect

PLACES = ["pt-BR-x-rio-branco", "pt-BR-x-rio-claro", "pt-BR-x-rio-verde"]


@pytest.mark.xfail(raises=AssertionError, 
    strict=True,
    reason="tugaphone#367: a tag that starts with the alias pt-BR-x-rio "
           "resolves to the Rio de Janeiro lect")
@pytest.mark.parametrize("tag", PLACES)
def test_other_rio_place_falls_back_with_warning(tag):
    with pytest.warns(UserWarning, match="not a tugaphone lect"):
        assert resolve_lect(tag) == "pt-BR"


@pytest.mark.xfail(raises=AssertionError, 
    strict=True,
    reason="tugaphone#367: the pt-BR-x-rio-grande-do-norte alias maps to the "
           "national fallback, so is_supported returns True")
def test_rio_grande_do_norte_is_not_supported():
    assert not is_supported("pt-BR-x-rio-grande-do-norte")
    with pytest.warns(UserWarning, match="not a tugaphone lect"):
        assert resolve_lect("pt-BR-x-rio-grande-do-norte") == "pt-BR"
