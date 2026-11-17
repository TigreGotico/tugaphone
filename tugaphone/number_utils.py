"""Numbers, dates, times, money, measures and abbreviations, read by text2spoken.

text2spoken owns every reading rule. tugaphone picks the variety that each lect
reads: the lects that write the European AO1990 norm read ``pt-PT``, and the
lects that write the Brazilian norm read ``pt-BR``.
"""
import re
import warnings
from typing import Optional

from text2spoken import NormalizationParams, normalize

from tugaphone.registry import resolve_lect, spelling_norm


class UnreadFormWarning(UserWarning):
    """A written form with digits that tugaphone has no reading for.

    The phoneme lattice has no reading for a digit and drops it, so the
    warning names the form and the text it came from.
    """


#: The text2spoken variety of each AO1990 norm (``registry.spelling_norm``).
TEXT2SPOKEN_TAGS = {"ao1990-pt": "pt-PT", "ao1990-br": "pt-BR"}


def text2spoken_tag(lang: str) -> str:
    """The text2spoken variety that ``lang`` reads: ``pt-PT`` or ``pt-BR``.

    "19" is "dezanove" in ``pt-PT`` and "dezenove" in ``pt-BR``. The European
    sub-lects and the African and Asian lects read ``pt-PT``. The Brazilian
    sub-lects and ``pt-UY`` read ``pt-BR``.
    """
    return TEXT2SPOKEN_TAGS[spelling_norm(resolve_lect(lang))]


def normalize_numbers(text: str, lang: str = "pt-PT", strict: bool = False,
                      scale: Optional[str] = None) -> str:
    """Rewrite the numbers, dates, times, money, measures and abbreviations of
    ``text`` as the words a speaker of ``lang`` says.

    "Nasceu a 25/12/2023." reads "Nasceu a vinte e cinco de dezembro de dois
    mil e vinte e três.". The rest of the text stays as written, so text that
    is already spelled out comes back unchanged.

    ``scale`` is ``"long"`` or ``"short"``. It overrides the scale of the
    variety: ``10^9`` is "mil milhões" in ``pt-PT`` and "um bilhão" in
    ``pt-BR``. With ``strict``, a written form that text2spoken cannot read
    raises ``text2spoken.UnreadFormError``. Otherwise the form stays as
    written, and a form with digits gives an :class:`UnreadFormWarning`.
    """
    tag = text2spoken_tag(lang)
    spoken = normalize(text, tag, NormalizationParams(scale=scale, strict=strict))
    for form in re.findall(r"\S*\d\S*", spoken):
        warnings.warn(f"{tag}: no reading for {form!r} in {text!r}; its digits are dropped",
                      UnreadFormWarning, stacklevel=2)
    return spoken
