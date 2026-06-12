"""Smoke-test every example script: assert it exits 0."""
import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXAMPLES = sorted(EXAMPLES_DIR.glob("[0-9][0-9]_*.py"))


def _run(script: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        env={
            **__import__("os").environ,
            "PYTHONPATH": str(script.parent.parent),
        },
    )


def test_all_examples_exist():
    assert len(EXAMPLES) >= 9, f"Expected at least 9 examples, found {len(EXAMPLES)}"


def test_01_basic():
    r = _run(EXAMPLES_DIR / "01_basic.py")
    assert r.returncode == 0, r.stderr


def test_02_dialects():
    r = _run(EXAMPLES_DIR / "02_dialects.py")
    assert r.returncode == 0, r.stderr


def test_03_regional_accents():
    r = _run(EXAMPLES_DIR / "03_regional_accents.py")
    assert r.returncode == 0, r.stderr


def test_04_numbers():
    r = _run(EXAMPLES_DIR / "04_numbers.py")
    assert r.returncode == 0, r.stderr


def test_05_token_tree():
    r = _run(EXAMPLES_DIR / "05_token_tree.py")
    assert r.returncode == 0, r.stderr


def test_06_serialize_accent():
    r = _run(EXAMPLES_DIR / "06_serialize_accent.py")
    assert r.returncode == 0, r.stderr


def test_07_homographs():
    r = _run(EXAMPLES_DIR / "07_homographs.py")
    assert r.returncode == 0, r.stderr


def test_08_rules_only():
    r = _run(EXAMPLES_DIR / "08_rules_only.py")
    assert r.returncode == 0, r.stderr


def test_09_plugin():
    r = _run(EXAMPLES_DIR / "09_plugin.py")
    assert r.returncode == 0, r.stderr
