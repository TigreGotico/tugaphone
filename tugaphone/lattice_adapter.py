"""Segment-model boundary between orthography2ipa's lattice and tugaphone.

B6 stage-2 routes tugaphone's *base* per-word IPA generation through the
shared orthography2ipa pronunciation lattice
(:meth:`orthography2ipa.g2p.G2P.ipa_lattice`) instead of the private
grapheme→phoneme character cascade in :mod:`tugaphone.tokenizer`. The lattice
is the object the shared beam reads: one ranked slot per GRAPHEME token, in
surface order, already scored with the engine's stress/positional context.

The two engines do not agree on segment *model*, so a naive
``"".join(slot.top)`` would corrupt the string operations the accent
primitives (:mod:`tugaphone.ipa_transforms`) run on top. This adapter makes
the boundary explicit and converts the flat lattice into tugaphone's canonical
layout so the primitive framework keeps composing unchanged:

* **Stress + syllabification** — the lattice is *pre-stress* and flat.
  tugaphone marks stress per syllable and joins syllables with the hiatus
  token ``·``. We re-group the per-grapheme slots into the word's syllables
  (via ``silabificador``, the same syllabifier tugaphone already uses),
  place the primary-stress mark before the stressed syllable, and join with
  ``·`` — matching the cascade's own ``WordToken.ipa`` layout.
* **Nasal glides** — the lattice emits nasalised off-glides as ``w̃``/``j̃``
  (base + combining tilde U+0303); tugaphone's nasal-diphthong convention
  nasalises only the nucleus and keeps the glide bare (``ɐ̃w``). We strip the
  combining tilde from glide symbols so the primitives' grapheme-cluster
  slicing sees the shape they were written against.

Where the lattice cannot cover a word (no grapheme tokens — e.g. pure
punctuation or fully out-of-script input), :func:`lattice_base_ipa` returns
``None`` and the caller keeps the cascade fallback.
"""
from functools import lru_cache
from typing import List, Optional

from orthography2ipa.g2p import G2P
from orthography2ipa.stress import _syllables_for, detect_stress


@lru_cache(maxsize=None)
def _engine(dialect_code: str) -> G2P:
    """A cached :class:`G2P` engine for ``dialect_code`` (resolved by o2i)."""
    return G2P(dialect_code)


# Combining tilde (U+0303). The lattice binds it to a base glide symbol for a
# nasalised off-glide; tugaphone keeps the glide bare and nasalises only the
# nucleus, so the tilde is dropped from ``w``/``j`` (and the espeak ``ʊ``/``ɪ``
# glide variants) while every other combining tilde — on a vowel nucleus — is
# preserved.
_COMBINING_TILDE = "̃"
_GLIDE_BASES = "wjʊɪ"


def _denasalize_glide(segment: str) -> str:
    """Strip the combining nasal tilde from glide symbols in ``segment``.

    ``ɐ̃w̃`` (ɐ + ̃ + w + ̃) → ``ɐ̃w`` (ɐ + ̃ + w): the nucleus keeps its tilde,
    the off-glide loses it. Tildes on any non-glide base are untouched.
    """
    out: List[str] = []
    for ch in segment:
        if (ch == _COMBINING_TILDE and out and out[-1] in _GLIDE_BASES):
            continue
        out.append(ch)
    return "".join(out)


def lattice_base_ipa(
    word: str,
    dialect_code: str,
    *,
    stress_token: str = "ˈ",
    hiatus_token: str = "·",
) -> Optional[str]:
    """Base IPA for ``word`` read off the shared o2i lattice, in tuga layout.

    Returns the canonical tugaphone per-word string (per-syllable, stress
    marked before the stressed syllable, syllables joined by ``hiatus_token``,
    glides denasalised), or ``None`` when the lattice yields no grapheme slots
    so the caller can fall back to the cascade.
    """
    engine = _engine(dialect_code)
    wl = word.lower().strip()
    if not wl:
        return None

    slots = engine.ipa_lattice(wl)
    if not slots:
        return None

    sylls = _syllables_for(wl, engine.lang)
    n_syll = max(1, len(sylls))

    # End-index (exclusive) of each syllable within the surface word, so a
    # slot's start offset locates its syllable. ``silabificador`` rebuilds the
    # word, so the boundaries align with the lattice spans.
    bounds: List[int] = []
    acc = 0
    for syl in sylls:
        acc += len(syl)
        bounds.append(acc)

    def syllable_of(start: int) -> int:
        for i, end in enumerate(bounds):
            if start < end:
                return i
        return n_syll - 1

    groups: List[List[str]] = [[] for _ in range(n_syll)]
    for slot in slots:
        if not slot.candidates:
            continue
        top = _denasalize_glide(slot.candidates[0].ipa)
        if not top:
            continue
        idx = syllable_of(slot.span[0]) if sylls else 0
        if idx >= n_syll:
            idx = n_syll - 1
        groups[idx].append(top)

    syllable_strings = ["".join(g) for g in groups]

    stressed_idx = 0
    if engine.spec.stress is not None and len(sylls) > 1:
        stressed_idx = detect_stress(wl, engine.spec.stress, syllables=sylls)
    if 0 <= stressed_idx < len(syllable_strings) and syllable_strings[stressed_idx]:
        syllable_strings[stressed_idx] = (
            stress_token + syllable_strings[stressed_idx]
        )

    joined = hiatus_token.join(s for s in syllable_strings if s)
    return joined or None
