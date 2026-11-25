"""``revision`` is the version strings of tugaphone and of its installed dependencies."""
import importlib.metadata
from importlib.metadata import PackageNotFoundError, distribution

import pytest

from tugaphone import content_revision, revision


@pytest.fixture(autouse=True)
def fresh_revision():
    content_revision._revision.cache_clear()
    yield
    content_revision._revision.cache_clear()


def expected() -> str:
    """The revision, built from the metadata of tugaphone and by the rule of the contract."""
    names = {"tugaphone"}
    for line in distribution("tugaphone").requires:
        name = line.split(";")[0]
        for cut in "<>=!~[( ":
            name = name.split(cut)[0]
        if "extra ==" not in line:
            names.add(name.lower().replace("_", "-").replace(".", "-"))
    return ";".join(f"{n}=={distribution(n).version}" for n in sorted(names))


def test_the_revision_is_the_sorted_version_strings_of_tugaphone_and_its_dependencies():
    assert revision() == expected()
    parts = revision().split(";")
    assert parts == sorted(parts)
    assert f"tugaphone=={importlib.metadata.version('tugaphone')}" in parts
    assert any(part.startswith("orthography2ipa==") for part in parts)


def test_the_revision_is_the_same_across_calls_and_lects():
    assert revision("pt-PT") == revision("pt-PT") == revision("pt-BR") == revision("xx")


def test_an_extra_is_not_in_the_revision():
    assert not any(part.startswith("markovonnx==") for part in revision().split(";"))


def test_a_new_orthography2ipa_version_changes_the_revision(monkeypatch):
    before = revision()
    real = importlib.metadata.version
    monkeypatch.setattr(content_revision, "version",
                        lambda name: "999.0.0a1" if name == "orthography2ipa" else real(name))
    content_revision._revision.cache_clear()
    after = revision()
    assert after != before
    assert "orthography2ipa==999.0.0a1" in after.split(";")
    assert after.replace("orthography2ipa==999.0.0a1", "") == before.replace(f"orthography2ipa=={real('orthography2ipa')}", "")


def test_a_dependency_that_is_not_installed_is_left_out(monkeypatch):
    real = importlib.metadata.version

    def missing(name):
        if name == "bifonia":
            raise PackageNotFoundError(name)
        return real(name)

    monkeypatch.setattr(content_revision, "version", missing)
    assert revision() == ";".join(p for p in expected().split(";") if not p.startswith("bifonia=="))
