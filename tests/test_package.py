"""Smoke tests for the public package surface."""
import tugaphone


def test_version_is_exposed():
    assert isinstance(tugaphone.__version__, str)
    assert tugaphone.__version__
