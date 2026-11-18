"""``revision(lect)`` changes when the output of a lect can change, and stays equal across processes and across
edits that cannot change the output.

A test never edits an installed file. It copies the package that it edits, and a process with the copy first on its
import path computes the revision.
"""
import os
import re
import shutil
import site
import subprocess
import sys
import sysconfig
import unicodedata
import warnings
import zipfile
from importlib.util import find_spec
from pathlib import Path

import pytest

import tugaphone
from tugaphone import phonemize, revision
from tugaphone import content_revision
from tugaphone.content_revision import RevisionError, distribution_digest, outside_stdlib, probe, tree_digest

PACKAGE = Path(tugaphone.__file__).parent


def installed(name: str) -> Path:
    return Path(find_spec(name).submodule_search_locations[0])


def copy_package(source: Path, into: Path) -> Path:
    target = into / source.name
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} is not in {path}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def add_statement(path: Path) -> None:
    path.write_text(path.read_text(encoding="utf-8") + "\n_REVISION_TEST_EDIT = 1\n", encoding="utf-8")


def revision_in_process(lect: str, path: Path | None = None, seed: str = "0") -> str:
    """The revision that a fresh process computes, with ``path`` first on its import path."""
    paths = [str(path)] if path else []
    env = {**os.environ, "PYTHONHASHSEED": seed,
           "PYTHONPATH": os.pathsep.join([*paths, *(entry or os.getcwd() for entry in sys.path)])}
    script = "import sys, tugaphone; print(tugaphone.__file__); print(tugaphone.revision(sys.argv[1]))"
    done = subprocess.run([sys.executable, "-P", "-c", script, lect], capture_output=True, text=True, env=env,
                          check=True)
    where, value = done.stdout.split()[-2:]
    expected = path / "tugaphone" if path and (path / "tugaphone").is_dir() else PACKAGE
    assert Path(where).parent == expected
    return value


@pytest.fixture
def tugaphone_copy(tmp_path):
    return copy_package(PACKAGE, tmp_path)


def test_a_revision_is_the_scheme_prefix_and_a_sha256():
    assert re.fullmatch(r"tp1:[0-9a-f]{64}", revision("pt-PT"))


def test_a_revision_is_equal_in_another_process_with_another_hash_seed():
    assert revision_in_process("pt-PT", seed="4242") == revision("pt-PT")


def test_pt_pt_and_pt_br_have_different_revisions():
    assert revision("pt-PT") != revision("pt-BR")


def test_an_alias_has_the_revision_of_its_lect():
    assert revision("pt") == revision("pt-PT")


def test_an_unknown_lect_warns_as_phonemize_warns_and_takes_the_fallback_revision():
    with warnings.catch_warnings(record=True) as phonemized:
        warnings.simplefilter("always")
        phonemize("olá", "xx-ZZ")
    with warnings.catch_warnings(record=True) as revised:
        warnings.simplefilter("always")
        value = revision("xx-ZZ")
    assert [str(w.message) for w in revised] == ["'xx-ZZ' is not a tugaphone lect; using pt-PT"]
    assert [str(w.message) for w in revised][0] in [str(w.message) for w in phonemized]
    assert value == revision("pt-PT")


def test_the_probe_loads_the_frontend_and_not_every_module():
    loaded = probe("pt-PT")
    assert {"tugaphone.lattice_core", "desacordo_ortografico", "bifonia", "o2i_lexicons", "tugalex",
            "ovos_number_parser.numbers_pt"} <= loaded
    assert "tugaphone.tokenizer" not in loaded
    assert "desacordo_ortografico.cli" not in loaded


def test_a_copy_of_the_package_has_the_revision_of_the_package(tugaphone_copy):
    assert revision_in_process("pt-PT", tugaphone_copy.parent) == revision("pt-PT")


def test_a_one_byte_edit_of_a_data_file_changes_the_revision(tugaphone_copy):
    edit(tugaphone_copy / "data" / "loanwords.json", '"ace": "ˈeɪs"', '"ace": "ˈeɪz"')
    assert revision_in_process("pt-PT", tugaphone_copy.parent) != revision("pt-PT")


def test_an_edit_of_a_module_that_the_probe_does_not_load_changes_the_revision(tugaphone_copy):
    assert "tugaphone.tokenizer" not in probe("pt-PT")
    add_statement(tugaphone_copy / "tokenizer.py")
    assert revision_in_process("pt-PT", tugaphone_copy.parent) != revision("pt-PT")


