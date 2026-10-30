"""Orthographic text transforms applied BEFORE number verbalisation.

These rewrite raw written conventions (unit symbols, number ranges, clock
times, European thousands/decimal separators, honorific abbreviations, regnal
Roman numerals, letter-spelled acronyms) into plain words or digit tokens that
:func:`tugaphone.number_utils.normalize_numbers` can then read out loud. They
run at the text level, before any lattice/phoneme work, so they are plugged
into :func:`tugaphone.lattice_core._normalizer` ahead of
``normalize_numbers``.

The reading rules for ranges, clock times, separators, abbreviations, and
regnal numerals are ported from the European-Portuguese TTS front-end
tts_eu_pt (https://github.com/logus2k/tts_eu_pt), written by Antonio Cruz
and released under the Apache License 2.0. The rules from that project's
``tts_eu_pt/g2p.py`` were reimplemented here in tugaphone's own idiom; one
rule was deliberately left out: the original elides "vinte e cinco" to
"vinte cinco" in the twenties, but standard European Portuguese keeps the
conjunction, so tugaphone always reads "vinte e cinco".
"""
from __future__ import annotations

import functools
import json
import re
from pathlib import Path

from tugalex import TugaLexicon

from tugaphone.number_utils import NumberParser

_DATA = Path(__file__).parent / "data"

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
# Unit symbols. The SI writes a space between a number and its unit symbol
# (SI brochure, IPQ/Inmetro 2021, §5.4.3) and between a number and "%"
# (same brochure, p. 28). Text often glues them ("7kg", "20%") or puts the
# euro sign first ("€20"). These rules restore "<number> <symbol>", which
# normalize_numbers then reads with the unit name and number agreement.
# A symbol counts only right after digits, so the letter "m" or a word
# such as "kg" in running text is never touched.
# ---------------------------------------------------------------------------
_NUMBER = r"\d+(?:[.,]\d+)*"
_SYMBOLS = "|".join(re.escape(s) for s in
                    sorted(NumberParser.UNIT_NAMES, key=len, reverse=True))
_GLUED_UNIT = re.compile(rf"(?<![\w.,])({_NUMBER})({_SYMBOLS})(?![\w/²³])")
_EURO_FIRST = re.compile(rf"€ ?({_NUMBER})(?!\w)")
# "2,50 €" is read "dois euros e cinquenta cêntimos" (Ciberdúvidas 25561:
# "cinquenta euros e trinta cêntimos"). Only one or two decimals are cents.
_EURO_CENTS = re.compile(r"(?<![\w.,])(\d+(?:\.\d{3})*),(\d{1,2}) €")
# A "x" or "×" between two numbers is multiplication, read "vezes": "dois
# vezes dois são quatro" (Priberam DLPO, "vezes"). Hex literals ("0x1F")
# and words ("o x da questão") have a letter on one side and are untouched.
_TIMES = re.compile(r"(?<![\w.,])(\d+(?:,\d+)?) ?[x×] ?(?=\d+(?:,\d+)?(?:[x×]\d|(?!\w)))")


def _euro_cents_repl(match: "re.Match[str]") -> str:
    euros, cents = match.group(1), int(match.group(2).ljust(2, "0"))
    if cents == 0:
        return f"{euros} €"
    cents_text = f"{cents} cêntimo" if cents == 1 else f"{cents} cêntimos"
    if int(euros.replace(".", "")) == 0:
        return cents_text
    return f"{euros} € e {cents_text}"


def separate_unit_symbols(text: str) -> str:
    """"7kg" -> "7 kg"; "20%" -> "20 %"; "€20" -> "20 €";
    "2,50 €" -> "2 € e 50 cêntimos"; "15x8" -> "15 vezes 8"."""
    text = _GLUED_UNIT.sub(r"\1 \2", text)
    text = _EURO_FIRST.sub(r"\1 €", text)
    text = _EURO_CENTS.sub(_euro_cents_repl, text)
    while True:
        expanded = _TIMES.sub(r"\1 vezes ", text)
        if expanded == text:
            return text
        text = expanded


