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

* **expansion** — the spelling step (:mod:`desacordo_ortografico`), orthographic
  rewrites (:mod:`tugaphone.text_normalization`) and text2spoken, which reads
  numbers, dates, times, money, measures and abbreviations
  (:mod:`tugaphone.number_utils`), run as the pipeline's ``expand``, before the
  lattice sees the text;
* **marks** — sense-based heterophone marking (:mod:`bifonia`) runs as the
  pipeline's ``mark``, on the whole sentence after ``expand``. It adds marks
  and keeps every letter, and the engine checks that;
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
import re
from typing import List

from bifonia import add_extra_diacritics
from desacordo_ortografico import convert as convert_spelling
from orthography2ipa import G2P, Pipeline, packaged_lexicon

from tugaphone.codeswitch import split_runs, transcribe_contact
from tugaphone.registry import (PACKAGED_LEXICON_LECTS, default_contact,
                                list_dialects, resolve_lect, spelling_norm)
from tugaphone.text_normalization import normalize_text

_VALID_CONTACT = ("auto", "es", "fr", "en", "none")

#: The desacordo_ortografico features of the spelling step, per AO1990 norm. The
#: Brazilian group keeps the trema: in a 1943 or 1971 text it is the only mark of
#: a pronounced u (sangüíneo), and G2P cannot recover that u from the AO1990 form.
#: It also leaves out ptbr-divergence, which picks one form of a VOLP dual
#: (epilético → epiléptico); AO1990 Base IV 1.º c) leaves that choice to the writer.
SPELLING_FEATURES = {
    "ao1990-pt": frozenset({"1911-word-map", "trema", "ao-map-consonant", "base-iv",
                            "initial-sc", "ao-map-diacritic"}),
    "ao1990-br": frozenset({"1911-word-map", "base-iv", "initial-sc", "hyphen-lexical"}),
}

#: A word token, the same shape desacordo_ortografico's rules use, so the extra
#: Brazilian step below rewrites words without touching punctuation or spacing.
_WORD_RE = re.compile(r"[0-9A-Za-zÀ-ɏ]+(?:[-'’][0-9A-Za-zÀ-ɏ]+)*")


def _is_single_e_acute(word: str, restored: str) -> bool:
    """Whether ``restored`` differs from ``word`` only by one ``e`` → ``é``."""
    if len(word) != len(restored):
        return False
    diffs = [(a, b) for a, b in zip(word, restored) if a != b]
    if len(diffs) != 1:
        return False
    a, b = diffs[0]
    return a.lower() == "e" and b.lower() == "é"


def _open_ei_diphthong(text: str) -> str:
    """Re-accent the open ``éi`` AO1990 Base IX 3.º dropped in Brazilian paroxytones.

    For each word that holds an unaccented ``ei``, the backward conversion toward
    ``br_1971`` gives the pre-AO1990 spelling, which marks the open diphthong. The
    result replaces the word only when it differs from it by exactly one ``e`` → ``é``:
    a closed ``ei`` word (``feia``) and any word whose conversion changes more than
    that accent stay as written. desacordo_ortografico holds only the singular of these
    words, so a plural that ends in ``s`` (``ideias``) converts unchanged: its stem is
    tried instead, and the final letter is reattached to the restored stem.
    """

    def rewrite(match: re.Match) -> str:
        word = match.group(0)
        if "ei" not in word.lower():
            return word
        restored = convert_spelling(word, "ao1990-br", "br_1971")
        if _is_single_e_acute(word, restored):
            return restored
        if restored == word and word.endswith(("s", "S")):
            stem = word[:-1]
            stem_restored = convert_spelling(stem, "ao1990-br", "br_1971")
            if _is_single_e_acute(stem, stem_restored):
                return stem_restored + word[-1]
        return word

    return _WORD_RE.sub(rewrite, text)


def normalize_spelling(text: str, lect: str) -> str:
    """Rewrite the old spellings of ``text`` in the AO1990 norm of ``lect``.

    "A acção da pharmacia" becomes "A ação da farmácia". Case and punctuation
    stay. Modern text stays as written, the dual forms included (pt-PT sector,
    pt-BR facto), with these changes:

    * a name in an old spelling takes the AO1990 spelling (Sophia → Sofia,
      Rachel → Raquel), although AO1990 Base XXI lets a name keep its spelling;
    * for the Brazilian lects, the hyphen rules of AO1990 change the word count
      (há-de → há de, manda-chuva → mandachuva);
    * for the Brazilian lects, an AO1990 paroxytone that lost the accent of an
      open ``éi`` (Base IX 3.º) takes its pre-AO1990 spelling, which marks the
      open vowel (ideia becomes idéia).
    """
    norm = spelling_norm(lect)
    text = convert_spelling(text, "etymological", norm, features=SPELLING_FEATURES[norm])
    if norm == "ao1990-br":
        text = _open_ei_diphthong(text)
    return text


