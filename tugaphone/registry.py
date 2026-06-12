"""Dialect registry: resolve BCP-47 language codes to inventories and presets.

Maps every supported language code — the five major Lusophone dialects, the
city-level inventories and the regional accent presets — to a
:class:`~tugaphone.dialects.DialectInventory` class and, where one applies, a
:class:`~tugaphone.regional.RegionalTransforms` preset. Regional accents use
BCP-47 private-use subtags (``pt-PT-x-porto``), the convention shared across
the phonetics stack.

    >>> from tugaphone.registry import resolve_dialect, list_dialects
    >>> resolve_dialect("pt-PT-x-porto").transforms is not None
    True
    >>> "pt-BR-x-sao-paulo" in list_dialects()
    True
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from tugaphone.dialects import (DialectInventory, EuropeanPortuguese,
                                LisbonPortuguese, BrazilianPortuguese,
                                RioJaneiroPortuguese, SaoPauloPortuguese,
                                AngolanPortuguese, MozambicanPortuguese,
                                TimoresePortuguese)
from tugaphone.regional import (RegionalTransforms, NorthernDialect,
                                PortoDialect, MinhoDialect, BragaDialect,
                                FamalicaoDialect, FafeDialect,
                                TrasMontanoDialect, CoimbraDialect,
                                AlentejoDialect, AlgarveDialect,
                                MadeiraDialect, AzoresDialect)


@dataclass(frozen=True)
class DialectEntry:
    """A registered dialect: its canonical code, inventory and optional preset.

    Attributes:
        code: Canonical BCP-47 tag (private-use subtags for regional accents).
        inventory: :class:`DialectInventory` subclass; called to get a fresh
            inventory instance on every resolution.
        transforms: Regional accent preset applied on top of the inventory,
            or ``None`` when the inventory alone defines the dialect.
        region: Human-readable label.
        aliases: Alternative codes that resolve to this entry.
    """
    code: str
    inventory: Callable[[], DialectInventory]
    transforms: Optional[RegionalTransforms] = None
    region: str = ""
    aliases: Tuple[str, ...] = ()


_ENTRIES: Tuple[DialectEntry, ...] = (
    # Major Lusophone dialects — inventory-defined.
    DialectEntry("pt-PT", EuropeanPortuguese, region="Portugal (Lisbon standard)",
                 aliases=("pt",)),
    DialectEntry("pt-BR", BrazilianPortuguese, region="Brazil"),
    DialectEntry("pt-AO", AngolanPortuguese, region="Angola (Luanda)"),
    DialectEntry("pt-MZ", MozambicanPortuguese, region="Mozambique (Maputo)"),
    DialectEntry("pt-TL", TimoresePortuguese, region="Timor-Leste"),
    # City-level inventories backed by their own lexicon region maps.
    DialectEntry("pt-PT-x-lisbon", LisbonPortuguese, region="Lisbon",
                 aliases=("pt-PT-x-lisboa",)),
    DialectEntry("pt-BR-x-rio-janeiro", RioJaneiroPortuguese,
                 region="Rio de Janeiro", aliases=("pt-BR-x-rio",)),
    DialectEntry("pt-BR-x-sao-paulo", SaoPauloPortuguese, region="São Paulo"),
    # Regional accent presets — grounded rule compositions over the
    # European Portuguese base (see tugaphone.regional).
    DialectEntry("pt-PT-x-north", EuropeanPortuguese, NorthernDialect,
                 region="Northern Portugal", aliases=("pt-PT-x-norte",)),
    DialectEntry("pt-PT-x-porto", EuropeanPortuguese, PortoDialect,
                 region="Porto / Douro Litoral"),
    DialectEntry("pt-PT-x-minho", EuropeanPortuguese, MinhoDialect,
                 region="Minho"),
    DialectEntry("pt-PT-x-braga", EuropeanPortuguese, BragaDialect,
                 region="Braga"),
    DialectEntry("pt-PT-x-famalicao", EuropeanPortuguese, FamalicaoDialect,
                 region="Vila Nova de Famalicão"),
    DialectEntry("pt-PT-x-fafe", EuropeanPortuguese, FafeDialect,
                 region="Fafe"),
    DialectEntry("pt-PT-x-transmontano", EuropeanPortuguese, TrasMontanoDialect,
                 region="Trás-os-Montes", aliases=("pt-PT-x-tras-os-montes",)),
    DialectEntry("pt-PT-x-coimbra", EuropeanPortuguese, CoimbraDialect,
                 region="Coimbra / Centro-Litoral", aliases=("pt-PT-x-central",)),
    DialectEntry("pt-PT-x-alentejo", EuropeanPortuguese, AlentejoDialect,
                 region="Alentejo"),
    DialectEntry("pt-PT-x-algarve", EuropeanPortuguese, AlgarveDialect,
                 region="Algarve"),
    DialectEntry("pt-PT-x-madeira", EuropeanPortuguese, MadeiraDialect,
                 region="Madeira"),
    DialectEntry("pt-PT-x-azores", EuropeanPortuguese, AzoresDialect,
                 region="Açores (São Miguel)", aliases=("pt-PT-x-acores",)),
)

DIALECT_REGISTRY: Dict[str, DialectEntry] = {e.code.lower(): e for e in _ENTRIES}
_ALIAS_INDEX: Dict[str, DialectEntry] = {
    alias.lower(): e for e in _ENTRIES for alias in e.aliases
}


def normalize_dialect_code(lang: str) -> str:
    """Normalize the casing of a BCP-47 tag (``PT-pt-X-PORTO`` → ``pt-PT-x-porto``).

    The language subtag is lowercased, two-letter region subtags are
    uppercased, and everything else (including the ``x`` private-use marker
    and its subtags) is lowercased. The tag structure is not validated.
    """
    segments = (lang or "").strip().split("-")
    normalized = []
    for i, seg in enumerate(segments):
        if i > 0 and len(seg) == 2 and seg.lower() != "x":
            normalized.append(seg.upper())
        else:
            normalized.append(seg.lower())
    return "-".join(normalized)


def resolve_dialect(lang: str = "pt-PT") -> DialectEntry:
    """Resolve a language code to its :class:`DialectEntry`.

    Resolution order: exact canonical code, then alias, both
    case-insensitive. Unknown codes fall back by popping trailing subtags
    (``pt-PT-x-unknown`` → ``pt-PT``); anything still unmatched resolves to
    ``pt-PT``, preserving the European Portuguese default.
    """
    key = normalize_dialect_code(lang).lower()
    while key:
        entry = DIALECT_REGISTRY.get(key) or _ALIAS_INDEX.get(key)
        if entry is not None:
            return entry
        if "-" not in key:
            break
        key = key.rsplit("-", 1)[0]
    return DIALECT_REGISTRY["pt-pt"]


def get_dialect_inventory(lang: str = "pt-PT") -> DialectInventory:
    """Return a fresh :class:`DialectInventory` for ``lang``."""
    return resolve_dialect(lang).inventory()


def get_regional_transforms(lang: str = "pt-PT") -> Optional[RegionalTransforms]:
    """Return the regional accent preset for ``lang``, or ``None``."""
    return resolve_dialect(lang).transforms


def list_dialects() -> List[str]:
    """Return all canonical dialect codes, sorted. Aliases are not listed."""
    return sorted(e.code for e in _ENTRIES)
