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
from pathlib import Path
from typing import Dict, Optional

from orthography2ipa import G2P, register_lexicon

from tugaphone.dialects import LEXICON
from tugaphone.number_utils import normalize_numbers
from tugaphone.registry import lexicon_region, resolve_lect

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


def _write_lexicon(region: str, path: Path) -> None:
    ipa_map: Dict[str, str] = LEXICON.get_ipa_map(region=region)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tsv.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for word in sorted(ipa_map):
            fh.write(f"{word}\t{_relayout(ipa_map[word])}\n")
    tmp.replace(path)


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
    if not path.exists():
        _write_lexicon(region, path)
    register_lexicon(lect, str(path))
    _registered.add(lect)


def _normalizer(lect: str):
    """The orthography2ipa ``normalize`` callable tugaphone supplies for ``lect``.

    Numbers and ordinals are verbalized first (so their spelled-out words are
    then available to homograph marking), then heterophonic homographs are
    marked by sense; both are orthographic, pre-lattice transformations.
    """

    def normalize(text: str) -> str:
        return _mark_heterophones(normalize_numbers(text, lect))

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


def phonemize(text: str, lang: str = "pt-PT") -> str:
    """Phonemize ``text`` for ``lang`` through the orthography2ipa lattice."""
    lect = resolve_lect(lang)
    return engine(lect).transcribe(text)


def clear_caches() -> None:
    """Drop the per-lect engine and lexicon-registration caches (tests)."""
    engine.cache_clear()
    _registered.clear()