def _expander(lect: str):
    """The orthography2ipa ``expand`` callable for ``lect``.

    :func:`normalize_spelling` runs first, so the later stages read AO1990
    text, then :func:`tugaphone.text_normalization.normalize_text` spells out
    the text, so ``mark`` sees words.

    The engine joins the expanded runs and the forced words back into one
    sentence for ``mark``, so the spaces at the ends of a run are kept: the
    rewrites drop them, and a forced word would then fuse with its neighbours.
    """

    def expand(text: str) -> str:
        words = text.strip()
        if not words:
            return text
        lead = text[:len(text) - len(text.lstrip())]
        trail = text[len(text.rstrip()):]
        words = normalize_spelling(words, lect)
        return lead + normalize_text(words, lect) + trail

    return expand


def pipeline(lect: str) -> Pipeline:
    """The orthography2ipa :class:`~orthography2ipa.Pipeline` tugaphone runs for ``lect``.

    ``G2P(lect, pipeline=pipeline(lect)).transcribe(text)`` gives the same
    output as ``phonemize(text, lect)`` with ``contact="none"``. The
    ``contact="auto"`` path sends contact words through the ``es-ES``,
    ``fr-FR`` or ``en-GB`` lattice, and one ``Pipeline`` cannot express that.

    The pipeline holds the lect's packaged lexicon, the number expansion and the
    homograph marks, with ``lect`` selecting bifonia's per-lect marks. The
    packaged lexicon holds the exceptions and the patches of the lect: the
    patches cover the words that a rule could reach and does not reach yet. A
    lect with no packaged lexicon gets an empty one, so only the rules answer it.
    Each call returns a new ``Pipeline``, because the lexicon is a mutable dict.

    ``lect`` must be a code of :func:`tugaphone.list_dialects`. Any other code
    raises ``ValueError``: tugaphone and orthography2ipa resolve a loose tag
    differently (``br`` is Portuguese to :func:`tugaphone.resolve_lect` and
    Breton to orthography2ipa), so pass the result of
    :func:`tugaphone.resolve_lect` to both.
    """
    if lect not in list_dialects():
        raise ValueError(
            f"{lect!r} is not a tugaphone lect; pass a code of list_dialects(), "
            "for example the result of resolve_lect()")
    lexicon = packaged_lexicon(lect, patches=True) if lect in PACKAGED_LEXICON_LECTS else {}
    return Pipeline(
        lexicon=lexicon,
        expand=_expander(lect),
        mark=functools.partial(add_extra_diacritics, lang=lect))


@functools.lru_cache(maxsize=None)
def engine(lect: str) -> G2P:
    """A cached orthography2ipa engine for ``lect`` built on :func:`pipeline`.

    ``lect`` must already be an orthography2ipa lect code (see
    :func:`tugaphone.registry.resolve_lect`).
    """
    return G2P(lect, pipeline=pipeline(lect))


def _validate_contact(contact: str) -> None:
    if contact not in _VALID_CONTACT:
        raise ValueError(
            f"unknown contact {contact!r}; expected one of {_VALID_CONTACT}")


def phonemize(text: str, lang: str = "pt-PT", contact: str = "none") -> str:
    """Phonemize ``text`` for ``lang`` through the orthography2ipa lattice.

    ``contact`` is ``"none"`` (the default: every word is Portuguese),
    ``"auto"`` (each contact word is classified among es/fr/en), or ``"es"``,
    ``"fr"`` or ``"en"``. Contact words go through that language's lattice and
    are nativized onto the Portuguese inventory (see :mod:`tugaphone.codeswitch`).
    Any other ``contact`` raises ``ValueError``. Returns space-separated IPA per
    word, with ``ˈ`` before each stressed syllable.
    """
    _validate_contact(contact)
    lect = resolve_lect(lang)
    if contact == "none":
        return engine(lect).transcribe(text)

    runs = split_runs(text, contact, default_side=default_contact(lect))
    out: List[str] = []
    # Contiguous Portuguese tokens are transcribed as one phrase, so the
    # cross-word sandhi between them stays.
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
