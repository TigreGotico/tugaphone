"""``revision`` is the version strings of tugaphone and of its installed dependencies."""
import importlib.metadata
from importlib.metadata import PackageNotFoundError, metadata

import pytest

from tugaphone import content_revision, revision


@pytest.fixture(autouse=True)
def fresh_revision():
    content_revision._revision.cache_clear()
    yield
    content_revision._revision.cache_clear()


def canonical(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def expected() -> str:
    """The revision, built from the metadata of tugaphone by the rule of the contract."""
    names = set()
    for line in importlib.metadata.requires("tugaphone"):
        name = line.split(";")[0]
        for cut in "<>=!~[( ":
            name = name.split(cut)[0]
        if "extra ==" not in line:
            names.add(canonical(name))
    pins = [f"{metadata(n)['Name']}=={metadata(n)['Version']}" for n in sorted(names)]
    return ";".join([f"tugaphone=={metadata('tugaphone')['Version']}", *pins])


def test_the_revision_is_tugaphone_then_the_sorted_dependencies():
    assert revision() == expected()
    parts = revision().split(";")
    assert parts[0] == f"tugaphone=={importlib.metadata.version('tugaphone')}"
    tail = [canonical(part.split("==")[0]) for part in parts[1:]]
    assert tail == sorted(tail)
    assert any(part.startswith("orthography2ipa==") for part in parts)


def test_a_name_is_spelled_as_the_distribution_metadata_spells_it():
    assert f"{metadata('desacordo-ortografico')['Name']}==" in revision()


def test_the_revision_is_the_same_across_calls_and_lects():
    assert revision("pt-PT") == revision("pt-PT") == revision("pt-BR") == revision("xx")


def test_an_extra_is_not_in_the_revision():
    assert not any(part.startswith("markovonnx==") for part in revision().split(";"))


def test_a_new_orthography2ipa_version_changes_the_revision(monkeypatch):
    before = revision()
    real = content_revision.metadata

    def newer(name):
        return {"Name": real(name)["Name"], "Version": "999.0.0a1"} if canonical(name) == "orthography2ipa" else real(name)

    monkeypatch.setattr(content_revision, "metadata", newer)
    content_revision._revision.cache_clear()
    after = revision()
    assert after != before
    assert "orthography2ipa==999.0.0a1" in after.split(";")
    old = f"orthography2ipa=={real('orthography2ipa')['Version']}"
    assert after.replace("orthography2ipa==999.0.0a1", "") == before.replace(old, "")


def test_a_dependency_that_is_not_installed_is_left_out(monkeypatch):
    real = content_revision.metadata

    def missing(name):
        if name == "bifonia":
            raise PackageNotFoundError(name)
        return real(name)

    monkeypatch.setattr(content_revision, "metadata", missing)
    assert revision() == ";".join(p for p in expected().split(";") if not p.startswith("bifonia=="))
