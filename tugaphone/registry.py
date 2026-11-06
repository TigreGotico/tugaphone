"""Dialect registry: resolve language codes to orthography2ipa lect specs.

A tugaphone dialect *is* an orthography2ipa lect spec. The canonical dialect
set is therefore the Portuguese-family specs orthography2ipa ships
(:func:`orthography2ipa.available_codes`), reachable by their BCP-47 codes —
the five national standards, the European and Brazilian sub-regional varieties,
the African and Asian lects, and the historical/contact varieties.

    >>> from tugaphone.registry import resolve_lect, list_dialects
    >>> resolve_lect("pt-PT-x-porto")
    'pt-PT-x-porto'
    >>> "pt-BR-x-sp" in list_dialects()
    True

Legacy tugaphone accent codes (``pt-PT-x-azores``, ``pt-BR-x-sao-paulo``, …)
resolve to their orthography2ipa equivalents through :data:`_ALIASES`.
"""
from __future__ import annotations

import warnings
from typing import Dict, List, Optional

from orthography2ipa import available_codes, resolve, resolves_exactly

from tugaphone.version import VERSION_MAJOR

#: Portuguese-family lect codes orthography2ipa ships, the canonical dialects.
_PT_PREFIXES = ("pt-", "pt_")

#: Lects written in another orthography, so the modern Portuguese text stages do
#: not apply. orthography2ipa keeps their specs. Barranquenho and
#: Galician-Portuguese fall outside the prefixes; ``g2p_barranquenho`` reads the
#: first.
_OWN_ORTHOGRAPHY = frozenset({"pt-PT-x-medieval"})


def _canonical_codes() -> List[str]:
    return sorted(
        c for c in available_codes()
        if c.startswith(_PT_PREFIXES) and c not in _OWN_ORTHOGRAPHY
    )


_CANONICAL: List[str] = _canonical_codes()
_CANONICAL_SET = set(_CANONICAL)


#: Legacy / convenience codes → the orthography2ipa lect that answers for them.
_ALIASES: Dict[str, str] = {
    "pt": "pt-PT",
    "pt-pt-x-lisboa": "pt-PT-x-lisbon",
    "pt-pt-x-acores": "pt-PT-x-acores",
    "pt-pt-x-azores": "pt-PT-x-acores",
    "pt-pt-x-sao-miguel": "pt-PT-x-sao-miguel",
    "pt-pt-x-north": "pt-PT-x-minho",
    "pt-pt-x-norte": "pt-PT-x-minho",
    "pt-pt-x-fafe": "pt-PT-x-minho",
    "pt-pt-x-famalicao": "pt-PT-x-viana",
    "pt-pt-x-transmontano": "pt-PT-x-trasosmontes",
    "pt-pt-x-tras-os-montes": "pt-PT-x-trasosmontes",
    "pt-pt-x-central": "pt-PT-x-coimbra",
    "pt-br-x-sao-paulo": "pt-BR-x-sp",
    "pt-br-x-rio-janeiro": "pt-BR-x-rj",
    "pt-br-x-rio": "pt-BR-x-rj",
}


#: Lects that take a packaged orthography2ipa lexicon. ``o2i-lexicons`` ships a
#: residual lexicon for ``pt-PT`` and for ``pt-BR``: the words the lect's rules
#: get wrong. It is not enabled for a sub-lect, because it would overwrite that
#: spec's phonology with the parent's forms. Every other lect runs on the rules
#: alone.
PACKAGED_LEXICON_LECTS = frozenset({"pt-PT", "pt-BR"})

#: The release that removes :func:`lexicon_region`.
LEXICON_REGION_REMOVAL_VERSION = f"{VERSION_MAJOR + 1}.0.0"


def normalize_dialect_code(lang: str) -> str:
    """Normalize the casing of a BCP-47 tag (``PT-pt-X-PORTO`` → ``pt-PT-x-porto``).

    The language subtag is lowercased, two-letter region subtags are
    uppercased, and everything else (the ``x`` private-use marker and its
    subtags) is lowercased. The tag structure is not validated.
    """
    segments = (lang or "").strip().split("-")
    normalized = []
    in_private_use = False
    for i, seg in enumerate(segments):
        low = seg.lower()
        if low == "x":
            in_private_use = True
            normalized.append(low)
        elif i > 0 and len(seg) == 2 and not in_private_use:
            normalized.append(seg.upper())
        else:
            normalized.append(low)
    return "-".join(normalized)