def test_an_edit_of_a_dependency_module_that_the_probe_does_not_load_changes_the_revision(tmp_path):
    assert "desacordo_ortografico.cli" not in probe("pt-PT")
    add_statement(copy_package(installed("desacordo_ortografico"), tmp_path) / "cli.py")
    assert revision_in_process("pt-PT", tmp_path) != revision("pt-PT")


def test_a_version_edit_keeps_the_revision(tugaphone_copy):
    version = tugaphone_copy / "version.py"
    text = version.read_text(encoding="utf-8")
    bumped = re.sub(r"VERSION_ALPHA = \d+", "VERSION_ALPHA = 999", text)
    assert bumped != text
    version.write_text(bumped, encoding="utf-8")
    assert revision_in_process("pt-PT", tugaphone_copy.parent) == revision("pt-PT")


def test_a_docstring_edit_keeps_the_revision(tugaphone_copy):
    before = tree_digest("tugaphone", tugaphone_copy)
    core = tugaphone_copy / "lattice_core.py"
    edit(core, '"""Phonemize ``text`` for ``lang``', '"""Phonemize the edited ``text`` for ``lang``')
    edit(core, "    Each call returns a new ``Pipeline``", "    Each call gives a new ``Pipeline``")
    assert tree_digest("tugaphone", tugaphone_copy) == before


def test_a_comment_edit_keeps_the_revision(tugaphone_copy):
    before = tree_digest("tugaphone", tugaphone_copy)
    core = tugaphone_copy / "lattice_core.py"
    edit(core, "\ndef pipeline(", "\n# A comment on its own line.\ndef pipeline(")
    edit(core, "    _validate_contact(contact)\n", "    _validate_contact(contact)  # A comment at the end of a line.\n")
    assert tree_digest("tugaphone", tugaphone_copy) == before


def test_a_one_token_code_edit_changes_the_digest(tugaphone_copy):
    before = tree_digest("tugaphone", tugaphone_copy)
    edit(tugaphone_copy / "registry.py", '"pt-br-x-rio": "pt-BR-x-rj"', '"pt-br-x-rio": "pt-BR"')
    assert tree_digest("tugaphone", tugaphone_copy) != before


def test_another_unicode_database_changes_the_revision(monkeypatch):
    before = revision("pt-PT")
    monkeypatch.setattr(unicodedata, "unidata_version", "1.1.0")
    content_revision._revision.cache_clear()
    try:
        assert revision("pt-PT") != before
    finally:
        content_revision._revision.cache_clear()


def test_a_package_imported_from_a_zip_raises_and_does_not_hash_nothing(tmp_path, monkeypatch):
    archive = tmp_path / "zipped.zip"
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("zipped_dependency/__init__.py", "VALUE = 1\n")
    monkeypatch.syspath_prepend(str(archive))
    assert find_spec("zipped_dependency").origin.startswith(str(archive))
    with pytest.raises(RevisionError, match="cannot be read from the file system"):
        distribution_digest("zipped-dependency", {"zipped_dependency"})


def test_a_distribution_with_no_file_raises():
    with pytest.raises(RevisionError, match="no file of the distribution"):
        distribution_digest("absent", {"no_module_of_this_name"})


def test_a_standard_library_file_under_another_name_is_not_on_the_output_path():
    stdlib = Path(sysconfig.get_paths()["stdlib"])
    modules = {
        "_sysconfigdata__linux_x86_64-linux-gnu": str(stdlib / "_sysconfigdata__linux_x86_64-linux-gnu.py"),
        "calendar_patched": str(stdlib / "calendar.py"),
        "made_at_run_time": None,
        "tugaphone": tugaphone.__file__,
        "desacordo_ortografico": find_spec("desacordo_ortografico").origin,
    }
    assert outside_stdlib(modules) == {"tugaphone", "desacordo_ortografico"}


def test_a_distribution_in_a_site_packages_directory_under_the_standard_library_counts(tmp_path, monkeypatch):
    stdlib = tmp_path / "usr" / "lib" / "python3"
    base_site = stdlib / "site-packages"
    user_site = stdlib / "user-site-packages"
    monkeypatch.setattr(sysconfig, "get_paths", lambda *args, **kwargs: {
        "stdlib": str(stdlib), "platstdlib": str(stdlib),
        "purelib": str(tmp_path / "venv" / "site-packages"), "platlib": str(tmp_path / "venv" / "site-packages")})
    monkeypatch.setattr(site, "getsitepackages", lambda *args: [str(base_site)])
    monkeypatch.setattr(site, "getusersitepackages", lambda: str(user_site))
    modules = {
        "base_distribution": str(base_site / "base_distribution" / "__init__.py"),
        "user_distribution": str(user_site / "user_distribution.py"),
        "json_copy": str(stdlib / "json" / "__init__.py"),
    }
    assert outside_stdlib(modules) == {"base_distribution", "user_distribution"}


