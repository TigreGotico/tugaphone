"""Content revision of a lect: a string that changes when the output of ``phonemize`` for the lect can change.

A consumer that records the revision of the lect it trained on can tell whether the tugaphone it runs reads the
same rules, without a comparison of version strings. These packages publish an alpha almost every day, and most
alphas change no output for a given lect.

The revision is a sha256 over:

- the version of the Unicode database of the running Python (``unicodedata.unidata_version``), which decides how
  the text stages normalise and classify characters;
- the revision of the orthography2ipa spec of the lect (:func:`orthography2ipa.spec_revision`), and of the packaged
  lexicon when the lect takes one (:func:`orthography2ipa.lexicon_revision`);
- each other distribution that a probe call of :func:`tugaphone.phonemize` for the lect imports, in a fresh process.
  Such a distribution counts whole: the code tokens of each of its Python modules, the ones the probe does not load
  included, and the bytes of each of its data files.

A comment, a docstring, a blank line, the width of an indent and a ``version.py`` or ``_version.py`` at the top of a
package do not count. No version string counts, with one exception: a distribution that ships a compiled module
counts by its name and version, because its files differ by platform and by Python build.

The revision covers ``contact="none"``, the default. See :func:`revision`.

A distribution whose files cannot be read from the file system, as a package imported from a zip, raises
:class:`RevisionError`: a hash of no files would stay equal across every edit of it.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import secrets
import site
import subprocess
import sys
import sysconfig
import tokenize
import unicodedata
from functools import cache
from importlib.metadata import PackageNotFoundError, packages_distributions, version
from importlib.util import find_spec
from pathlib import Path
from typing import Callable, Dict, FrozenSet, Iterator, List, Optional, Set, Tuple

from orthography2ipa import lexicon_revision, spec_revision

from tugaphone.registry import PACKAGED_LEXICON_LECTS, resolve_lect

#: The prefix of a revision. It changes when the inputs or the encoding of the hash change.
FORMAT = "tp1"

#: The text of the probe call: a title, a cardinal, an ordinal, a year, a time and a homograph.
PROBE_TEXT = "O Sr. Silva leu 23 livros no 1.º dia de 2024, às 10:30, e a sede da sede é longe."

#: The seconds that the probe process can run. A cold probe takes 4 to 5.5 s on a laptop, nearly all of it in
#: ``import tugaphone``. A small board or a cold disk can be ten times slower. The limit only ends a hung process.
PROBE_TIMEOUT = 120

_PROBE = """
import sys
before = set(sys.modules)
import json, warnings
warnings.simplefilter("ignore")
import tugaphone
tugaphone.phonemize(sys.argv[2], sys.argv[1])
loaded = {name: getattr(module, "__file__", None) for name, module in list(sys.modules.items())
          if name not in before and name.split(".")[0] not in sys.stdlib_module_names}