def resolve_lect(lang: str = "pt-PT") -> str:
    """Resolve ``lang`` to the orthography2ipa lect code that answers for it.

    Resolution order: a legacy alias, then the code itself, each matched
    exactly against the canonical codes or the old keys orthography2ipa keeps
    as aliases, then a progressive pop of trailing subtags
    (``pt-PT-x-unknown`` → ``pt-PT``). An unresolved code falls back to
    ``pt-PT``, preserving the European Portuguese default. A code that does not
    name a lect itself warns, because the caller gets another variety.
    """
    canon = normalize_dialect_code(lang).lower()
    key = canon
    lect = None
    while key and not (lect := _registered(_ALIASES.get(key, key))):
        key = key.rpartition("-")[0]
    resolved = lect or "pt-PT"
    if key != canon or lect is None:
        warnings.warn(f"{lang!r} is not a tugaphone lect; using {resolved}",
                      stacklevel=2)
    return resolved


def _registered(code: str) -> Optional[str]:
    """The canonical dialect that ``code`` names exactly, or ``None``.

    Canonical codes compare case-insensitively. A code orthography2ipa renamed
    reaches its spec through the exact alias orthography2ipa keeps for the old
    key; nearest-language guessing never counts as a match.
    """
    folded = code.lower()
    for lect in _CANONICAL:
        if lect.lower() == folded:
            return lect
    if resolves_exactly(code) and (lect := resolve(code)) in _CANONICAL_SET:
        return lect
    return None


def lexicon_region(lect: str) -> Optional[str]:
    """Deprecated: the ``tugalex`` region whose lexicon overlays ``lect``.

    No lect takes a ``tugalex`` region map, so the answer is ``None`` for every
    lect. :data:`PACKAGED_LEXICON_LECTS` names the lects that take a lexicon.
    """
    warnings.warn(
        "lexicon_region() is deprecated and returns None: no lect takes a "
        "tugalex region map. Use PACKAGED_LEXICON_LECTS. It will be removed in "
        f"tugaphone {LEXICON_REGION_REMOVAL_VERSION}.",
        DeprecationWarning,
        stacklevel=2,
    )
    return None


def list_dialects() -> List[str]:
    """Every canonical dialect code (the Portuguese-family orthography2ipa specs)."""
    return list(_CANONICAL)


#: Lects that embed Spanish rather than English by default. ``pt-UY`` is
#: Uruguayan border Portuguese (*portunhol*), in daily contact with Spanish.
_SPANISH_CONTACT_LECTS = frozenset({"pt-UY"})


def default_contact(lect: str) -> str:
    """The default code-switch contact language for ``lect``.

    English is the dominant loan source across the Lusophone world — the
    Brazilian tech/media register especially — so it is the default side an
    unclassified contact word falls to. The Uruguayan border lect (``pt-UY``,
    *portunhol*) embeds Spanish instead.
    """
    return "es" if lect in _SPANISH_CONTACT_LECTS else "en"


# --------------------------------------------------------------------------
# Backwards-compatible shims (deprecated).
# --------------------------------------------------------------------------

def get_dialect_inventory(lang: str = "pt-PT"):
    """A tugaphone :class:`~tugaphone.dialects.DialectInventory` for ``lang``.

    Retained for the rules-only benchmark baseline and the token-feature API,
    which read the private grapheme cascade rather than the lattice. The
    phonemization path (:func:`tugaphone.lattice_core.phonemize`) no longer uses
    it. The nearest national inventory is chosen from the resolved lect family.
    """
    from tugaphone.dialects import (EuropeanPortuguese, BrazilianPortuguese,
                                    AngolanPortuguese, MozambicanPortuguese,
                                    TimoresePortuguese)

    lect = resolve_lect(lang)
    if lect.startswith("pt-BR"):
        return BrazilianPortuguese()
    if lect == "pt-AO":
        return AngolanPortuguese()
    if lect == "pt-MZ":
        return MozambicanPortuguese()
    if lect == "pt-TL":
        return TimoresePortuguese()
    return EuropeanPortuguese()


def resolve_dialect(lang: str = "pt-PT") -> str:
    """Deprecated alias for :func:`resolve_lect`.

    .. deprecated::
        A dialect is now an orthography2ipa lect code, not a
        ``DialectEntry``. Use :func:`resolve_lect`.
    """
    import warnings

    warnings.warn(
        "resolve_dialect() is deprecated; a dialect is an orthography2ipa lect "
        "code — use resolve_lect().",
        DeprecationWarning,
        stacklevel=2,
    )
    return resolve_lect(lang)
