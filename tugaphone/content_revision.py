"""``tugaphone==<version>``, then the installed dependencies as ``<Name>==<version>`` sorted by name, joined by ``;``."""
from __future__ import annotations

from functools import cache
from importlib.metadata import PackageNotFoundError, metadata, requires

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def revision(lang: str = "pt-PT") -> str:
    """``tugaphone==<version>`` first, then ``<Name>==<version>`` for each installed dependency.

    The dependencies are sorted by canonical name, and each name is spelled as the distribution metadata spells it.
    The value is the same for every ``lang``. A dependency that is not installed, or that an extra or a false
    environment marker excludes, is left out.
    """
    return _revision()


@cache
def _revision() -> str:
    names = {canonicalize_name(Requirement(line).name) for line in requires("tugaphone") or ()
             if Requirement(line).marker is None or Requirement(line).marker.evaluate({"extra": ""})}
    pins = []
    for name in sorted(names - {"tugaphone"}):
        try:
            pins.append(_pin(name))
        except PackageNotFoundError:
            pass
    return ";".join([_pin("tugaphone"), *pins])


def _pin(name: str) -> str:
    found = metadata(name)
    return f"{found['Name']}=={found['Version']}"