@pytest.mark.parametrize("packages_dir", ["site-packages", "dist-packages"])
def test_a_standard_library_file_under_the_bare_prefix_is_not_on_the_output_path(tmp_path, monkeypatch, packages_dir):
    stdlib = tmp_path / "opt" / "py" / "Lib"
    site_packages = stdlib / packages_dir
    monkeypatch.setattr(sysconfig, "get_paths", lambda *args, **kwargs: {
        "stdlib": str(stdlib), "platstdlib": str(stdlib),
        "purelib": str(tmp_path / "venv" / "site-packages"), "platlib": str(tmp_path / "venv" / "site-packages")})
    monkeypatch.setattr(site, "getsitepackages", lambda *args: [str(stdlib.parent), str(site_packages)])
    monkeypatch.setattr(site, "getusersitepackages", lambda: str(tmp_path / "user" / "site-packages"))
    modules = {
        "calendar_copy": str(stdlib / "calendar.py"),
        "numtag": str(site_packages / "numtag" / "__init__.py"),
    }
    assert outside_stdlib(modules) == {"numtag"}


def test_a_module_level_string_constant_edit_changes_the_revision(tugaphone_copy):
    edit(tugaphone_copy / "number_utils.py", '_NUMBER = r"\\d+(?:[.,]\\d+)*"', '_NUMBER = r"\\d*(?:[.,]\\d+)*"')
    assert revision_in_process("pt-PT", tugaphone_copy.parent) != revision("pt-PT")


def compiled_distribution(root: Path, init: str, binary: bytes) -> Path:
    package = root / "compiled_dependency"
    package.mkdir(exist_ok=True)
    (package / "__init__.py").write_text(init, encoding="utf-8")
    (package / "_speedups.cpython-314-x86_64-linux-gnu.so").write_bytes(binary)
    metadata = root / "compiled_dependency-1.2.3.dist-info"
    metadata.mkdir(exist_ok=True)
    (metadata / "METADATA").write_text("Metadata-Version: 2.1\nName: compiled-dependency\nVersion: 1.2.3\n",
                                       encoding="utf-8")
    return package


def test_a_compiled_distribution_counts_by_name_and_version_and_not_by_its_files(tmp_path, monkeypatch):
    package = compiled_distribution(tmp_path, "VALUE = 1\n", b"\x7fELF one build")
    monkeypatch.syspath_prepend(str(tmp_path))
    assert distribution_digest("compiled-dependency", {"compiled_dependency"}) == "compiled 1.2.3"
    (package / "_speedups.cpython-314-x86_64-linux-gnu.so").write_bytes(b"\x7fELF another platform")
    (package / "__init__.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert distribution_digest("compiled-dependency", {"compiled_dependency"}) == "compiled 1.2.3"


FAKE_MODULE = "/opt/fake/site-packages/fake_distribution/__init__.py"


def fake_probe(monkeypatch, script: str) -> None:
    """Make the probe child run ``script``. The child gets the lect, the text and the marker as arguments."""
    monkeypatch.setattr(content_revision, "_PROBE", script)


def test_output_after_the_result_does_not_corrupt_the_probe(monkeypatch):
    fake_probe(monkeypatch, f"""
import atexit, json, sys
print("a library writes to stdout before the result")
print(sys.argv[3])
print(json.dumps({{"fake_distribution": {FAKE_MODULE!r}}}))
print("{{not json, after the result")
atexit.register(print, "a library writes to stdout at exit")
""")
    assert probe("probe-test-junk") == {"fake_distribution"}


def test_a_probe_that_prints_nothing_raises_a_revision_error(monkeypatch):
    fake_probe(monkeypatch, "pass")
    with pytest.raises(RevisionError, match="gave no result"):
        probe("probe-test-silent")


def test_a_probe_result_that_is_not_json_raises_a_revision_error(monkeypatch):
    fake_probe(monkeypatch, "import sys; print(sys.argv[3]); print('{not json')")
    with pytest.raises(RevisionError, match="not JSON"):
        probe("probe-test-bad-json")


def test_a_probe_that_hangs_past_the_timeout_raises_a_revision_error(monkeypatch):
    fake_probe(monkeypatch, "import time; time.sleep(60)")
    monkeypatch.setattr(content_revision, "PROBE_TIMEOUT", 1)
    with pytest.raises(RevisionError, match="did not finish in 1 s"):
        probe("probe-test-hang")


def test_a_revision_error_is_a_runtime_error():
    assert issubclass(RevisionError, RuntimeError)
