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

    Distribution: all northern varieties + Galician (Cintra 1971:87; whitepaper4
    rule N1). Case is preserved for the leading character. ``postag`` is
    accepted for signature uniformity but unused (this is not POS-conditioned).

    CAVEAT: routing through the G2P as ⟨b⟩ forces the STOP outcome [b] in every
    position, losing the intervocalic spirant realisation [β] that the merged
    labial has (Cintra 1971:87 "b ou β"; see :func:`ipa_transforms.betacism`,
    which keeps [β] intervocalically). Acceptable only as a coarse input hack;
    prefer the post-G2P ``betacism`` transform where the [b]~[β] allophony
    matters.
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

    Distribution: Transmontano / Alto-Minhoto, archaic (Cintra 1971, trait 3;
    whitepaper4 §3). Case-insensitive on the digraph. ``postag`` unused.

    DO NOT COMPOSE with :func:`ipa_transforms.palatal_affrication_ch`. That
    post-G2P rule counts ``word.lower().count("ch")`` to decide how many /ʃ/ to
    affricate; after this respelling the word contains no ⟨ch⟩, so the count is
    0 and no affrication fires — the two rules cancel. The phenomenon (⟨ch⟩ kept
    as a distinct historical affricate /tʃ/, Cintra trait 3) is correct, but the
    correct mechanism is ``palatal_affrication_ch`` ALONE, applied to the
    original spelling. This respelling merges ⟨ch⟩ into the ⟨x⟩=/ʃ/ path and is
    retained only for callers that deliberately want the merged /ʃ/ outcome.
    """
    out = re.sub(r"ch", "x", word)
    out = re.sub(r"Ch", "X", out)
    out = re.sub(r"CH", "X", out)
    return out
