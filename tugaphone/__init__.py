"""tugaphone — dialect-aware Portuguese phonemization on the orthography2ipa lattice.

The phonemizer drives the shared orthography2ipa candidate lattice: a dialect is
an orthography2ipa lect spec, and the lattice — the spec's grapheme table,
``allophone_rules`` and cross-word ``sandhi_rules`` — produces the dialect's
phonology directly. tugaphone contributes the stages orthography2ipa leaves to
the caller (number/ordinal verbalization, sense-based homograph marking, the
``pt-PT`` residual lexicon, syllabification), wired through orthography2ipa's
own extension points. See :mod:`tugaphone.lattice_core`.
"""
from typing import Optional

from tugaphone.version import __version__
from tugaphone.lattice_core import phonemize, pipeline
from tugaphone.registry import is_supported, list_dialects, resolve_lect
from tugaphone.content_revision import revision
from tugaphone.accent import (
    force_accent,
    respell,
    respell_word,
    AccentOverlay,
    Transform,
    RespellRule,
    DEFAULT_RESPELL_RULES,
)


class TugaPhonemizer:
    """Dialect-aware Portuguese phonemization on the orthography2ipa lattice.

    Every Portuguese-family lect orthography2ipa ships is reachable by its
    BCP-47 code — the national standards ("pt-PT", "pt-BR", "pt-AO", "pt-MZ",
    "pt-TL"), the European and Brazilian sub-regional varieties
    ("pt-PT-x-porto", "pt-BR-x-sp", …), and the African, Asian and historical
    lects; the full list comes from :func:`tugaphone.list_dialects`.
    """

    def phonemize_sentence(self, sentence: str, lang: str = "pt-PT",
                           contact: str = "none") -> str:
        """Phonemize raw ``sentence`` for the ``lang`` lect: see :func:`tugaphone.phonemize`.

        ``contact`` is the embedded-language policy, ``"none"`` (the default),
        ``"auto"``, ``"es"``, ``"fr"`` or ``"en"``; see :mod:`tugaphone.codeswitch`.
        Returns space-separated IPA per word, with ``ˈ`` before
        each stressed syllable. An unknown ``contact`` raises ``ValueError``.
        """
        return phonemize(sentence, lang, contact)

    @staticmethod
    def force_accent(text: str, lect: str, mode: str = "ipa",
                     base_lect: str = "pt-PT",
                     overlay: Optional["AccentOverlay"] = None) -> str:
        """Force ``text`` into the ``lect`` accent for a downstream TTS.

        ``mode="ipa"`` returns the target lect's IPA (phoneme-input TTS);
        ``mode="respell"`` returns Portuguese text respelled so a grapheme-input
        TTS speaking ``base_lect`` pronounces the target accent. See
        :func:`tugaphone.accent.force_accent`.
        """
        return force_accent(text, lect, mode=mode, base_lect=base_lect,
                            overlay=overlay)

    @staticmethod
    def is_supported(lang: str) -> bool:
        """Whether ``lang`` names a tugaphone lect, itself or through an alias.

        See :func:`tugaphone.registry.is_supported`.
        """
        return is_supported(lang)


__all__ = [
    "TugaPhonemizer",
    "phonemize",
    "list_dialects",
    "resolve_lect",
    "is_supported",
    "force_accent",
    "respell",
    "respell_word",
    "AccentOverlay",
    "Transform",
    "RespellRule",
    "DEFAULT_RESPELL_RULES",
    "pipeline",
    "revision",
    "__version__",
]

