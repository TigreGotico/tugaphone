"""Word-level language detection for code-switch routing.

The code-switch stage needs one decision per token: is this word Portuguese, or
is it embedded contact-language material to route through the ``es``/``fr``/``en``
lattice and nativize? The orthographic heuristic in :mod:`tugaphone.codeswitch`
answers that from spelling alone — it flags a word only when it carries a letter
or digraph Portuguese does not use natively or is a known function word. That
misses the loans and internationalisms spelled with Portuguese-legal letters
(``site``, ``feedback``, ``general``) and, on the border, cannot tell a Spanish
embed from a Portuguese word.

This module adds a statistical detector: four character-level Markov models —
one each for Portuguese, Spanish, French and English — trained on Wikipedia and
serialized as small JSON artifacts under ``tugaphone/data/langdetect/``. A word
is scored under all four models; the model that assigns it the lowest perplexity
wins.

In-language default (null beats wrong)
--------------------------------------
Portuguese is the surrounding language, so it is the default: a word is only
routed out of Portuguese when a foreign model beats the Portuguese model by at
least :data:`DEFAULT_MARGIN` nats-per-character. Below that margin the word stays
``pt`` — a weak, ambiguous signal never misroutes a native word. The genuinely
ambiguous shared-alphabet internationalisms (``hotel``, ``radio``, ``general``)
sit inside that margin band and therefore stay Portuguese, which is exactly the
conservative behaviour a TTS frontend wants.

The detector is optional. It is used only when :mod:`markovonnx` is importable
and the bundled models are present; otherwise the caller falls back to the
orthographic heuristic. Loading is lazy and cached, so importing tugaphone never
pays the cost unless code-switching actually runs.
"""
from __future__ import annotations

import functools
import math
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

#: Languages the detector scores. ``pt`` is the in-language default.
LANGS: List[str] = ["pt", "es", "fr", "en"]

#: Boundary sentinels wrapping each word, matching the training pipeline so
#: word-initial and word-final character statistics are modelled.
_BOS, _EOS = "\x02", "\x03"

#: A foreign model must beat the Portuguese model by at least this many
#: nats-per-character (log-perplexity units) before a word is routed out of
#: Portuguese. Tuned on held-out Wikipedia words to favour never misrouting a
#: native word over catching every contact word (null beats wrong): a higher
#: margin keeps more words Portuguese. This is set well above the Basque
#: frontend's 0.25 because Portuguese, Spanish and French share the Romance
#: character-shape so tightly that a small margin misroutes common native words
#: (``noite``, ``carne``); 0.5 keeps native retention high at a modest recall
#: cost (see ``docs/codeswitch.md``).
DEFAULT_MARGIN: float = 0.5

#: High-frequency Portuguese grammatical words that are always kept Portuguese,
#: regardless of the models. Encyclopedic training text underrepresents
#: conversational grammar, so a char-model can rate a short function word like
#: ``de`` or ``que`` as Spanish/French on its letter shape alone — and these
#: shared-Romance function words are exactly the ones a Spanish or French model
#: also fits well. They are unambiguously native here and must never be routed to
#: a contact lattice, so the statistical decision is bypassed for them entirely.
#: (Deliberately limited to closed-class grammar and a few fixed greetings;
#: open-class words still go through the models.)
_PORTUGUESE_KEEP = frozenset("""
o a os as um uma uns umas de do da dos das em no na nos nas por pra pro
para com sem sob sobre entre ate até desde após trás e ou nem mas porém
que se como quando onde quem qual quais cujo cuja quanto porque porquê
não sim já ainda também só apenas muito pouco mais menos bem mal assim
tão tanto cada todo toda todos todas algum alguma nenhum nenhuma outro outra
este esta estes estas esse essa esses essas aquele aquela aqueles aquelas
isto isso aquilo meu minha teu tua seu sua nosso nossa vosso vossa
eu tu ele ela nós vós eles elas me te lhe nos vos lhes mim ti si
é foi era são somos sou está estão estava estou tem têm tinha há havia
ser estar ter haver fazer ir vir dar ver dizer poder querer saber
aqui ali aí lá cá agora hoje ontem amanhã sempre nunca depois antes então
olá oi bom boa obrigado obrigada por favor tchau adeus
""".split())

