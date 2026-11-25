"""The version strings of tugaphone and of its installed dependencies, as one revision string."""
from __future__ import annotations

from functools import cache
from importlib.metadata import PackageNotFoundError, requires, version

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def revision(lang: str = "pt-PT") -> str:
    """``tugaphone==<version>`` and ``<name>==<version>`` for each installed dependency, sorted by name, joined by ``;``.

    The value is the same for every ``lang``. A dependency that is not installed, or that an extra or a false
    environment marker excludes, is left out.
    """
    return _revision()


@cache
def _revision() -> str:
    names = {"tugaphone"}
    for line in requires("tugaphone") or ():
        requirement = Requirement(line)
        if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
            names.add(canonicalize_name(requirement.name))
    pins = []
    for name in sorted(names):
        try:
            pins.append(f"{name}=={version(name)}")
        except PackageNotFoundError:
            pass
    return ";".join(pins)
