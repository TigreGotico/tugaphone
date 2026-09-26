"""The orthography2ipa lattice as tugaphone's core phonemization pipeline.

tugaphone phonemizes by driving the shared orthography2ipa candidate lattice
(:class:`orthography2ipa.G2P`) and layering on top only the concerns
orthography2ipa deliberately does not own. Dialect selection *is* the choice of
orthography2ipa lect spec: every ``pt-*`` variety ships an engine spec whose
grapheme table, ``allophone_rules`` and ``sandhi_rules`` encode that variety's
phonology, so the dialect phenomena that were once re-implemented as post-hoc
string edits (betacism, Porto rising diphthongs, Madeiran ``/l/``
palatalisation, Azorean ``/u/`` fronting, coda-sibilant sandhi, …) are produced
by the lattice itself.

What tugaphone adds sits in the stages orthography2ipa leaves to the caller,
wired through orthography2ipa's own extension points rather than bolted on after
the fact:

* **normalization + verbalization** — gender-aware number/ordinal expansion
  (:mod:`tugaphone.number_utils`) and sense-based heterophone marking
  (:mod:`bifonia`) run as the engine's ``normalizer``, i.e. before the lattice
  sees the text (orthography2ipa's ``normalize`` stage);
* **lexicon** — the curated Portuguese pronunciation lexicon (``tugalex``) is
  registered per lect through :func:`orthography2ipa.register_lexicon`, so a
  covered word folds into the *same* override path as a spec ``word_exceptions``
  entry; lattice generation runs only for the words the lexicon does not cover;
* **syllabification** — supplied by orthography2ipa's own ``silabificador``
  ``syllabify`` plugin (a neutral stage), so stress lands on the same syllable
  tugaphone would have chosen.

The lexicon is transcribed in a narrower tradition than the specs' broad
inventory, so its entries are relaid into the spec's stress-before-syllable
layout on registration (:func:`_relayout`) to keep a sentence's IPA internally
consistent.
"""
from __future__ import annotations

import functools
import os
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path
from typing import Dict, Optional

from typing import List

from orthography2ipa import G2P, register_lexicon

from tugaphone.codeswitch import split_runs, transcribe_contact
from tugaphone.dialects import LEXICON
from tugaphone.number_utils import normalize_numbers
from tugaphone.registry import default_contact, lexicon_region, resolve_lect
from tugaphone.text_normalization import normalize_orthography

_VALID_CONTACT = ("auto", "es", "fr", "en", "none")

try:  # bifonia is a hard dependency, but keep the import failure legible
    from bifonia import add_extra_diacritics as _mark_heterophones
except Exception:  # pragma: no cover - exercised only on a broken install
    def _mark_heterophones(sentence: str) -> str:
        return sentence


#: Where the per-lect lexicon TSVs handed to orthography2ipa are materialised.
_LEXICON_CACHE = Path(
    os.environ.get(
        "TUGAPHONE_LEXICON_DIR",
        os.path.join(
            os.environ.get(
                "XDG_CACHE_HOME", os.path.expanduser("~/.cache")
            ),
            "tugaphone",
            "lexicon",
        ),
    )
)

_STRESS_MARKS = ("ˈ", "ˌ")
_SYLLABLE_JOINER = "·"


def _relayout(ipa: str) -> str:
    """Relay a ``·``-joined, nucleus-marked lexicon entry into spec layout.

    ``tugalex`` writes a stress mark immediately before the stressed nucleus and
    joins syllables with ``·`` (``gˈa·tʊ``). orthography2ipa marks stress at the
    onset of the stressed syllable and writes no syllable joiner (``ˈgatʊ``).
    Relaying keeps a lexicon hit and a lattice-generated word in one notation.
    """
    syllables = ipa.split(_SYLLABLE_JOINER)
    out = []
    for syllable in syllables:
        for mark in _STRESS_MARKS:
            if mark in syllable:
                syllable = mark + syllable.replace(mark, "")
        out.append(syllable)
    return "".join(out)


def _tugalex_version() -> str:
    """The installed tugalex version, or ``"0"`` when it can't be resolved.

    Used as the cache-invalidation key so a materialised TSV is tied to the
    tugalex data that produced it, not just the lect name.
    """
    try:
        return _pkg_version("tugalex")
    except PackageNotFoundError:  # pragma: no cover - exercised only on a broken install
        return "0"


def _stamp_path(path: Path) -> Path:
    return path.with_suffix(".version")


