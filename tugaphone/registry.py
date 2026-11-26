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

import functools
import warnings
from typing import Dict, List, Optional, Tuple

from linguatag import closest_lang, parse_tag, with_default_region
from orthography2ipa import ancestry_chain, available_codes, resolve, resolves_exactly


#: Lects written in another orthography, so the modern Portuguese text stages do
#: not apply. orthography2ipa keeps their specs. Barranquenho and
#: Galician-Portuguese fall outside the prefixes; for Barranquenho, use
#: ``orthography2ipa.G2P("ext-PT-x-barranco")``.
_OWN_ORTHOGRAPHY = frozenset({"pt-PT-x-medieval"})

# No Portuguese-family spec is a clade node, so the list keeps clades:
# filtering them out loads every spec orthography2ipa ships.
_CANONICAL: List[str] = sorted(
    c for c in available_codes(include_clades=True)
    if parse_tag(c).language == "pt" and c not in _OWN_ORTHOGRAPHY
)
_CANONICAL_SET = set(_CANONICAL)


#: Legacy / convenience codes → the orthography2ipa lect that answers for them.
_ALIASES: Dict[str, str] = {
    "pt-PT-x-lisboa": "pt-PT-x-lisbon",
    "pt-PT-x-acores": "pt-PT-x-acores",
    "pt-PT-x-azores": "pt-PT-x-acores",
    "pt-PT-x-sao-miguel": "pt-PT-x-sao-miguel",
    "pt-PT-x-north": "pt-PT-x-minho",
    "pt-PT-x-norte": "pt-PT-x-minho",
    "pt-PT-x-fafe": "pt-PT-x-minho",
    "pt-PT-x-famalicao": "pt-PT-x-viana",
    "pt-PT-x-transmontano": "pt-PT-x-tras-os-montes",
    "pt-PT-x-tras-os-montes": "pt-PT-x-tras-os-montes",
    "pt-PT-x-central": "pt-PT-x-coimbra",
    "pt-BR-x-sao-paulo": "pt-BR-x-sp",
    "pt-BR-x-rio-janeiro": "pt-BR-x-rj",
    "pt-BR-x-rio": "pt-BR-x-rj",
    "pt-BR-x-rio-grande-do-sul": "pt-BR-x-sul",
    "pt-BR-x-rio-grande-do-norte": "pt-BR",
    # The orthography2ipa notes for pt-PT-x-terceira call it "the best-described
    # member of the CENTRAL group of the Azores (Terceira, Graciosa, São Jorge,
    # Pico, Faial)", so each central island takes it. São Miguel has its own lect.
    "pt-PT-x-acores-sao-miguel": "pt-PT-x-sao-miguel",
    "pt-PT-x-acores-terceira": "pt-PT-x-terceira",
    "pt-PT-x-acores-faial": "pt-PT-x-terceira",
    "pt-PT-x-acores-pico": "pt-PT-x-terceira",
    "pt-PT-x-acores-sao-jorge": "pt-PT-x-terceira",
    "pt-PT-x-acores-graciosa": "pt-PT-x-terceira",
    "pt-PT-x-azores-sao-miguel": "pt-PT-x-sao-miguel",
    "pt-PT-x-azores-terceira": "pt-PT-x-terceira",
    "pt-PT-x-azores-faial": "pt-PT-x-terceira",
    "pt-PT-x-azores-pico": "pt-PT-x-terceira",
    "pt-PT-x-azores-sao-jorge": "pt-PT-x-terceira",
    "pt-PT-x-azores-graciosa": "pt-PT-x-terceira",
}


#: Lects that take a packaged orthography2ipa lexicon. ``o2i-lexicons`` ships a
#: residual lexicon for ``pt-PT`` and for ``pt-BR``: the words the lect's rules
#: get wrong, as exceptions and patches, and tugaphone takes both. A sub-lect
#: does not take it, because it would overwrite that spec's phonology with the
#: parent's forms. Every other lect runs on the rules alone.
PACKAGED_LEXICON_LECTS = frozenset({"pt-PT", "pt-BR"})



def resolve_lect(lang: str = "pt-PT") -> str:
    """Resolve ``lang`` to the orthography2ipa lect code that answers for it.

    A legacy alias or the code itself, each matched exactly against the
    canonical codes or the old keys orthography2ipa keeps as aliases. A legacy
    alias followed by more subtags takes the alias's lect, with trailing subtags
    removed one at a time (``pt-PT-x-lisboa-foo`` → ``pt-PT-x-lisbon``). Any
    other code takes the nearest lect (``pt-PT-x-unknown`` → ``pt-PT``). A code with
    no nearby lect falls back to ``pt-PT``, preserving the European Portuguese
    default. A code that does not name a lect itself warns, because the caller
    gets another variety.
    """
    lect, named = _resolve(lang)
    if not named:
        warnings.warn(f"{lang!r} is not a tugaphone lect; using {lect}",
                      stacklevel=2)
    return lect


def is_supported(lang: str) -> bool:
    """Whether ``lang`` names a tugaphone lect, itself or through an alias.

    A tag that :func:`resolve_lect` answers only by its fallback is not
    supported: another language (``en-US``), a lect written in another
    orthography (``pt-PT-x-medieval``, Barranquenho) and an unknown sub-tag
    (``pt-PT-x-unknown``) all return ``False``.
    """
    return _resolve(lang)[1]


@functools.lru_cache(maxsize=4096)
def _resolve(lang: str) -> Tuple[str, bool]:
    """The lect that answers for ``lang`` and whether ``lang`` names it."""
    tag = with_default_region((lang or "").strip())
    code = _ALIASES.get(tag, tag)
    if code in _CANONICAL_SET:
        return code, True
    # A code orthography2ipa renamed reaches its spec through the exact alias
    # orthography2ipa keeps for the old key; nearest-language guessing never
    # counts as a match.
    if resolves_exactly(code) and (lect := resolve(code)) in _CANONICAL_SET:
        return lect, True
    prefix = tag.rpartition("-")[0]
    while prefix and prefix not in _ALIASES:
        prefix = prefix.rpartition("-")[0]
    if prefix:
        return resolve(_ALIASES[prefix]), False
    return closest_lang(tag, _CANONICAL, lects="standard") or "pt-PT", False




def list_dialects() -> List[str]:
    """Every canonical dialect code (the Portuguese-family orthography2ipa specs)."""
    return list(_CANONICAL)


#: The AO1990 norm of each national standard, in desacordo_ortografico's names.
_SPELLING_NORMS: Dict[str, str] = {"pt-PT": "ao1990-pt", "pt-BR": "ao1990-br"}


@functools.lru_cache(maxsize=None)
def spelling_norm(lect: str) -> str:
    """The AO1990 norm whose spelling ``lect`` reads: ``ao1990-pt`` or ``ao1990-br``.

    A lect follows the norm of the nearest of ``pt-PT`` and ``pt-BR`` in its
    orthography2ipa lineage, itself included. The European sub-lects and the
    African and Asian lects descend from ``pt-PT``; the Brazilian sub-lects and
    ``pt-UY`` descend from ``pt-BR``. A lect under neither raises ``ValueError``.
    """
    for code in (lect, *ancestry_chain(lect)):
        if code in _SPELLING_NORMS:
            return _SPELLING_NORMS[code]
    raise ValueError(f"{lect!r} descends from neither pt-PT nor pt-BR")


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
