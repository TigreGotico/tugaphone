"""Accent forcing: bend text or IPA toward a target Lusophone accent.

:func:`tugaphone.phonemize` already gives a lect's IPA, so this module serves
two downstream uses:

1. **Phoneme-input TTS** (phoonnx and others): :func:`force_accent` with
   ``mode="ipa"`` transcribes with the target lect.

2. **Grapheme-input TTS** (a fixed pt-PT or pt-BR voice): the voice reads
   text, so :func:`force_accent` with ``mode="respell"`` respells the input in
   Portuguese spelling that the voice's own accent reads as the target sounds
   (``binho`` for the Northern betacism of ``vinho``). It transcribes the text
   with the target lect, compares the IPA with the ``base_lect`` reading, and
   rewrites only the graphemes whose pronunciation differs.

Respelling is lossy: a contrast that the base spelling cannot write (European
``[ɨ]`` against a fuller ``[ə]``) stays as it is. Each candidate edit is kept
only if the base lect's reading of it moves toward the target, so a respelling
never makes a word worse (:func:`respell_word`).

:class:`AccentOverlay` is a user-space layer on top of both modes: ordered
regex and word-map transforms, JSON-serialisable so a voice tweak can be
shared. It holds user data, not shipped dialect phonology.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from tugaphone.lattice_core import phonemize
from tugaphone.registry import resolve_lect

_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


@dataclass(frozen=True)
class RespellRule:
    """A candidate orthographic edit toward a non-base accent.

    ``pattern`` matches a slice of the (lower-cased) source word and
    ``replacement`` is the orthographic string proposed in its place, expressed
    in the *base* accent's spelling conventions (so the base voice reads it as
    the target sound). Rules are never applied blindly: :func:`respell_word`
    keeps an edit only when re-transcribing it with the base lect moves the word
    closer to the target IPA, so the table can be liberal — a rule that does not
    help a given lect simply never fires.
    """

    name: str
    pattern: str
    replacement: str
    note: str = ""

    def matches(self, word: str) -> List[Tuple[int, int]]:
        return [(m.start(), m.end()) for m in re.finditer(self.pattern, word)]


#: Portuguese orthographic conventions that coax a base voice toward another
#: accent's realisation. Grounded in the phenomena the lect specs encode:
#: Northern betacism, Brazilian dental palatalisation, coda-``l`` vocalisation,
#: and mid-vowel/diphthong monophthongisation. Order is a hint only; the
#: hill-climb in :func:`respell_word` re-evaluates every rule each round.
DEFAULT_RESPELL_RULES: Tuple[RespellRule, ...] = (
    # Northern betacism: ⟨v⟩ merges into [b].  vinho → binho
    RespellRule("betacism", r"v", "b", "[v]→[b] (Northern PT)"),
    # Brazilian dental palatalisation before [i]:  tia → tchia, dia → djia
    RespellRule("palatal-ti", r"ti", "tchi", "[t]→[tʃ] before [i]"),
    RespellRule("palatal-di", r"di", "dji", "[d]→[dʒ] before [i]"),
    # …and before a final unstressed ⟨e⟩ that raises to [i]:  dente → dentchi
    RespellRule("palatal-te", r"te\b", "tchi", "final ⟨te⟩ → [tʃi]"),
    RespellRule("palatal-de", r"de\b", "dji", "final ⟨de⟩ → [dʒi]"),
    # Coda /l/ vocalisation to [w]:  sal → sau, Brasil → Brasiu
    RespellRule("l-vocal", r"l(?=$|[bcçdfgjkmnpqrstvxz])", "u",
                "coda [ɫ]→[w] (Brazilian)"),
    # Diphthong monophthongisation:  peixe → pêxe, pouco → pôco
    RespellRule("mono-ei", r"ei", "ê", "[ej]→[e] (some Northern/Brazilian)"),
    RespellRule("mono-ou", r"ou", "ô", "[ow]→[o]"),
)


def _restore_case(original: str, respelled: str) -> str:
    """Re-apply the original word's leading capital to the respelling."""
    if original[:1].isupper() and respelled:
        return respelled[:1].upper() + respelled[1:]
    return respelled


def respell_word(
    word: str,
    target_lect: str,
    base_lect: str = "pt-PT",
    rules: Tuple[RespellRule, ...] = DEFAULT_RESPELL_RULES,
) -> str:
    """Respell one word so ``base_lect`` reads it toward ``target_lect``.

    Transcribes ``word`` with the target lect, then hill-climbs orthographic
    edits from ``rules``: each round it tries every single rule application and
    keeps the one edit that most reduces the distance between the *base* lect's
    reading of the candidate and the target IPA, stopping when no edit helps.
    Because the gate is the base lect's own transcription, an accepted respelling
    is guaranteed to move the base voice toward the target; a contrast the base
    orthography cannot express yields no improving edit and the word is returned
    unchanged.
    """
    target_ipa = phonemize(word, target_lect)
    lower = word.lower()
    # The distance keeps the stress and length marks, so an edit that shifts
    # stress scores worse and is rejected.
    cur = lower
    best_d = _levenshtein(phonemize(cur, base_lect), target_ipa)
    if best_d == 0:
        return word  # base already says it — leave spelling untouched
    improved = True
    while improved:
        improved = False
        candidate = None
        for rule in rules:
            for start, end in rule.matches(cur):
                trial = cur[:start] + rule.replacement + cur[end:]
                if trial == cur:
                    continue
                d = _levenshtein(phonemize(trial, base_lect), target_ipa)
                if d < best_d:
                    best_d, candidate = d, trial
        if candidate is not None:
            cur, improved = candidate, True
    if cur == lower:
        return word
    return _restore_case(word, cur)


