"""Orthographic text transforms applied BEFORE number verbalisation.

These rewrite raw written conventions (number ranges, clock times, European
thousands/decimal separators, honorific abbreviations, regnal Roman numerals,
letter-spelled acronyms) into plain words or digit tokens that
:func:`tugaphone.number_utils.normalize_numbers` can then read out loud. They
run at the text level, before any lattice/phoneme work, so they are plugged
into :func:`tugaphone.lattice_core._normalizer` ahead of
``normalize_numbers``.

The reading rules for ranges, clock times, separators, abbreviations, and
regnal numerals follow the behaviour of the European-Portuguese TTS front-end
logus2k/tts_eu_pt (Apache-2.0); the code here is an independent
reimplementation in tugaphone's idiom, not a port of that project's source.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Number ranges: a dash BETWEEN two digits is a numeric range, read " a ".
# Word hyphens ("chamo-me", "guarda-chuva") have letters on at least one side
# and are untouched.
# ---------------------------------------------------------------------------
_RANGE_DASH = re.compile(r"(?<=\d)[-–—−](?=\d)")


def split_number_ranges(text: str) -> str:
    """"1139-1185" -> "1139 a 1185"."""
    return _RANGE_DASH.sub(" a ", text)


# ---------------------------------------------------------------------------
# European number separators: "." groups thousands and is dropped;
# "," is the decimal mark, read "vírgula". Both only between two digits, so
# sentence-final periods, list commas and ordinal marks ("3.º") are unaffected.
# ---------------------------------------------------------------------------
_THOUSANDS_DOT = re.compile(r"(?<=\d)\.(?=\d)")
_DECIMAL_COMMA = re.compile(r"(?<=\d),(?=\d)")


def normalize_number_separators(text: str) -> str:
    """"92.073" -> "92073"; "10,4" -> "10 vírgula 4"."""
    text = _THOUSANDS_DOT.sub("", text)
    return _DECIMAL_COMMA.sub(" vírgula ", text)


# ---------------------------------------------------------------------------
# Clock times. "HH:00" is read "<hora> hora(s)" -- the digit token is left for
# normalize_numbers, which already picks the feminine form ("uma", "duas",
# "vinte e uma", ...) from the following "hora"/"horas" noun, so no separate
# gender table is needed here. Any other "HH:MM" is read "<hora> e <minutos>".
# Hours are restricted to 0-23; anything else (e.g. "24:00") is left alone.
# ---------------------------------------------------------------------------
_HOUR = r"(?:[01]?\d|2[0-3])"
_WHOLE_HOUR = re.compile(rf"\b({_HOUR}):00\b")
_CLOCK_TIME = re.compile(rf"\b({_HOUR}):([0-5]\d)\b")


def _whole_hour_repl(match: "re.Match[str]") -> str:
    hh = match.group(1)
    unit = "hora" if int(hh) == 1 else "horas"
    return f"{hh} {unit}"


def expand_clock_times(text: str) -> str:
    """"16:00" -> "16 horas"; "16:54" -> "16 e 54". Whole hours must be
    expanded first, so the ":00" case doesn't fall through to "16 e 0"."""
    text = _WHOLE_HOUR.sub(_whole_hour_repl, text)
    return _CLOCK_TIME.sub(r"\1 e \2", text)


# ---------------------------------------------------------------------------
# Honorific / place abbreviations, expanded before a capitalised word (the
# name they introduce). "n.º"/"nº" always mean "número" and carry no such
# condition -- they precede a plain number, not a name.
# ---------------------------------------------------------------------------
_ABBREVIATIONS = {
    "D.": "Dom",
    "Sr.": "Senhor",
    "Sra.": "Senhora",
    "Dr.": "Doutor",
    "Dra.": "Doutora",
    "Eng.": "Engenheiro",
    "Prof.": "Professor",
    "Av.": "Avenida",
    "R.": "Rua",
    "Lx.": "Lisboa",
}
_NUMERO_ABBREVIATIONS = {"n.º", "nº", "N.º", "Nº"}

_LEAD_PUNCT = "(“\"'¿¡"


def _is_capitalised(word: str) -> bool:
    core = word.lstrip(_LEAD_PUNCT)
    return bool(core) and core[0].isupper()


def expand_abbreviations(text: str) -> str:
    """"Sr. Silva" -> "Senhor Silva"; "n.º 4" -> "número 4"."""
    words = text.split()
    out = []
    for i, w in enumerate(words):
        if w in _NUMERO_ABBREVIATIONS:
            out.append("número")
            continue
        expansion = _ABBREVIATIONS.get(w)
        if expansion is not None and i + 1 < len(words) and _is_capitalised(words[i + 1]):
            out.append(expansion)
            continue
        out.append(w)
    return " ".join(out)