# ---------------------------------------------------------------------------
# Clock times. "HH:00" is read "<hora> hora(s)" -- the digit token is left for
# normalize_numbers, which already picks the feminine form ("uma", "duas",
# "vinte e uma", ...) from the following "hora"/"horas" noun, so no separate
# gender table is needed here. Any other "HH:MM" is read "<hora> e <minutos>".
# Whole hours additionally accept 24 ("24:00" -> "vinte e quatro horas");
# 25+ is not a clock hour and is left alone. Non-whole times keep the
# ordinary 0-23 range.
#
# The minute is emitted WITHOUT a leading zero ("9:05" -> "9 e 5", not
# "9 e 05"): normalize_numbers's tokenizer splits on whitespace, and a
# leading zero would otherwise make the token ambiguous with an ordinal or
# decimal spelling. Any punctuation immediately following the minutes/hour
# digits is left glued to them ("16:54." -> "16 e 54.") -- normalize_numbers
# itself splits trailing punctuation off a numeric token before checking
# whether it is a number, spells the digits, and glues the punctuation back
# on, so there is no need to detach it here with a space.
# ---------------------------------------------------------------------------
_HOUR = r"(?:[01]?\d|2[0-3])"
_HOUR_OR_24 = r"(?:[01]?\d|2[0-4])"
_PUNCT = r"[.,;:!?)\"”…]?"
_WHOLE_HOUR = re.compile(rf"\b({_HOUR_OR_24}):00({_PUNCT})")
_CLOCK_TIME = re.compile(rf"\b({_HOUR}):([0-5]\d)({_PUNCT})")


def _whole_hour_repl(match: "re.Match[str]") -> str:
    hh, punct = match.group(1), match.group(2)
    unit = "hora" if int(hh) == 1 else "horas"
    return f"{hh} {unit}{punct}"


def _clock_time_repl(match: "re.Match[str]") -> str:
    hh, mm, punct = match.group(1), match.group(2), match.group(3)
    mm = str(int(mm))  # drop the leading zero: "05" -> "5"
    return f"{hh} e {mm}{punct}"


def expand_clock_times(text: str) -> str:
    """"16:00" -> "16 horas"; "24:00" -> "24 horas"; "16:54" -> "16 e 54".
    Whole hours must be expanded first, so the ":00" case doesn't fall
    through to "16 e 0"."""
    text = _WHOLE_HOUR.sub(_whole_hour_repl, text)
    return _CLOCK_TIME.sub(_clock_time_repl, text)


# ---------------------------------------------------------------------------
# Given names and their grammatical gender come from tugalex:
# TugaLexicon.get_given_name_gender gives "m", "f", "mf" or None.
# ---------------------------------------------------------------------------
def _name_gender(word: str) -> str:
    """The gender a name gives a title or an ordinal: a name of both genders,
    or a word that is not a name, gives masculine."""
    return "feminine" if TugaLexicon.get_given_name_gender(word) == "f" else "masculine"


