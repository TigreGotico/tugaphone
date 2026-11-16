"""tugaphone as a backend of the scriptconv sentence gate.

The gate (``python -m scriptconv.testing.compare``) scores a backend against
standalone orthography2ipa, then switches off one stage at a time with
``without(stage)`` and scores again. The stages here are the fields of the
orthography2ipa ``Pipeline`` that :func:`tugaphone.pipeline` fills:

- ``lexicon``: the packaged lexicon of the lect;
- ``expand``: orthographic rewrites, then numbers and ordinals in words;
- ``mark``: bifonia's homograph marks.

A stage that is off takes the value an empty ``Pipeline`` gives it, so the
engine runs as if tugaphone had not supplied it. An empty lexicon is ``{}``,
because ``None`` would leave the choice to the process-wide lexicon.
"""
from __future__ import annotations

import dataclasses

from orthography2ipa import G2P

from tugaphone import pipeline, resolve_lect

STAGES = {"lexicon": {}, "expand": None, "mark": None}


class TugaphoneBackend:
    """``phonemize(text, lang)`` as the gate calls it, with stages that switch off."""

    def __init__(self, disabled: frozenset[str] = frozenset()) -> None:
        self.disabled = frozenset(disabled)
        self._engines: dict[str, G2P] = {}

    def without(self, stage: str) -> "TugaphoneBackend":
        """The same backend with ``stage`` switched off."""
        if stage not in STAGES:
            raise ValueError(f"tugaphone has no stage {stage!r}; its stages are {', '.join(STAGES)}")
        return TugaphoneBackend(self.disabled | {stage})

    def _engine(self, lect: str) -> G2P:
        if lect not in self._engines:
            stages = pipeline(lect)
            if self.disabled:
                stages = dataclasses.replace(stages, **{s: STAGES[s] for s in self.disabled})
            self._engines[lect] = G2P(lect, pipeline=stages)
        return self._engines[lect]

    def phonemize(self, text: str, lang: str) -> list[list[str]]:
        """The IPA of ``text`` as one sentence of one string."""
        return [[self._engine(resolve_lect(lang)).transcribe(text)]]
