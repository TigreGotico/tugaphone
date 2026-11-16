"""Smoke tests for the public package surface."""
import tugaphone
from tugaphone.dialects import (
    EuropeanPortuguese,
    BrazilianPortuguese,
    AngolanPortuguese,
    MozambicanPortuguese,
    TimoresePortuguese,
)


def test_version_is_exposed():
    assert isinstance(tugaphone.__version__, str)
    assert tugaphone.__version__


def test_dialect_inventories_instantiate():
    for cls in (
        EuropeanPortuguese,
        BrazilianPortuguese,
        AngolanPortuguese,
        MozambicanPortuguese,
        TimoresePortuguese,
    ):
        assert cls() is not None