#: Where the bundled JSON models live.
_MODEL_DIR = Path(__file__).parent / "data" / "langdetect"


def _load_gz(markov_chain_cls, path: Path):
    """Load a gzip-compressed markovonnx JSON model via a temporary file."""
    import gzip
    import tempfile

    with gzip.open(path, "rb") as fh:
        data = fh.read()
    with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return markov_chain_cls.load(tmp_path)
    finally:
        import os
        os.unlink(tmp_path)


def _normalize(word: str) -> str:
    """NFC + lowercase + keep only alphabetic characters (training parity)."""
    word = unicodedata.normalize("NFC", word).lower()
    return "".join(ch for ch in word if ch.isalpha())


def _wrap(word: str) -> List[str]:
    return [_BOS] + list(word) + [_EOS]


class MarkovLangDetector:
    """Four char-Markov models scoring a word as pt / es / fr / en."""

    def __init__(self, models: Dict[str, "object"]):
        self._models = models

    # -- construction ---------------------------------------------------------

    @classmethod
    def from_dir(cls, model_dir: Path = _MODEL_DIR) -> Optional["MarkovLangDetector"]:
        """Load the bundled models, or return ``None`` if unavailable.

        Returns ``None`` when :mod:`markovonnx` is not installed or any of the
        four model files is missing — the caller then falls back to the
        orthographic heuristic. Models are shipped gzip-compressed
        (``<lang>.json.gz``, a few tens of KB each); a plain ``<lang>.json`` is
        also accepted.
        """
        try:
            from markovonnx import MarkovChain
        except Exception:
            return None
        models = {}
        for lang in LANGS:
            gz = model_dir / f"{lang}.json.gz"
            plain = model_dir / f"{lang}.json"
            try:
                if gz.is_file():
                    models[lang] = _load_gz(MarkovChain, gz)
                elif plain.is_file():
                    models[lang] = MarkovChain.load(str(plain))
                else:
                    return None
            except Exception:
                return None
        return cls(models)

    # -- scoring --------------------------------------------------------------

    def score(self, word: str) -> Dict[str, float]:
        """Length-normalized log-perplexity per language (lower = better fit)."""
        seq = _wrap(_normalize(word))
        out: Dict[str, float] = {}
        for lang, mc in self._models.items():
            ppx = mc.perplexity([seq])
            out[lang] = math.log(max(ppx, 1e-30))
        return out

    def detect(self, word: str, margin: float = DEFAULT_MARGIN,
               default_side: Optional[str] = None
               ) -> Tuple[str, Dict[str, float]]:
        """Return ``(lang, scores)`` with the in-language default applied.

        The best-fitting foreign language is returned only if it beats ``pt`` by
        at least ``margin``; otherwise the word stays ``pt``. When two foreign
        models sit within ``margin`` of each other (the shared-Romance overlap),
        ``default_side`` — the dialect's contact side — breaks the tie so a
        genuinely ambiguous embed routes to the expected language.
        """
        core = _normalize(word)
        if not core:
            return "pt", {}
        if core in _PORTUGUESE_KEEP:
            # Unambiguously native grammar word: never route out of Portuguese.
            return "pt", {}
        scores = self.score(word)
        best = min(scores, key=scores.get)
        if best == "pt":
            return "pt", scores
        if (scores["pt"] - scores[best]) < margin:
            return "pt", scores
        # Tie-break among foreign models within a margin of the winner.
        if default_side is not None and default_side in scores:
            if (scores[default_side] - scores[best]) < margin:
                return default_side, scores
        return best, scores

    def is_contact(self, word: str, margin: float = DEFAULT_MARGIN) -> bool:
        """Whether *word* is embedded contact-language material (not Portuguese)."""
        return self.detect(word, margin)[0] != "pt"


@functools.lru_cache(maxsize=1)
def get_detector() -> Optional[MarkovLangDetector]:
    """The cached bundled detector, or ``None`` if unavailable."""
    return MarkovLangDetector.from_dir()