def respell(
    text: str,
    target_lect: str,
    base_lect: str = "pt-PT",
    rules: Tuple[RespellRule, ...] = DEFAULT_RESPELL_RULES,
) -> str:
    """Respell every word of ``text`` toward ``target_lect`` for a ``base_lect`` voice.

    Word tokens are respelled independently (:func:`respell_word`); punctuation
    and whitespace pass through untouched, so the result is readable Portuguese
    text a grapheme-input TTS speaking ``base_lect`` can pronounce with the
    target accent.
    """
    out: List[str] = []
    idx = 0
    for m in _WORD_RE.finditer(text):
        out.append(text[idx:m.start()])
        out.append(respell_word(m.group(), target_lect, base_lect, rules))
        idx = m.end()
    out.append(text[idx:])
    return "".join(out)


@dataclass
class Transform:
    """One ordered, user-supplied ad-hoc edit.

    ``kind`` is ``"regex"`` (``pattern`` is a regular expression) or ``"word"``
    (``pattern`` is matched as a whole word, case-insensitively by default).
    ``stage`` selects what it runs on: ``"ipa"`` transforms edit the phonemic
    output of ``mode="ipa"``, ``"text"`` transforms edit the respelled text of
    ``mode="respell"``. This is deliberately *user* space — not shipped dialect
    phonology — so anything goes; that is the point of the escape hatch.
    """

    kind: str = "regex"
    pattern: str = ""
    replacement: str = ""
    stage: str = "ipa"
    ignore_case: bool = True

    def apply(self, s: str) -> str:
        flags = re.IGNORECASE if self.ignore_case else 0
        if self.kind == "word":
            pat = r"\b" + re.escape(self.pattern) + r"\b"
            return re.sub(pat, self.replacement, s, flags=flags)
        if self.kind == "regex":
            return re.sub(self.pattern, self.replacement, s, flags=flags)
        raise ValueError(f"unknown transform kind: {self.kind!r}")

    def to_dict(self) -> Dict[str, object]:
        return {
            "kind": self.kind,
            "pattern": self.pattern,
            "replacement": self.replacement,
            "stage": self.stage,
            "ignore_case": self.ignore_case,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, object]) -> "Transform":
        return cls(
            kind=str(d.get("kind", "regex")),
            pattern=str(d.get("pattern", "")),
            replacement=str(d.get("replacement", "")),
            stage=str(d.get("stage", "ipa")),
            ignore_case=bool(d.get("ignore_case", True)),
        )


@dataclass
class AccentOverlay:
    """An ordered, shareable stack of user ad-hoc accent tweaks.

    The overlay is a user-owned escape hatch: hand-authored regex/word
    substitutions applied *after* the lattice, in order, either to the IPA
    (``stage="ipa"``) or to the respelled text (``stage="text"``). It serialises to plain JSON so a voice
    tweak — "on my TTS, always render ⟨lh⟩ as [j]" — can be saved next to the
    voice and shared, without ever touching shipped phonology.
    """

    name: str = ""
    transforms: List[Transform] = field(default_factory=list)

    def apply(self, s: str, stage: str) -> str:
        for t in self.transforms:
            if t.stage == stage:
                s = t.apply(s)
        return s

    def to_dict(self) -> Dict[str, object]:
        return {"name": self.name,
                "transforms": [t.to_dict() for t in self.transforms]}

    @classmethod
    def from_dict(cls, d: Dict[str, object]) -> "AccentOverlay":
        return cls(
            name=str(d.get("name", "")),
            transforms=[Transform.from_dict(t)
                        for t in d.get("transforms", [])],
        )

    def to_json(self, **kwargs) -> str:
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("indent", 2)
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, s: str) -> "AccentOverlay":
        return cls.from_dict(json.loads(s))


def force_accent(
    text: str,
    lect: str,
    mode: str = "ipa",
    base_lect: str = "pt-PT",
    overlay: Optional[AccentOverlay] = None,
    rules: Tuple[RespellRule, ...] = DEFAULT_RESPELL_RULES,
) -> str:
    """Force ``text`` into the ``lect`` accent for a downstream TTS.

    ``mode="ipa"`` returns the target lect's IPA, for a phoneme-input TTS.
    ``mode="respell"`` returns Portuguese text respelled so a grapheme-input
    TTS that speaks ``base_lect`` pronounces the target accent (see
    :func:`respell`). Any other ``mode`` raises ``ValueError``. ``lect`` and
    ``base_lect`` resolve as in :func:`tugaphone.resolve_lect`; ``base_lect``
    matters only in respell mode. ``rules`` is the respelling rule table
    (:data:`DEFAULT_RESPELL_RULES` by default). The ``overlay`` applies last:
    its ``stage="ipa"`` transforms in IPA mode, its ``stage="text"`` transforms
    in respell mode.
    """
    target = resolve_lect(lect)
    base = resolve_lect(base_lect)
    if mode == "ipa":
        out = phonemize(text, target)
        if overlay is not None:
            out = overlay.apply(out, stage="ipa")
        return out
    if mode == "respell":
        out = respell(text, target, base, rules)
        if overlay is not None:
            out = overlay.apply(out, stage="text")
        return out
    raise ValueError(f"mode must be 'ipa' or 'respell', got {mode!r}")


__all__ = [
    "force_accent",
    "respell",
    "respell_word",
    "RespellRule",
    "DEFAULT_RESPELL_RULES",
    "Transform",
    "AccentOverlay",
]