print(sys.argv[3], json.dumps(loaded), sep="\\n", flush=True)
"""


class RevisionError(RuntimeError):
    """``revision`` cannot give a revision: the probe fails, or the files of a distribution cannot be read."""

_NATIVE = frozenset({".so", ".pyd", ".dll", ".dylib"})
_VERSION_FILES = frozenset({"version.py", "_version.py"})
_DROPPED = frozenset({tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER})
_LINE = frozenset({"NEWLINE", "INDENT", "DEDENT"})


def _orthography2ipa_revision(lect: str) -> str:
    spec = spec_revision(lect)
    if lect not in PACKAGED_LEXICON_LECTS:
        return spec
    return f"{spec} {lexicon_revision(lect, patches=True)}"


#: Distributions that publish an output-stable revision of their own. The revision enters in place of the files.
OWN_REVISIONS: Dict[str, Callable[[str], str]] = {
    "orthography2ipa": _orthography2ipa_revision,
}


def revision(lang: str = "pt-PT") -> str:
    """A string that changes when the output of ``phonemize(text, lang)`` can change, for some text.

    ``lang`` resolves as :func:`tugaphone.phonemize` resolves it, with the same warning for a code that is not a
    lect, so a code and the lect it resolves to have one revision. The value is ``"tp1:"`` and a sha256 in hex. It
    is computed at the first call for a lect in a process and kept. The first call runs a probe in a fresh process
    and reads the files of each distribution on the output path.

    The revision covers ``contact="none"``, the default and the path that scriptconv uses. Another ``contact`` value
    also reads the ``en-GB``, ``es-ES`` and ``fr-FR`` specs of orthography2ipa and the optional markovonnx detector.
    The revision covers neither, so it can stay equal while that output changes.

    Raises
    ------
    RevisionError
        The probe process fails, or the files of a distribution on the output path cannot be read.
    """
    return _revision(resolve_lect(lang))


@cache
def _revision(lect: str) -> str:
    digest = hashlib.sha256(json.dumps([FORMAT, lect, unicodedata.unidata_version]).encode())
    for distribution, top_levels in sorted(distributions(lect).items()):
        own = OWN_REVISIONS.get(distribution)
        value = own(lect) if own else distribution_digest(distribution, top_levels)
        digest.update(f"\0{distribution}\0{value}".encode())
    return f"{FORMAT}:{digest.hexdigest()}"


@cache
def probe(lect: str) -> FrozenSet[str]:
    """The modules outside the standard library that ``phonemize(PROBE_TEXT, lect)`` imports.

    The call runs in a fresh process with the import path of this one. The process prints a marker line and then
    the result, so text that a library prints to stdout, also at exit, does not mix with the result.
    """
    path = os.pathsep.join(entry or os.getcwd() for entry in sys.path)
    marker = f"tugaphone-revision-probe-{secrets.token_hex(8)}"
    try:
        done = subprocess.run([sys.executable, "-P", "-c", _PROBE, lect, PROBE_TEXT, marker], capture_output=True,
                              text=True, env={**os.environ, "PYTHONPATH": path}, timeout=PROBE_TIMEOUT)
    except subprocess.TimeoutExpired as e:
        raise RevisionError(f"the revision probe for {lect!r} did not finish in {PROBE_TIMEOUT} s") from e
    if done.returncode:
        raise RevisionError(f"the revision probe for {lect!r} failed:\n{done.stderr}")
    _, found, after = done.stdout.rpartition(f"{marker}\n")
    if not found:
        raise RevisionError(f"the revision probe for {lect!r} gave no result:\n{done.stdout}{done.stderr}")
    result = after.partition("\n")[0]
    try:
        return outside_stdlib(json.loads(result))
    except json.JSONDecodeError as e:
        raise RevisionError(f"the revision probe for {lect!r} gave a result that is not JSON: {result!r}") from e


def outside_stdlib(modules: Dict[str, Optional[str]]) -> FrozenSet[str]:
    """The names of ``modules``, a map of name to file, that a file outside the standard library holds.

    A module of the standard library can have a name that :data:`sys.stdlib_module_names` does not hold, as the
    platform-named ``_sysconfigdata`` module or a copy of ``calendar`` that a dependency loads under another name.
    Its file is in the standard library directory. A module with no file was made at run time by code that is hashed
    with its own distribution. A site-packages directory can also be under the standard library directory, as
    ``/usr/lib/python3.X/site-packages`` is on Arch and on Fedora, so a file in the site-packages of the venv, of
    the base interpreter or of the user is installed, not standard library.
    """
    paths = sysconfig.get_paths()
    stdlib = (paths["stdlib"], paths["platstdlib"])
    site_packages = tuple(entry for entry in site.getsitepackages()
                          if os.path.basename(os.path.normpath(entry)) in ("site-packages", "dist-packages"))
    installed = (paths["purelib"], paths["platlib"], *site_packages, site.getusersitepackages())
    return frozenset(name for name, where in modules.items()
                     if where and (not where.startswith(stdlib) or where.startswith(installed)))


def _canonical(distribution: str) -> str:
    return re.sub(r"[-_.]+", "-", distribution).lower()


def distributions(lect: str) -> Dict[str, Set[str]]:
    """Each distribution that holds a module of the probe, with all of its top-level names.

    ``tugaphone`` and ``orthography2ipa`` are always in the result. A top-level name that no installed distribution
    holds, as a checkout on the import path, stands for a distribution of its own name.
    """
    owners = packages_distributions()
    loaded = {module.split(".")[0] for module in probe(lect)} | {"tugaphone", "orthography2ipa"}
    found: Dict[str, Set[str]] = {}
    for name in loaded:
        for owner in owners.get(name) or [name]:
            found.setdefault(_canonical(owner), set()).add(name)
    for name, held in owners.items():
        for owner in map(_canonical, held):
            if owner in found:
                found[owner].add(name)
    return found


def distribution_digest(distribution: str, top_levels: Set[str]) -> str:
    """The hash of the files of a distribution, found where the import system finds each top-level name."""
    files: List[Tuple[str, Path]] = []
    for name in sorted(top_levels):
        files.extend(_top_level_files(name))
    if not files:
        raise RevisionError(f"no file of the distribution {distribution!r} can be read, so no edit of it would "
                           "change the revision")
    if any(path.suffix in _NATIVE for _, path in files):
        try:
            return f"compiled {version(distribution)}"
        except PackageNotFoundError:
            return "compiled"
    return _digest(sorted(files))


def tree_digest(name: str, *roots: Path) -> str:
    """The hash of the files of the package ``name`` under ``roots``: code tokens of each module, bytes of each data file."""
    return _digest(sorted((f"{name}/{relative}", path) for relative, path in _package_files(roots)))


def _digest(files: List[Tuple[str, Path]]) -> str:
    digest = hashlib.sha256()
    for relative, path in files:
        digest.update(f"\0{relative}\0{file_digest(path)}".encode())
    return digest.hexdigest()


def _top_level_files(name: str) -> List[Tuple[str, Path]]:
    spec = find_spec(name)
    if spec is None:
        return []
    roots = tuple(map(Path, spec.submodule_search_locations or ()))
    if roots and all(root.is_dir() for root in roots):
        return [(f"{name}/{relative}", path) for relative, path in _package_files(roots)]
    if not roots and spec.origin and Path(spec.origin).is_file():
        return [(Path(spec.origin).name, Path(spec.origin))]
    raise RevisionError(f"the files of {name!r} cannot be read from the file system (found at {spec.origin!r}), "
                       "so no edit of it would change the revision")


def _package_files(roots: Tuple[Path, ...]) -> Iterator[Tuple[str, Path]]:
    for root in roots:
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            if (path.is_file() and "__pycache__" not in relative.parts and path.suffix != ".pyc"
                    and not (len(relative.parts) == 1 and relative.name in _VERSION_FILES)):
                yield relative.as_posix(), path


def file_digest(path: Path) -> str:
    """The hash of the code tokens of a Python module, or of the bytes of any other file."""
    data = path.read_bytes()
    if path.suffix == ".py":
        try:
            data = json.dumps(code_tokens(data), ensure_ascii=False).encode()
        except (SyntaxError, tokenize.TokenError, UnicodeDecodeError):
            pass
    return hashlib.sha256(data).hexdigest()


def code_tokens(source: bytes) -> List[Tuple[str, str]]:
    """The tokens of a module that can change what it does.

    Comments, blank lines and a string that stands as a statement of its own, as a docstring does, are left out.
    NEWLINE, INDENT and DEDENT count with an empty string, so the width of an indent does not count. An f-string is
    one token with its source text, so the tokens are equal on each Python version.
    """
    encoding, _ = tokenize.detect_encoding(io.BytesIO(source).readline)
    lines = io.StringIO(source.decode(encoding), newline="\n").readlines()
    tokens: List[Tuple[str, str]] = []
    depth, start = 0, (0, 0)
    for token in tokenize.tokenize(io.BytesIO(source).readline):
        kind = tokenize.tok_name[token.type]
        if kind in ("FSTRING_START", "TSTRING_START"):
            depth, start = depth + 1, start if depth else token.start
        elif kind in ("FSTRING_END", "TSTRING_END"):
            depth -= 1
            if not depth:
                tokens.append(("STRING", _source_text(lines, start, token.end)))
        elif not depth and token.type not in _DROPPED:
            tokens.append((kind, "" if kind in _LINE else token.string))
    return _without_string_statements(tokens)


def _source_text(lines: List[str], start: Tuple[int, int], end: Tuple[int, int]) -> str:
    (first, first_column), (last, last_column) = start, end
    if first == last:
        return lines[first - 1][first_column:last_column]
    return lines[first - 1][first_column:] + "".join(lines[first:last - 1]) + lines[last - 1][:last_column]


def _without_string_statements(tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    kept: List[Tuple[str, str]] = []
    at = 0
    while at < len(tokens):
        end = at
        while end < len(tokens) and tokens[end][0] == "STRING":
            end += 1
        starts_line = not kept or kept[-1][0] in _LINE
        if end > at and starts_line and (end == len(tokens) or tokens[end][0] == "NEWLINE"):
            at = end + 1
            continue
        kept.extend(tokens[at:max(end, at + 1)])
        at = max(end, at + 1)
    return kept