# ---------------------------------------------------------------------------
# Abbreviations. Two groups:
#
# * UNCONDITIONAL: expanded wherever they appear, with no regard to what
#   follows -- section/reference markers ("vs.", "pág./págs.", "tel.",
#   "art.", "fig.", "cap.", "séc.") and place-name abbreviations ("Av.",
#   "R.", "Lx.", "n.º"/"nº") that stand for the same word whether followed
#   by a capitalised name, a lowercase word, or end of sentence.
# * NAME-INTRODUCING: "D." is expanded only right before a capitalised word
#   (the name it introduces): alone it is as often an initial or a letter.
#   It reads "Dona" before a feminine given name ("D. Maria") and "Dom"
#   otherwise: "D." is the abbreviation "de dom e de dona" (Priberam).
#   The personal titles "Sr.", "Dr.", "Eng.", "Prof." and their feminine and
#   plural forms stand for one word wherever they appear ("o Sr. presidente",
#   "os Srs. deputados", "falei com o Dr."), so they are unconditional.
#
# Forms with a superscript ending ("Sr.ª", "Sr.as", "n.os", "Ex.mo") match no
# ordinary word, so they are unconditional. The expansions follow the
# Vocabulário Ortográfico of the Academia das Ciências de Lisboa ("Sr.ª"
# senhora, "V. Ex.ª" Vossa Excelência, "S. Ex.ª" Sua Excelência, "Ex.mo"
# Excelentíssimo, "Dr.ª" Doutora, "Eng.ª" Engenheira, "prof.ª" professora)
# and the vocabularies quoted by Ciberdúvidas: 33650 ("Srs.", "Sr.as",
# "VV. Ex.as", "V. Exas.", "Exmos.") and 15826 ("n.os", "Ex.as").
# ---------------------------------------------------------------------------
_UNCONDITIONAL_ABBREVIATIONS = {
    "vs.": "versus",
    "pág.": "página",
    "págs.": "páginas",
    "tel.": "telefone",
    "art.": "artigo",
    "fig.": "figura",
    "cap.": "capítulo",
    "séc.": "século",
    "Av.": "Avenida",
    "R.": "Rua",
    "Lx.": "Lisboa",
    "n.º": "número",
    "nº": "número",
    "N.º": "número",
    "Nº": "número",
    "n.os": "números",
    "N.os": "números",
    "Sr.ª": "Senhora",
    "Sr.as": "Senhoras",
    "Dr.ª": "Doutora",
    "Eng.ª": "Engenheira",
    "Prof.ª": "Professora",
    "Ex.ª": "Excelência",
    "Ex.as": "Excelências",
    "Exa.": "Excelência",
    "Exas.": "Excelências",
    "Ex.mo": "Excelentíssimo",
    "Ex.ma": "Excelentíssima",
    "Ex.mos": "Excelentíssimos",
    "Ex.mas": "Excelentíssimas",
    "Exmo.": "Excelentíssimo",
    "Exma.": "Excelentíssima",
    "Exmos.": "Excelentíssimos",
    "Exmas.": "Excelentíssimas",
}
_UNCONDITIONAL_ABBREVIATIONS.update({
    "Sr.": "Senhor",
    "Sra.": "Senhora",
    "Srs.": "Senhores",
    "Sras.": "Senhoras",
    "Dr.": "Doutor",
    "Dra.": "Doutora",
    "Eng.": "Engenheiro",
    "Prof.": "Professor",
})
_HONORIFIC_ABBREVIATIONS = {
    "D.": "Dom",
}
# Nouns a capital letter labels ("a vitamina D.", "a alínea D."): after them
# "D." is the letter, whatever word follows.
_LETTER_LABEL_NOUNS = frozenset({
    "vitamina", "letra", "alínea", "classe", "grupo", "tipo", "plano",
})

# "V." and "S." are the possessive of a following "Excelência" form only:
# alone, "V." is a letter or a Roman numeral and "S." is "São".
_POSSESSIVES = {
    "V.": ("Vossa", "Vossas"),
    "VV.": ("Vossas", "Vossas"),
    "Vv.": ("Vossas", "Vossas"),
    "S.": ("Sua", "Suas"),
}
_EXCELENCIA_PLURAL = {"Ex.as": True, "Exas.": True, "Ex.ª": False, "Exa.": False}
# Punctuation after an abbreviation's own period ("V. Ex.ª, obrigado").
_ABBREVIATION_TRAIL = ",;:!?)\"”"

_LEAD_PUNCT = "(“\"'¿¡"


def _is_capitalised(word: str) -> bool:
    core = word.lstrip(_LEAD_PUNCT)
    return bool(core) and core[0].isupper()


