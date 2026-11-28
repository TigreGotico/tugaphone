"""The Flores, Corvo and Santa Maria tags are supported aliases of pt-PT-x-acores."""

import warnings

import pytest

from tugaphone import is_supported
from tugaphone.registry import resolve_lect

# Mikołajczak (2014) groups Flores and Corvo in the western group and Santa Maria
# in the eastern group, which pt-PT-x-acores models.
_ISLAND_TAGS = [
    "pt-PT-x-acores-flores",
    "pt-PT-x-acores-corvo",
    "pt-PT-x-acores-santa-maria",
]


@pytest.mark.xfail(raises=AssertionError, 
    strict=True,
    reason="https://github.com/TigreGotico/tugaphone/issues/376: the Flores, "
           "Corvo and Santa Maria tags warn and are unsupported")
def test_island_tags_resolve_to_the_acores_lect_without_a_warning():
    for tag in _ISLAND_TAGS:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            lect = resolve_lect(tag)
        assert lect == "pt-PT-x-acores", tag
        assert [str(w.message) for w in caught
                if "is not a tugaphone lect" in str(w.message)] == [], tag
        assert is_supported(tag) is True, tag