# ---------------------------------------------------------------------------
# Regnal Roman numerals -> masculine ordinals. Multi-letter numerals (II..XX)
# always convert; a single I/V/X converts only right after a capitalised
# name-like word (length > 1), so "eu vi X" stays untouched.
# ---------------------------------------------------------------------------
_ROMAN_ORDINAL_M = {
    "I": "Primeiro", "II": "Segundo", "III": "Terceiro", "IV": "Quarto", "V": "Quinto",
    "VI": "Sexto", "VII": "Sétimo", "VIII": "Oitavo", "IX": "Nono", "X": "Décimo",
    "XI": "Décimo Primeiro", "XII": "Décimo Segundo", "XIII": "Décimo Terceiro",
    "XIV": "Décimo Quarto", "XV": "Décimo Quinto", "XVI": "Décimo Sexto",
    "XVII": "Décimo Sétimo", "XVIII": "Décimo Oitavo", "XIX": "Décimo Nono",
    "XX": "Vigésimo",
}
_TRAIL_PUNCT = ".,;:!?)\"”"


def _split_trailing_punct(w: str) -> tuple[str, str]:
    i = len(w)
    while i > 0 and w[i - 1] in _TRAIL_PUNCT:
        i -= 1
    return w[:i], w[i:]


def expand_regnal_numerals(text: str) -> str:
    """"Afonso I" -> "Afonso Primeiro"; "eu vi X" is untouched."""
    words = text.split()
    out = []
    for i, w in enumerate(words):
        core, trail = _split_trailing_punct(w)
        ordinal = _ROMAN_ORDINAL_M.get(core)
        if ordinal is not None:
            if len(core) >= 2:
                out.append(ordinal + trail)
                continue
            if i > 0:
                prev_core, _ = _split_trailing_punct(words[i - 1])
                if prev_core.isalpha() and prev_core[:1].isupper() and len(prev_core) > 1:
                    out.append(ordinal + trail)
                    continue
        out.append(w)
    return " ".join(out)


# ---------------------------------------------------------------------------
# Acronyms spoken as Portuguese letter names, matched case-SENSITIVELY so
# ordinary lowercase words ("ia", "eu") are never touched.
#
# The brief calls for a general rule (spell any all-caps 2-4 letter token
# that isn't a pronounceable dictionary word/acronym), with an explicit
# allowlist for words that ARE read out loud (NASA, UNESCO, FIFA, NATO/OTAN,
# SIDA, OVNI). A generic "is this pronounceable in Portuguese" heuristic is
# too easy to get wrong on real proper nouns and product names (e.g. an
# ALLCAPS brand), so this ships the narrower, safer form the brief allows:
# an explicit dict of the acronyms in scope, plus the letter-name table so
# the dict is trivial to extend. NASA/UNESCO/FIFA/NATO/OTAN/SIDA/OVNI simply
# never appear in the dict, so they pass through unspelled.
# ---------------------------------------------------------------------------
_LETTER_NAMES = {
    "A": "á", "B": "bê", "C": "cê", "D": "dê", "E": "é", "F": "éfe", "G": "gê",
    "H": "agá", "I": "i", "J": "jota", "K": "capa", "L": "éle", "M": "éme",
    "N": "éne", "O": "ó", "P": "pê", "Q": "quê", "R": "érre", "S": "ésse",
    "T": "tê", "U": "u", "V": "vê", "W": "dâblio", "X": "xis", "Y": "ípsilon",
    "Z": "zê",
}


def _spell_letters(acronym: str) -> str:
    return " ".join(_LETTER_NAMES[c] for c in acronym)


_ACRONYMS = {
    # explicit spellings called out in the brief
    "IA": "i á", "LLM": "éle éle éme", "UTC": "u tê cê", "TTS": "tê tê ésse",
    "PT": "pê tê", "EU": "e u",
}
for _a in ("GPS", "USB", "PDF", "SMS", "CPU", "URL", "API", "IVA", "IRS", "NIF", "SNS", "PS", "PSD"):
    _ACRONYMS[_a] = _spell_letters(_a)
del _a

_TRAIL_PUNCT_WIDE = ".,;:!?)\"”…"


def _split_edges(w: str) -> tuple[str, str, str]:
    """(leading punctuation, core, trailing punctuation) of a token."""
    i, j = 0, len(w)
    while i < j and w[i] in _LEAD_PUNCT:
        i += 1
    while j > i and w[j - 1] in _TRAIL_PUNCT_WIDE:
        j -= 1
    return w[:i], w[i:j], w[j:]


def expand_acronyms(text: str) -> str:
    """"IA" -> "i á"; lowercase "ia"/"eu" (ordinary words) are untouched."""
    out = []
    for w in text.split():
        lead, core, trail = _split_edges(w)
        repl = _ACRONYMS.get(core)
        out.append(lead + (repl if repl is not None else core) + trail)
    return " ".join(out)


def normalize_orthography(text: str) -> str:
    """Apply every rule above, in the order that keeps them from interfering:
    separators and ranges (digit-only), then clock times (also digit-only),
    then abbreviations, regnal numerals and acronyms (word-token rules)."""
    text = normalize_number_separators(text)
    text = split_number_ranges(text)
    text = expand_clock_times(text)
    text = expand_abbreviations(text)
    text = expand_regnal_numerals(text)
    text = expand_acronyms(text)
    return text
