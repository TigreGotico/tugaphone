"""tugaphone — dialect-aware Portuguese phonemization on the orthography2ipa lattice.

The phonemizer drives the shared orthography2ipa candidate lattice: a dialect is
an orthography2ipa lect spec, and the lattice — the spec's grapheme table,
``allophone_rules`` and cross-word ``sandhi_rules`` — produces the dialect's
phonology directly. tugaphone contributes the stages orthography2ipa leaves to
the caller (number/ordinal verbalization, sense-based homograph marking, the
curated ``tugalex`` lexicon, syllabification), wired through orthography2ipa's
own extension points. See :mod:`tugaphone.lattice_core`.
"""
import warnings
from typing import Optional

from tugaphone.version import __version__
from tugaphone.lattice_core import phonemize as _phonemize
from tugaphone.lattice_core import phonemize
from tugaphone.registry import list_dialects, resolve_lect
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

    def __init__(self) -> None:
        pass

    def phonemize_sentence(self, sentence: str, lang: str = "pt-PT",
                           contact: str = "none",
                           regional_dialect: Optional[object] = None) -> str:
        """Phonemize ``sentence`` for the ``lang`` dialect.

        Parameters:
            sentence: Input text to phonemize.
            lang: BCP-47 lect code to target. National standards, sub-regional
                varieties and the African/Asian lects all resolve to an
                orthography2ipa spec; see :func:`tugaphone.list_dialects`.
            contact: Embedded-language policy. Defaults to ``"none"`` — the
                engine-only path, so the out-of-the-box output is unchanged by
                this feature (Portuguese shares the Romance character-shape with
                its contact languages too tightly for statistical routing to be
                safe by default). Opt in with ``"auto"`` (detect and classify
                each contact word among es/fr/en, unclassified words falling to
                the dialect's side) or force a single lattice with ``"es"`` /
                ``"fr"`` / ``"en"``. Contact words are transcribed through the
                orthography2ipa contact lattice and nativized onto the Portuguese
                inventory; see :mod:`tugaphone.codeswitch`.
            regional_dialect: Deprecated and ignored. Dialect is now selected
                entirely by ``lang``; the regional accent is encoded in the
                orthography2ipa lect spec, not applied as a post-hoc transform.

        Returns:
            Space-separated IPA for each word.
        """
        if regional_dialect is not None:
            warnings.warn(
                "regional_dialect= is deprecated and ignored; select the "
                "accent through lang= (e.g. lang='pt-PT-x-porto'). The accent "
                "is encoded in the orthography2ipa lect spec.",
                DeprecationWarning,
                stacklevel=2,
            )
        return _phonemize(sentence, lang, contact)

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
        """Whether ``lang`` resolves to a known Portuguese lect."""
        return resolve_lect(lang) is not None


__all__ = [
    "TugaPhonemizer",
    "phonemize",
    "list_dialects",
    "resolve_lect",
    "force_accent",
    "respell",
    "respell_word",
    "AccentOverlay",
    "Transform",
    "RespellRule",
    "DEFAULT_RESPELL_RULES",
    "__version__",
]


if __name__ == "__main__":
    ph = TugaPhonemizer()
    sentences = [
        "O gato dorme.",
        "Tu falas português muito bem.",
        "O comboio chegou à estação.",
        "Vou pôr a manteiga no frigorífico.",
    ]
    for s in sentences:
        print(s)
        for code in ["pt-PT", "pt-PT-x-porto", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
            print(f"{code} → {ph.phonemize_sentence(s, code)}")
        print("######")