def _write_lexicon(region: str, path: Path) -> None:
    ipa_map: Dict[str, str] = LEXICON.get_ipa_map(region=region)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tsv.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for word in sorted(ipa_map):
            fh.write(f"{word}\t{_relayout(ipa_map[word])}\n")
    tmp.replace(path)
    _stamp_path(path).write_text(_tugalex_version(), encoding="utf-8")


def _is_stale(path: Path) -> bool:
    """Whether the materialised TSV at ``path`` needs to be rewritten.

    True when the file is missing, empty (a previous write got interrupted),
    or was materialised from a different tugalex version than is installed
    now — the case that otherwise lets a tugalex data fix never reach an
    installation that already has the TSV.
    """
    if not path.exists() or path.stat().st_size == 0:
        return True
    stamp = _stamp_path(path)
    try:
        return stamp.read_text(encoding="utf-8").strip() != _tugalex_version()
    except OSError:
        return True


_registered: set = set()


def _ensure_lexicon(lect: str) -> None:
    """Register the tugalex lexicon for ``lect`` with orthography2ipa, once."""
    if lect in _registered:
        return
    region = lexicon_region(lect)
    if region is None:
        _registered.add(lect)
        return
    path = _LEXICON_CACHE / f"{lect}.tsv"
    if _is_stale(path):
        _write_lexicon(region, path)
    register_lexicon(lect, str(path))
    _registered.add(lect)


def _normalizer(lect: str):
    """The orthography2ipa ``normalize`` callable tugaphone supplies for ``lect``.

    Orthographic rewrites (ranges, clock times, European number separators,
    abbreviations, regnal numerals, letter-spelled acronyms) run first, since
    they produce the digit tokens and words number verbalization then reads;
    numbers and ordinals are verbalized next (so their spelled-out words are
    then available to homograph marking); heterophonic homographs are marked
    last. All three stages are orthographic, pre-lattice transformations.
    """

    def normalize(text: str) -> str:
        return _mark_heterophones(normalize_numbers(normalize_orthography(text), lect))

    return normalize


@functools.lru_cache(maxsize=None)
def engine(lect: str) -> G2P:
    """A cached orthography2ipa engine for ``lect`` with tugaphone's layers.

    ``lect`` must already be an orthography2ipa lect code (see
    :func:`tugaphone.registry.resolve_lect`); the lexicon is registered and the
    number/homograph normalizer attached before the engine is built.
    """
    _ensure_lexicon(lect)
    return G2P(lect, normalizer=_normalizer(lect))


def _validate_contact(contact: str) -> None:
    if contact not in _VALID_CONTACT:
        raise ValueError(
            f"unknown contact {contact!r}; expected one of {_VALID_CONTACT}")


def phonemize(text: str, lang: str = "pt-PT", contact: str = "none") -> str:
    """Phonemize ``text`` for ``lang`` through the orthography2ipa lattice.

    Portuguese tokens are transcribed by the ``lang`` lattice (numbers verbalized
    by the normalizer, cross-word sandhi preserved within contiguous Portuguese
    runs); detected contact-language tokens are transcribed through the
    ``es-ES``/``fr-FR``/``en-US`` lattice and nativized onto the Portuguese
    inventory (see :mod:`tugaphone.codeswitch`). ``contact`` is one of ``auto``
    (detect and classify each contact word among es/fr/en, unclassified words
    falling to the dialect's side), ``es``, ``fr``, ``en`` or ``none`` (the
    default: disable switching — the engine-only, behaviour-preserving path).
    """
    _validate_contact(contact)
    lect = resolve_lect(lang)
    if contact == "none":
        return engine(lect).transcribe(text)

    side = default_contact(lect)
    runs = split_runs(text, contact, default_side=side)
    out: List[str] = []
    # Transcribe contiguous Portuguese tokens as one phrase to preserve sandhi;
    # nativize each contact token individually.
    pt_buffer: List[str] = []

    def flush() -> None:
        if pt_buffer:
            out.append(engine(lect).transcribe(" ".join(pt_buffer)))
            pt_buffer.clear()

    for contact_lang, token in runs:
        if contact_lang is not None:
            flush()
            out.append(transcribe_contact(token, contact_lang))
        else:
            pt_buffer.append(token)
    flush()
    return " ".join(p for p in out if p)


def clear_caches() -> None:
    """Drop the per-lect engine and lexicon-registration caches (tests)."""
    engine.cache_clear()
    _registered.clear()
