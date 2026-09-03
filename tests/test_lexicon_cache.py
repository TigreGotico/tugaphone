"""Regression tests for the materialised tugalex lexicon cache invalidation.

A materialised ``<lect>.tsv`` in TUGAPHONE_LEXICON_DIR is tied to the tugalex
version that produced it: a missing or empty TSV, or one whose version stamp
does not match the installed ``tugalex``, is rewritten before use; a TSV
whose stamp matches the installed version is reused as-is. These tests
exercise ``tugaphone.lattice_core._ensure_lexicon`` directly against a
scratch cache directory so they never touch the real ``~/.cache/tugaphone``.
"""
import pytest

from tugaphone import lattice_core


@pytest.fixture
def scratch_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(lattice_core, "_LEXICON_CACHE", tmp_path)
    monkeypatch.setattr(lattice_core, "_registered", set())
    calls = []
    orig_write = lattice_core._write_lexicon

    def spy_write(region, path):
        calls.append(path)
        orig_write(region, path)

    monkeypatch.setattr(lattice_core, "_write_lexicon", spy_write)
    return tmp_path, calls


def test_stale_version_stamp_triggers_rewrite(scratch_cache, monkeypatch):
    tmp_path, calls = scratch_cache
    lect = "pt-PT"
    region = lattice_core.lexicon_region(lect)
    assert region is not None

    path = tmp_path / f"{lect}.tsv"
    path.write_text("bogus\tˈbɔgʊʃ\n", encoding="utf-8")
    lattice_core._stamp_path(path).write_text("0.0.0-stale", encoding="utf-8")

    monkeypatch.setattr(lattice_core, "_tugalex_version", lambda: "9.9.9")

    lattice_core._ensure_lexicon(lect)

    assert calls == [path], "a stale version stamp must trigger a rewrite"
    # the rewrite must reflect the real tugalex data, not the bogus entry
    assert "bogus\tˈbɔgʊʃ" not in path.read_text(encoding="utf-8")


def test_matching_version_stamp_is_reused(scratch_cache, monkeypatch):
    tmp_path, calls = scratch_cache
    lect = "pt-PT"

    monkeypatch.setattr(lattice_core, "_tugalex_version", lambda: "1.2.3")
    lattice_core._ensure_lexicon(lect)
    assert calls == [tmp_path / f"{lect}.tsv"]

    # a second lookup under the same version must not rewrite the cache
    lattice_core._registered.discard(lect)
    lattice_core._ensure_lexicon(lect)
    assert calls == [tmp_path / f"{lect}.tsv"], "matching stamp must be reused, not rewritten"
