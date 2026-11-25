"""Every alias value names a lect that orthography2ipa lists."""

import pytest
from orthography2ipa import available_codes

from tugaphone.registry import _ALIASES, list_dialects


@pytest.mark.xfail(
    strict=True,
    reason="tugaphone#358: _ALIASES holds the renamed key pt-PT-x-trasosmontes")
def test_every_alias_value_is_a_current_lect():
    known = set(list_dialects()) | set(available_codes())
    stale = {alias: lect for alias, lect in _ALIASES.items() if lect not in known}
    assert stale == {}
