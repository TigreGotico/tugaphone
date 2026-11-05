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
* **lexicon** — for ``pt-PT`` and ``pt-BR``, the engine takes the residual
  lexicon of ``o2i-lexicons`` through its :class:`orthography2ipa.Pipeline`, so
  a covered word folds into the *same* override path as a spec
  ``word_exceptions`` entry. It holds only the words the lect's rules get
  wrong. Every other lect runs on the rules alone. The lexicon belongs to the
  engine, so a plain :class:`orthography2ipa.G2P` in the same process stays on
  the rules;
* **syllabification** — orthography2ipa's bundled splitter, which reads the
  diphthongs and hiatus of the lect spec.
"""
from __future__ import annotations

import functools
from typing import List, Optional

from orthography2ipa import G2P, Pipeline, packaged_lexicon
from orthography2ipa.syllabifier_plugin import SyllabifierPlugin

from tugaphone.codeswitch import split_runs, transcribe_contact
from tugaphone.number_utils import normalize_numbers
from tugaphone.registry import PACKAGED_LEXICON_LECTS, default_contact, resolve_lect
from tugaphone.text_normalization import normalize_orthography

_VALID_CONTACT = ("auto", "es", "fr", "en", "none")

try:  # bifonia is a hard dependency, but keep the import failure legible
    from bifonia import add_extra_diacritics as _mark_heterophones
except Exception:  # pragma: no cover - exercised only on a broken install
    def _mark_heterophones(sentence: str, lang: str = "pt-PT") -> str:
        return sentence


class _BundledSplitter(SyllabifierPlugin):
    """Sends every word to the bundled splitter of orthography2ipa.

    A pipeline with no syllabifier takes the plugin that discovery finds, and
    ``silabificador`` is installed for :mod:`tugaphone.tokenizer`.
    """

    @property
    def language_codes(self) -> List[str]:
        return []

    def syllabify(self, word: str, lang: Optional[str] = None) -> List[str]:
        return []


def _normalizer(lect: str):
    """The orthography2ipa ``normalize`` callable tugaphone supplies for ``lect``.

    Orthographic rewrites (ranges, clock times, European number separators,
    abbreviations, regnal numerals, letter-spelled acronyms) run first, since
    they produce the digit tokens and words number verbalization then reads;
    numbers and ordinals are verbalized next (so their spelled-out words are
    then available to homograph marking); heterophonic homographs are marked
    last, with ``lect`` selecting bifonia's per-lect marks (every ``pt-BR``
    sub-lect takes the Brazilian ones). All three stages are orthographic,
    pre-lattice transformations.
    """

    def normalize(text: str) -> str:
        text = normalize_numbers(normalize_orthography(text, lect), lect)
        return _mark_heterophones(text, lect)

    return normalize


@functools.lru_cache(maxsize=None)
def engine(lect: str) -> G2P:
    """A cached orthography2ipa engine for ``lect`` with tugaphone's layers.

    ``lect`` must already be an orthography2ipa lect code (see
    :func:`tugaphone.registry.resolve_lect`). The engine holds the lect's
    packaged lexicon and the number/homograph normalizer. A lect with no packaged
    lexicon gets an empty one, so only the rules answer it.
    """
    lexicon = packaged_lexicon(lect) if lect in PACKAGED_LEXICON_LECTS else {}
    return G2P(lect, normalizer=_normalizer(lect),
               pipeline=Pipeline(lexicon=lexicon, syllabifier=_BundledSplitter()))


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
    """Drop the per-lect engine cache (tests)."""
    engine.cache_clear()
