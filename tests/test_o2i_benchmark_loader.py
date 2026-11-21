"""The scripts that read orthography2ipa's gold load orthography2ipa's
scripts/benchmark.py, never tugaphone's own.

``O2I_ROOT`` names the orthography2ipa checkout. A ``scripts/`` directory counts
only when an ``orthography2ipa/`` package sits next to it, so a venv inside the
tugaphone checkout does not find tugaphone's ``scripts/benchmark.py``.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

FAKE_BENCHMARK = '''
_PORTUGUESE_TTS_LANGS = ["pt-PT", "pt-BR", "mwl"]


def load_portuguese_tts(lect, limit):
    return [("frase de " + lect, "gold")]


def normalize(ipa, *args):
    return ipa
'''


@pytest.fixture
def o2i_root(tmp_path, monkeypatch):
    (tmp_path / "orthography2ipa").mkdir()
    (tmp_path / "orthography2ipa" / "__init__.py").write_text("")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "benchmark.py").write_text(FAKE_BENCHMARK)
    monkeypatch.setenv("O2I_ROOT", str(tmp_path))
    return tmp_path


@pytest.fixture
def venv_in_checkout(tmp_path, monkeypatch):
    """An orthography2ipa wheel in a venv inside a checkout whose own scripts/
    holds a benchmark.py, as in a venv inside the tugaphone checkout."""
    site = tmp_path / ".venv" / "site-packages"
    (site / "orthography2ipa").mkdir(parents=True)
    (site / "orthography2ipa" / "__init__.py").write_text("")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "benchmark.py").write_text("NOT_O2I = True\n")
    monkeypatch.delenv("O2I_ROOT", raising=False)
    monkeypatch.syspath_prepend(str(site))
    monkeypatch.delitem(sys.modules, "orthography2ipa", raising=False)
    return tmp_path


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_roundtrip_eval_reads_o2i_root(o2i_root):
    module = _load(ROOT / "scripts" / "roundtrip_eval.py", "roundtrip_eval_under_test")
    assert Path(module.O2I.__file__) == o2i_root / "scripts" / "benchmark.py"


def test_synthetic_corpus_full_reads_o2i_root(o2i_root):
    module = _load(ROOT / "examples" / "12_synthetic_corpus.py", "synthetic_corpus_under_test")
    # mwl is not a tugaphone lect, so only the two Portuguese lects remain.
    assert module._load_full() == [("frase de pt-BR", "pt-BR"), ("frase de pt-PT", "pt-PT")]


def test_roundtrip_eval_skips_a_checkout_without_orthography2ipa(venv_in_checkout):
    with pytest.raises(RuntimeError, match="O2I_ROOT"):
        _load(ROOT / "scripts" / "roundtrip_eval.py", "roundtrip_eval_under_test")


def test_synthetic_corpus_skips_a_checkout_without_orthography2ipa(venv_in_checkout):
    module = _load(ROOT / "examples" / "12_synthetic_corpus.py", "synthetic_corpus_under_test")
    with pytest.raises(RuntimeError, match="O2I_ROOT"):
        module._load_full()
