"""Pre-G2P morpheme transforms: dialectal/archaic respellings fed to G2P.

Each function has the signature ``(word: str, postag: str) -> str`` and returns
a possibly respelled surface form. These rules model dialect features that are
cleanest to express orthographically — the respelled form is then handed to the
grapheme-to-phoneme cascade, which produces the dialectal phonemes for free.

This is the text-level ("forced mispronunciation") strategy: a feature that
corresponds to a grapheme substitution is best applied before G2P, so the
phonemizer's own rules carry it through (whitepaper4 §"Fully simulable").

Sources follow the precedence order documented in
:mod:`tugaphone.ipa_transforms`.
"""

import re
from typing import Callable

MorphemeTransform = Callable[[str, str], str]


def spell_v_as_b(word: str, postag: str = "NOUN") -> str:
    """Respell <v> as <b> so G2P yields the betacism stop [b].

    Phenomenon: northern betacism merges /v/ into [b]. Applying it at the
    orthographic level (*vaca*→*baca*, *vinho*→*binho*) lets the G2P cascade
    produce [b] directly, which composes correctly with downstream rules that
    reference /b/.

    Distribution: all northern varieties + Galician (Cintra 1971; whitepaper4
    rule N1). Case is preserved for the leading character.
    """
    out = re.sub(r"v", "b", word)
    out = re.sub(r"V", "B", out)
    return out


def archaic_ch_to_x(word: str, postag: str = "NOUN") -> str:
    """Respell <ch> as <x> to feed the apico-palatal source of <ch>.

    Phenomenon: in conservative Transmontano the digraph <ch> kept a distinct
    (historically affricate) value; respelling to <x> routes it through the
    phonemizer's /ʃ/ path so the post-G2P affrication rule can target it
    consistently regardless of lexicon idiosyncrasies.

    Distribution: Transmontano / Alto-Minhoto, archaic (Cintra 1971;
    whitepaper4 §3). Case-insensitive on the digraph.
    """
    out = re.sub(r"ch", "x", word)
    out = re.sub(r"Ch", "X", out)
    out = re.sub(r"CH", "X", out)
    return out