def expand_abbreviations(text: str) -> str:
    """"Sr. Silva" -> "Senhor Silva"; "D. Maria" -> "Dona Maria"; "n.º 4" ->
    "número 4"; "Av. Liberdade"
    or a bare "R." at sentence end both -> "Avenida"/"Rua" regardless of
    capitalisation, since these stand for the same word either way."""
    words = text.split()
    cores = [w.rstrip(_ABBREVIATION_TRAIL) for w in words]
    out = []
    for i, w in enumerate(words):
        core, trail = cores[i], w[len(cores[i]):]
        following = cores[i + 1] if i + 1 < len(words) else None
        possessive = _POSSESSIVES.get(core)
        if possessive is not None and following in _EXCELENCIA_PLURAL:
            out.append(possessive[_EXCELENCIA_PLURAL[following]] + trail)
            continue
        expansion = _UNCONDITIONAL_ABBREVIATIONS.get(core)
        if expansion is not None:
            out.append(expansion + trail)
            continue
        expansion = _HONORIFIC_ABBREVIATIONS.get(core)
        after_label = i > 0 and cores[i - 1].lower() in _LETTER_LABEL_NOUNS
        if (expansion is not None and following is not None
                and _is_capitalised(words[i + 1]) and not after_label):
            if _name_gender(_split_edges(following)[1]) == "feminine":
                expansion = "Dona"
            out.append(expansion + trail)
            continue
        out.append(w)
    return " ".join(out)


# ---------------------------------------------------------------------------
# Roman numerals after centuries, rulers, popes and parts of a work. After
# its noun, a numeral up to ten reads as an ordinal and above ten as a
# cardinal: "até 10 (Celso Cunha e Lindley Cintra) inclusive, usam-se os
# ordinais e depois os cardinais, sempre que o numeral vier depois do
# substantivo" (Ciberdúvidas 14284) -- "D. João V (quinto)", "Luís XIV é
# «catorze»", "o século XV é o século «quinze»" (Ciberdúvidas 14167). The
# Nova Gramática applies the rule to every part of a work, and a numeral
# before its noun keeps the ordinal above ten (Ciberdúvidas 11716).
#
# An ordinal agrees with its noun or name: "D. Maria II" is "Dona Maria
# Segunda", "a parte V" is "a parte quinta". A cardinal above ten is a label
# and stays masculine, "sente-se a omissão da palavra número" (Cunha &
# Cintra, quoted by Ciberdúvidas 33468).
#
# When a numeral converts:
# * after a part-of-work noun, matched case-insensitively ("O SÉCULO XIX");
# * never inside a run of all-caps words ("EU VI O FILME"), or after the
#   word of a fixed expression in data/letter_expressions.json ("raio X");
# * a multi-letter numeral of I, V and X converts anywhere else;
# * a single I, V or X converts only after a given name ("Isabel I"), so
#   "eu vi X" and "Raio X" stay untouched;
# * a numeral with L, C, D or M converts only after a part-of-work noun, so
#   "tamanho XL" and "o CD" stay untouched.
# ---------------------------------------------------------------------------
_ROMAN = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
_WORK_PARTS = {
    "século": "masculine", "capítulo": "masculine", "tomo": "masculine",
    "volume": "masculine", "livro": "masculine", "canto": "masculine",
    "ato": "masculine", "título": "masculine",
    "parte": "feminine", "secção": "feminine", "seção": "feminine",
}
# Articles and contractions before a numeral that precedes its noun, and the
# gender of the noun they announce.
_PRENOMINAL = {
    "o": "masculine", "os": "masculine", "do": "masculine", "dos": "masculine",
    "no": "masculine", "nos": "masculine", "ao": "masculine", "aos": "masculine",
    "pelo": "masculine", "pelos": "masculine",
    "a": "feminine", "as": "feminine", "da": "feminine", "das": "feminine",
    "na": "feminine", "nas": "feminine", "à": "feminine", "às": "feminine",
    "pela": "feminine", "pelas": "feminine",
}
_TRAIL_PUNCT = ".,;:!?)\"”"


