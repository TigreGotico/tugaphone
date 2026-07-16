"""tugaphone on the orthography2ipa base interfaces.

tugaphone *consumes* orthography2ipa — it drives the shared candidate lattice
(the Portuguese lect specs, their stress and sandhi rules) and adds the stages
orthography2ipa leaves to the caller: gender-aware number verbalization,
sense-based homograph marking and the curated ``tugalex`` lexicon overlay (see
:mod:`tugaphone.lattice_core`). Use the engine directly:

    >>> from tugaphone.plugin import TugaphoneG2PPlugin
    >>> TugaphoneG2PPlugin().transcribe("o gato dorme")

Two classes live here:

- :class:`TugaphoneG2PPlugin` — the full phonemizer behind the shared
  engine interface.
- :class:`SilabificadorSyllabifier` — a component plugin registered in
  the ``orthography2ipa.syllabify`` entry-point group, so
  orthography2ipa's own stress detection syllabifies Portuguese with
  ``silabificador`` instead of its naive vowel-group splitter.
"""
from typing import List, Optional

from orthography2ipa import WordContext
from orthography2ipa.syllabifier_plugin import SyllabifierPlugin
from silabificador import syllabify as _syllabify

from tugaphone.registry import list_dialects


class TugaphoneG2PPlugin:
    """Dialect-aware Portuguese G2P via the tugaphone pipeline.

    The underlying :class:`tugaphone.TugaPhonemizer` (lexicon + bifonia
    homograph resolution) loads lazily on first transcription.
    """

    def __init__(self, lang: str = "pt-PT") -> None:
        self.lang = lang
        self._phonemizer = None

    @property
    def language_codes(self) -> List[str]:
        return list_dialects()

    def _engine(self):
        if self._phonemizer is None:
            from tugaphone import TugaPhonemizer
            self._phonemizer = TugaPhonemizer()
        return self._phonemizer

    def transcribe(self, text: str) -> str:
        return self._engine().phonemize_sentence(text, lang=self.lang)

    def transcribe_word(
        self, word: str, context: Optional[WordContext] = None
    ) -> str:
        lang = (context.lang if context is not None and context.lang
                else self.lang)
        return self._engine().phonemize_sentence(word, lang=lang)


class SilabificadorSyllabifier(SyllabifierPlugin):
    """Portuguese syllabifier for orthography2ipa's stress detection.

    **Kept as a class, no longer registered as an entry point.**
    orthography2ipa ships this same plugin itself now
    (``orthography2ipa[portuguese]``, wrapping the same ``silabificador``), and
    two entry points claiming ``pt-PT`` at the same priority meant the winner was
    whichever importlib enumerated last — a coin flip between two objects that do
    the identical thing. One owner, and it is the library the plugin plugs into.
    """

    @property
    def language_codes(self) -> List[str]:
        codes = list_dialects()
        codes.extend(["pt-CV", "pt-GW", "pt-MO", "pt-ST", "pt-GQ"])
        return codes

    def syllabify(self, word: str, lang: Optional[str] = None) -> List[str]:
        return list(_syllabify(word))
