"""tugaphone.tokenizer, tugaphone.dialects and get_dialect_inventory are deprecated.

Each warns once with the removal release, the next major version, and the
warning points at the caller's line. A fresh interpreter runs each import,
because a module warns only on its first import.
"""
import json
import subprocess
import sys
import warnings

import pytest

from tugaphone.version import VERSION_MAJOR

REMOVAL = f"{VERSION_MAJOR + 1}.0.0"

CALLER = """
import json
import warnings

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    {statement}
print(json.dumps([[w.category.__name__, str(w.message), w.filename]
                  for w in caught if issubclass(w.category, DeprecationWarning)]))
"""


def _deprecations(tmp_path, statement):
    caller = tmp_path / "caller.py"
    caller.write_text(CALLER.format(statement=statement), encoding="utf-8")
    result = subprocess.run([sys.executable, str(caller)], capture_output=True,
                            text=True, check=True)
    return str(caller), json.loads(result.stdout.splitlines()[-1])


@pytest.mark.parametrize("module", ["tugaphone.tokenizer", "tugaphone.dialects"])
def test_import_warns_with_removal_version_at_caller(tmp_path, module):
    caller, caught = _deprecations(tmp_path, f"import {module}")
    assert len(caught) == 1, caught
    category, message, filename = caught[0]
    assert category == "DeprecationWarning"
    assert message.startswith(f"{module} is deprecated")
    assert f"removed in tugaphone {REMOVAL}" in message
    assert filename == caller


def test_import_still_works():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from tugaphone.dialects import EuropeanPortuguese
        from tugaphone.tokenizer import Sentence
    sentence = Sentence("o gato", dialect=EuropeanPortuguese())
    assert [w.surface for w in sentence.words] == ["o", "gato"]


def test_get_dialect_inventory_warns_at_caller():
    from tugaphone.dialects import BrazilianPortuguese
    from tugaphone.registry import get_dialect_inventory

    with pytest.warns(DeprecationWarning, match=f"removed in tugaphone {REMOVAL}") as caught:
        inventory = get_dialect_inventory("pt-BR")
    assert isinstance(inventory, BrazilianPortuguese)
    # Building an inventory also runs tugalex's own deprecation of get_ipa_map.
    ours = [w for w in caught if "get_dialect_inventory" in str(w.message)]
    assert [w.filename for w in ours] == [__file__]


def test_phonemize_path_is_silent():
    code = ("import tugaphone; tugaphone.phonemize('Tenho 3 gatos.', 'pt-PT'); "
            "tugaphone.phonemize('Vou ao shopping.', 'pt-BR', contact='auto')")
    subprocess.run([sys.executable, "-W", "error::DeprecationWarning", "-c", code],
                   check=True)