@functools.lru_cache(maxsize=1)
def _letter_expressions() -> frozenset[tuple[str, str]]:
    """(lowercase word, letter) pairs of data/letter_expressions.json."""
    data = json.loads((_DATA / "letter_expressions.json").read_text(encoding="utf-8"))
    pairs = (phrase.rsplit(" ", 1) for phrase in data["expressions"])
    return frozenset((word.lower(), letter) for word, letter in pairs)


def _split_trailing_punct(w: str) -> tuple[str, str]:
    i = len(w)
    while i > 0 and w[i - 1] in _TRAIL_PUNCT:
        i -= 1
    return w[:i], w[i:]


def _is_brazilian(lang: str) -> bool:
    return "pt-br" in lang.lower()


def _roman_value(numeral: str) -> int | None:
    if not numeral or not _ROMAN.fullmatch(numeral):
        return None
    values = [_ROMAN_VALUES[c] for c in numeral]
    return sum(-v if v < nxt else v for v, nxt in zip(values, values[1:] + [0]))


def _is_caps_word(core: str) -> bool:
    return any(c.isalpha() for c in core) and core == core.upper()


def _in_caps_run(cores: list[str], i: int) -> bool:
    """Whether cores[i] stands in a run of all-caps words that holds a word
    of two or more letters other than a Roman numeral ("EU VI O FILME").
    "O XIX Congresso" is not such a run."""
    start, end = i, i
    while start > 0 and _is_caps_word(cores[start - 1]):
        start -= 1
    while end + 1 < len(cores) and _is_caps_word(cores[end + 1]):
        end += 1
    return any(sum(c.isalpha() for c in w) >= 2 and _roman_value(w) is None
               for w in cores[start:end + 1])


def _converts(numeral: str, prev_word: str | None, cores: list[str], i: int) -> bool:
    if prev_word is not None and (prev_word.lower(), numeral) in _letter_expressions():
        return False
    if prev_word is not None and prev_word.lower() in _WORK_PARTS:
        return True
    if _in_caps_run(cores, i) or not set(numeral) <= set("IVX"):
        return False
    return len(numeral) >= 2 or (prev_word is not None and TugaLexicon.get_given_name_gender(prev_word) is not None)


def _read_roman(value: int, prev_word: str | None, lang: str) -> str:
    article = _PRENOMINAL.get(prev_word.lower()) if prev_word else "masculine"
    if article is not None:
        gender, as_ordinal = article, True
    elif value <= 10:
        gender = _WORK_PARTS.get(prev_word.lower()) or _name_gender(prev_word)
        as_ordinal = True
    else:
        gender, as_ordinal = "masculine", False
    return NumberParser.pronounce_number_word(
        str(value), gender=gender, as_ordinal=as_ordinal, is_brazilian=_is_brazilian(lang))


def _title(reading: str) -> str:
    return " ".join(w if w == "e" else w.capitalize() for w in reading.split())


def expand_regnal_numerals(text: str, lang: str = "pt-PT") -> str:
    """"Afonso I" -> "Afonso Primeiro"; "Isabel II" -> "Isabel Segunda";
    "o século XIX" -> "o século dezanove"; "a II Guerra Mundial" -> "a
    Segunda Guerra Mundial"; "eu vi X", "Raio X" and "EU VI O FILME" are
    untouched."""
    words = text.split()
    cores = [_split_edges(w)[1] for w in words]
    out = []
    for i, w in enumerate(words):
        core, trail = _split_trailing_punct(w)
        value = _roman_value(core)
        prev_core = _split_trailing_punct(words[i - 1])[0] if i > 0 else None
        if value is None or not _converts(core, prev_core, cores, i):
            out.append(w)
            continue
        reading = _read_roman(value, prev_core, lang)
        # The numeral takes the case of the name it belongs to: the name
        # before it ("Pio Doze") or, before its noun, the name after it ("a
        # Segunda Guerra Mundial"). After a common noun it is lowercase ("o
        # século dezanove").
        if prev_core is None or prev_core.lower() in _PRENOMINAL:
            name = words[i + 1] if i + 1 < len(words) else None
            capitalised = name is None or _is_capitalised(name)
        else:
            capitalised = prev_core[:1].isupper()
        out.append((_title(reading) if capitalised else reading) + trail)
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
# Acronyms whose letters also spell a Portuguese word ("IA" and the verb
# form "ia", "EU" and the pronoun "eu"): inside all-caps text ("ELE IA SAIR",
# "EU VI O FILME") they are the word.
_WORD_ACRONYMS = frozenset({"IA", "EU"})
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


def _in_caps_text(cores: list[str], i: int) -> bool:
    """Whether cores[i] stands in a run of all-caps words that holds another
    word of two or more letters ("ELA E EU"), so the run is all-caps text and
    not one acronym in mixed-case text ("A IA aprende")."""
    start, end = i, i
    while start > 0 and _is_caps_word(cores[start - 1]):
        start -= 1
    while end + 1 < len(cores) and _is_caps_word(cores[end + 1]):
        end += 1
    return any(j != i and sum(c.isalpha() for c in cores[j]) >= 2
               for j in range(start, end + 1))


def expand_acronyms(text: str) -> str:
    """"IA" -> "i á"; lowercase "ia"/"eu" (ordinary words) are untouched."""
    words = text.split()
    cores = [_split_edges(w)[1] for w in words]
    out = []
    for i, w in enumerate(words):
        lead, core, trail = _split_edges(w)
        repl = _ACRONYMS.get(core)
        if core in _WORD_ACRONYMS and _in_caps_text(cores, i):
            repl = None
        out.append(lead + (repl if repl is not None else core) + trail)
    return " ".join(out)


# ---------------------------------------------------------------------------
# Letter-digit codes ("T2" housing typology, "A3" motorway, "RTP2", "mp3"):
# the letters by their names, then the number as a cardinal. A number that
# labels something is invariable, "sente-se a omissão da palavra número"
# (Cunha & Cintra, quoted by Ciberdúvidas 33468), so it is masculine even
# before a feminine word ("o T2 na cidade" -> "tê dois"). The reading is the
# same whatever the code stands for, so no context is needed. Codes take
# one to three capitals or one or two lowercase letters, so longer
# capitalised words ("COVID19") and ordinary lowercase words are left alone.
# Right after a number the letters are a unit symbol ("10 m2"), not a code.
# ---------------------------------------------------------------------------
_LETTER_DIGIT_CODE = re.compile(r"([A-Z]{1,3}|[a-z]{1,2})(\d+)")


def expand_letter_digit_codes(text: str, lang: str = "pt-PT") -> str:
    """"T2" -> "tê dois"; "RTP2" -> "érre tê pê dois"; "10 m2" is untouched."""
    words = text.split()
    out = []
    for i, w in enumerate(words):
        lead, core, trail = _split_edges(w)
        match = _LETTER_DIGIT_CODE.fullmatch(core)
        after_number = i > 0 and _split_edges(words[i - 1])[1].isdigit()
        if match is None or after_number:
            out.append(w)
            continue
        letters, digits = match.groups()
        number = NumberParser.pronounce_number_word(
            digits, gender="masculine", as_ordinal=False,
            is_brazilian=_is_brazilian(lang))
        out.append(f"{lead}{_spell_letters(letters.upper())} {number}{trail}")
    return " ".join(out)


def normalize_orthography(text: str, lang: str = "pt-PT") -> str:
    """Apply every rule above, in the order that keeps them from interfering:
    unit symbols first (the euro-cents rule needs the decimal comma), then
    separators and ranges (digit-only), then clock times (also digit-only),
    then abbreviations, regnal numerals and acronyms (word-token rules)."""
    text = separate_unit_symbols(text)
    text = normalize_number_separators(text)
    text = split_number_ranges(text)
    text = expand_clock_times(text)
    text = expand_abbreviations(text)
    text = expand_regnal_numerals(text, lang)
    text = expand_acronyms(text)
    text = expand_letter_digit_codes(text, lang)
    return text
