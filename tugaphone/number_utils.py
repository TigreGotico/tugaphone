"""Numbers, dates, times, money and measures, read by text2spoken.

text2spoken reads first, so where it reads a form, its reading stands. The
lects that write the European AO1990 norm read ``pt-PT``, and the lects that
write the Brazilian norm read ``pt-BR``. For a form that text2spoken leaves as
written, a fallback rewrite below reads it, and text2spoken reads the digits
that the rewrite leaves. Each fallback names the text2spoken issue for its
form, and goes when text2spoken reads the form.
"""
import re
import string
import unicodedata
import warnings
from typing import Optional

from text2spoken import FrozenMap, GrammaticalGender, NormalizationParams, normalize
from tugalex import TugaLexicon

from tugaphone.registry import resolve_lect, spelling_norm
from tugaphone.version import VERSION_MAJOR

#: The release that removes :class:`NumberParser`.
NUMBER_PARSER_REMOVAL_VERSION = f"{VERSION_MAJOR + 1}.0.0"


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


def text2spoken_reading(text: str, lang: str, scale: Optional[str] = None,
                        gender: Optional[str] = None) -> str:
    """``text`` read by text2spoken in the variety of ``lang``. ``gender``
    ("masculine" or "feminine") is the gender of a number that no word in the
    text decides."""
    default_gender = FrozenMap({"pt": GrammaticalGender(gender)}) if gender else FrozenMap()
    return normalize(text, text2spoken_tag(lang),
                     NormalizationParams(scale=scale, default_gender=default_gender))


def warn_unread_digits(spoken: str, text: str, lang: str) -> None:
    """Give an :class:`UnreadFormWarning` for each form with digits left in
    ``spoken``, the reading of ``text``."""
    for form in re.findall(r"\S*\d\S*", spoken):
        warnings.warn(f"{text2spoken_tag(lang)}: no reading for {form!r} in {text!r}; "
                      "its digits are dropped", UnreadFormWarning, stacklevel=3)


# Unit symbols read after a number, as (singular, plural) names. Symbols
# and names follow the SI brochure ("Sistema Internacional de Unidades
# (SI)", Inmetro/IPQ, 2021, ISBN 978-85-86920-28-8, §5.2-5.3): the symbol
# is invariable, "l" and "L" are both the litre, "%" reads "por cento". The
# names are the dictionary forms ("quilómetro", "quilograma"); pt-BR writes
# "quilômetro". Every name is masculine -- "o grama", "duzentos gramas"
# (Inmetro, "Unidades Legais de Medida") -- so the number before a symbol is
# masculine.
UNIT_NAMES = {
    "%": ("por cento", "por cento"),
    "€": ("euro", "euros"),
    "mm": ("milímetro", "milímetros"),
    "cm": ("centímetro", "centímetros"),
    "m": ("metro", "metros"),
    "km": ("quilómetro", "quilómetros"),
    "km/h": ("quilómetro por hora", "quilómetros por hora"),
    "mm2": ("milímetro quadrado", "milímetros quadrados"),
    "cm2": ("centímetro quadrado", "centímetros quadrados"),
    "cm²": ("centímetro quadrado", "centímetros quadrados"),
    "m2": ("metro quadrado", "metros quadrados"),
    "m²": ("metro quadrado", "metros quadrados"),
    "km2": ("quilómetro quadrado", "quilómetros quadrados"),
    "km²": ("quilómetro quadrado", "quilómetros quadrados"),
    "cm3": ("centímetro cúbico", "centímetros cúbicos"),
    "cm³": ("centímetro cúbico", "centímetros cúbicos"),
    "m3": ("metro cúbico", "metros cúbicos"),
    "m³": ("metro cúbico", "metros cúbicos"),
    "mg": ("miligrama", "miligramas"),
    "g": ("grama", "gramas"),
    "kg": ("quilograma", "quilogramas"),
    "ml": ("mililitro", "mililitros"),
    "mL": ("mililitro", "mililitros"),
    "cl": ("centilitro", "centilitros"),
    "cL": ("centilitro", "centilitros"),
    "dl": ("decilitro", "decilitros"),
    "dL": ("decilitro", "decilitros"),
    "l": ("litro", "litros"),
    "L": ("litro", "litros"),
}


# ---------------------------------------------------------------------------
# Number ranges: a dash BETWEEN two digits is a numeric range, read " a ".
# text2spoken leaves a score ("3-2") and a range with an em dash ("10—20")
# as written: https://github.com/TigreGotico/text2spoken/issues/250
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
# text2spoken reads both, so normalize_numbers does not run this rewrite.
# ---------------------------------------------------------------------------
_THOUSANDS_DOT = re.compile(r"(?<=\d)\.(?=\d)")
_DECIMAL_COMMA = re.compile(r"(?<=\d),(?=\d)")


def normalize_number_separators(text: str) -> str:
    """"92.073" -> "92073"; "10,4" -> "10 vírgula 4"."""
    text = _THOUSANDS_DOT.sub("", text)
    return _DECIMAL_COMMA.sub(" vírgula ", text)


# ---------------------------------------------------------------------------
# Unit symbols. The SI writes a space between a number and its unit symbol
# (SI brochure, Inmetro/IPQ 2021, §5.4.3) and between a number and "%"
# (same brochure, p. 28). Text often glues them ("7kg", "20%") or puts the
# euro sign first ("€20"). These rules restore "<number> <symbol>", which
# normalize_numbers then reads with the unit name and number agreement.
# A symbol counts only right after digits, so the letter "m" or a word
# such as "kg" in running text is never touched. text2spoken leaves a glued
# litre symbol with a capital L ("10mL", "2L") as written:
# https://github.com/TigreGotico/text2spoken/issues/249
# ---------------------------------------------------------------------------
_NUMBER = r"\d+(?:[.,]\d+)*"
_SYMBOLS = "|".join(re.escape(s) for s in
                    sorted(UNIT_NAMES, key=len, reverse=True))
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
# Clock times. "HH:00" is read "<hora> hora(s)", and the reader of the digits
# takes the feminine ("uma", "duas") from "hora". Any other "HH:MM" is read
# "<hora> e <minutos>". text2spoken leaves a clock time with no time word
# before it ("Chegou 16:54.", "9:05") and "24:00" as written:
# https://github.com/TigreGotico/text2spoken/issues/251
# A whole hour can be 24 ("24:00" -> "vinte e quatro horas"); other times
# take hours 0-23. The minute loses its leading zero ("9:05" -> "9 e 5"), so
# it does not read as an ordinal or a decimal. Punctuation after the digits
# stays glued to them ("16:54." -> "16 e 54."): the reader of the digits
# splits it off.
# ---------------------------------------------------------------------------
_HOUR = r"(?:[01]?\d|2[0-3])"
_HOUR_OR_24 = r"(?:[01]?\d|2[0-4])"
_PUNCT = r"[.,;:!?)\"”…]?"
_WHOLE_HOUR = re.compile(rf"\b({_HOUR_OR_24}):00(?:(\s+horas?\b)|({_PUNCT}))")
_CLOCK_TIME = re.compile(rf"\b({_HOUR}):([0-5]\d)({_PUNCT})")


def _whole_hour_repl(match: "re.Match[str]") -> str:
    hh, noun, punct = match.groups()
    if noun:  # "12:00 horas" already names the hour
        return hh + noun
    unit = "hora" if int(hh) == 1 else "horas"
    return f"{hh} {unit}{punct}"


def _clock_time_repl(match: "re.Match[str]") -> str:
    hh, mm, punct = match.groups()
    return f"{hh} e {int(mm)}{punct}"


def expand_clock_times(text: str) -> str:
    """"16:00" -> "16 horas"; "12:00 horas" -> "12 horas"; "16:54" -> "16 e 54".
    Whole hours must be expanded first, so the ":00" case doesn't fall
    through to "16 e 0"."""
    text = _WHOLE_HOUR.sub(_whole_hour_repl, text)
    return _CLOCK_TIME.sub(_clock_time_repl, text)


# ---------------------------------------------------------------------------
# Number words, so a rule can tell that a word ends a spoken number ("oitenta
# m2" after text2spoken). A spoken number joins its words with "e" and its
# decimal part with "vírgula".
# ---------------------------------------------------------------------------
_NUMBER_WORDS = frozenset("""
    zero um uma dois duas três quatro cinco seis sete oito nove dez onze doze
    treze catorze quatorze quinze dezasseis dezesseis dezassete dezessete
    dezoito dezanove dezenove vinte trinta quarenta cinquenta sessenta setenta
    oitenta noventa cem cento duzentos duzentas trezentos trezentas
    quatrocentos quatrocentas quinhentos quinhentas seiscentos seiscentas
    setecentos setecentas oitocentos oitocentas novecentos novecentas mil
    milhão milhões bilião biliões bilhão bilhões trilião triliões trilhão
    trilhões
""".split())
_NUMBER_JOINERS = frozenset({"e", "vírgula"})


def is_number_word(core: str) -> bool:
    return core.isdigit() or core.lower() in _NUMBER_WORDS


def _is_mark(ch: str) -> bool:
    category = unicodedata.category(ch)
    return category[0] == "P" or category in ("Sm", "Sk")


_SIGNED_NUMBER = re.compile(r"[-−]?\d+(?:[.,]\d+)*")


def _split_trailing_marks(word: str) -> tuple[str, str]:
    i = len(word)
    while i > 0 and _is_mark(word[i - 1]):
        i -= 1
    return word[:i], word[i:]


# ---------------------------------------------------------------------------
# A "x" between two numbers is multiplication, read "vezes": "dois vezes dois
# são quatro" (Priberam DLPO, "vezes"). Each factor reads alone, as a
# masculine cardinal. text2spoken reads "2×2". It leaves "15x8" as written,
# and reads "2 x 2" as "dois x dois", leaving the "x":
# https://github.com/TigreGotico/text2spoken/issues/240
# ---------------------------------------------------------------------------
_FACTOR = r"\d+(?:,\d+)?"
_PRODUCT_X = re.compile(rf"(?<![\w.,]){_FACTOR}(?: ?x ?{_FACTOR})+(?!\w)")


def read_multiplication_signs(text: str, lang: str = "pt-PT") -> str:
    """"15x8" -> "quinze vezes oito"; "2 x 3 x 4" -> "dois vezes três vezes quatro"."""
    def read(match: "re.Match[str]") -> str:
        factors = re.split(r" ?x ?", match.group())
        return " vezes ".join(text2spoken_reading(f, lang, gender="masculine") for f in factors)
    return _PRODUCT_X.sub(read, text)


def _written_after_digits(text: str, symbols: frozenset[str]) -> list[bool]:
    """For each word of ``text`` in ``symbols``, in order: whether a number in
    digits comes before it."""
    words = text.split()
    return [i > 0 and _SIGNED_NUMBER.fullmatch(words[i - 1]) is not None
            for i, w in enumerate(words) if _split_trailing_marks(w)[0] in symbols]


def _read_flagged(text: str, symbols: frozenset[str], flags: list[bool], read) -> str:
    """Rewrite the words of ``text`` in ``symbols`` whose flag is set, with
    ``read(words, i)``. text2spoken leaves these words as written, so they come
    in the same order as in the input; if their count differs, none is read."""
    words = text.split()
    positions = [i for i, w in enumerate(words) if _split_trailing_marks(w)[0] in symbols]
    if len(positions) != len(flags):
        return text
    for i, flag in zip(positions, flags):
        if flag:
            words[i] = read(words, i)
    return " ".join(words)


_SPACED_PRODUCT = re.compile(rf"(?<![\w.,]){_NUMBER}(?: x {_NUMBER})+(?!\w)")


def read_spoken_times(spoken: str, written: str, lang: str = "pt-PT") -> str:
    """The "x" that text2spoken leaves in a product written in digits: "2 x 2",
    read "dois x dois", gives "dois vezes dois". Each product of ``written`` is
    found in ``spoken`` by the readings of its factors, in either gender, so a
    product that text2spoken read ("4 x 5 m", "quatro por cinco metros") does
    not stop the next one. A product that the author wrote in words reads the
    same and keeps its "x": as many matches as ``written`` has between this
    product and the one before are skipped."""
    start = written_start = 0
    for product in _SPACED_PRODUCT.finditer(written):
        factors = ["|".join(re.escape(text2spoken_reading(factor, lang, gender=gender))
                            for gender in ("masculine", "feminine"))
                   for factor in product.group().split(" x ")]
        spoken_product = re.compile(r"(?<!\w)" + " x ".join(f"(?:{f})" for f in factors) + r"(?!\w)")
        in_words = len(spoken_product.findall(written, written_start, product.start()))
        written_start = product.end()
        match = spoken_product.search(spoken, start)
        for _ in range(in_words):
            match = match and spoken_product.search(spoken, match.end())
        if match:
            reading = match.group().replace(" x ", " vezes ")
            spoken = spoken[:match.start()] + reading + spoken[match.end():]
            start = match.start() + len(reading)
    return spoken


# ---------------------------------------------------------------------------
# Scientific notation: "1e6" is "um vezes dez elevado a seis". Mantissa and
# exponent read alone. text2spoken leaves the notation as written:
# https://github.com/TigreGotico/text2spoken/issues/249
# ---------------------------------------------------------------------------
_SCIENTIFIC = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)[eE]([+\-−]?\d+)(?!\w)")


def read_scientific_notation(text: str, lang: str = "pt-PT") -> str:
    """"1e6" -> "um vezes dez elevado a seis"; "2,5e3" -> "dois vírgula cinco
    vezes dez elevado a três"."""
    def read(match: "re.Match[str]") -> str:
        mantissa = text2spoken_reading(match.group(1).replace(".", ","), lang, gender="masculine")
        exponent = text2spoken_reading(match.group(2).replace("−", "-"), lang, gender="masculine")
        return f"{mantissa} vezes dez elevado a {exponent}"
    return _SCIENTIFIC.sub(read, text)


# ---------------------------------------------------------------------------
# Unit symbols after a number that text2spoken reads but whose symbol it leaves
# as written ("dez m2"): https://github.com/TigreGotico/text2spoken/issues/249
# The names follow the SI brochure (Inmetro/IPQ 2021) in UNIT_NAMES. The
# number takes the singular as in the CLDR 49 plural rules, which text2spoken
# follows for "metro": pt-PT only for "um" ("one: i = 1 and v = 0"), pt-BR
# for an integer part of zero or one ("one: i = 0..1"), so "um vírgula oito
# litro" in pt-BR.
# ---------------------------------------------------------------------------
_UNREAD_UNITS = frozenset({"mm2", "cm2", "m2", "km2", "cm3", "m3", "mg", "mL", "cl", "cL", "dl", "dL", "L"})


def _number_before(words: list[str], i: int) -> list[str]:
    """The words of the spoken number that ends at words[i - 1]."""
    j = i
    while j > 0 and (is_number_word(words[j - 1])
                     or (words[j - 1].lower() in _NUMBER_JOINERS and j > 1
                         and is_number_word(words[j - 2]))):
        j -= 1
    return [w.lower() for w in words[j:i]]


def read_unit_symbols(spoken: str, written: str, lang: str = "pt-PT") -> str:
    """The unit symbols of ``spoken`` that follow a number written in digits in
    ``written``: "10 mg", read "dez mg", gives "dez miligramas". In "dois L"
    the "L" is a letter and stays."""
    brazilian = text2spoken_tag(lang) == "pt-BR"
    flags = _written_after_digits(separate_unit_symbols(written), _UNREAD_UNITS)

    def read(words: list[str], i: int) -> str:
        symbol, trail = _split_trailing_marks(words[i])
        number = _number_before(words, i)
        if brazilian:
            integer = number[:number.index("vírgula")] if "vírgula" in number else number
            plural = integer not in (["zero"], ["um"], ["uma"])
        else:
            plural = number not in (["um"], ["uma"])
        name = UNIT_NAMES[symbol][plural]
        return (name.replace("quilómetro", "quilômetro") if brazilian else name) + trail
    return _read_flagged(spoken, _UNREAD_UNITS, flags, read)


# ---------------------------------------------------------------------------
# A number between marks ("/7/", ":7:") reads alone, as a masculine cardinal.
# A mark is punctuation or a math or modifier symbol. text2spoken reads it
# wrong or leaves it as written: https://github.com/TigreGotico/text2spoken/issues/250
# ---------------------------------------------------------------------------
def read_joined_numbers(text: str, lang: str = "pt-PT") -> str:
    """"casa /7/ casa" -> "casa /sete/ casa"; "25:00" is untouched."""
    out = []
    for w in text.split():
        i, j = 0, len(w)
        while i < j and _is_mark(w[i]):
            i += 1
        while j > i and _is_mark(w[j - 1]):
            j -= 1
        core = w[i:j]
        if core.isdecimal() and (i or j < len(w)):
            w = w[:i] + text2spoken_reading(core, lang, gender="masculine") + w[j:]
        out.append(w)
    return " ".join(out)


# ---------------------------------------------------------------------------
# text2spoken leaves a bare dot number as written: a section ("secção 3.2"),
# a version or name ("Indústria 4.0", "Romanos 13.8") or a rare decimal
# (https://github.com/TigreGotico/text2spoken/issues/242). Most are labels, so
# this rewrite reads them with "ponto", as text2spoken reads a version
# (tugaphone#324). After "às", "das" or "pelas" text2spoken leaves only an
# amount, which its clock guard keeps out of the clock reading (text2spoken#522),
# so that number reads as a decimal. "92.073" is a thousands group.
# ---------------------------------------------------------------------------
_DOT_NUMBER = re.compile(r"(?<![\w.,])(\d+)\.(\d+)(?![\w,]|\.\w)")
_CLOCK_WORD_BEFORE = re.compile(r"\b(?:às|das|pelas)\s+$", re.IGNORECASE)


def read_dot_numbers(text: str) -> str:
    """"secção 3.2" -> "secção 3 ponto 2"; "das 4.25 por cento" -> "das 4,25 por cento"."""
    def read(m):
        whole, part = m.groups()
        if len(part) == 3:
            return m.group()
        if _CLOCK_WORD_BEFORE.search(text, 0, m.start()):
            return f"{whole},{part}"
        rest = part.lstrip("0") or "0"
        return f"{whole} ponto {'zero ' * (len(part) - len(rest))}{rest}"
    return _DOT_NUMBER.sub(read, text)


# ---------------------------------------------------------------------------
# A pair of numbers in digits, "de 1 a 2 casas" or "entre 1 e 2 casas", whose
# noun may give the first number another gender. text2spoken leaves the pair
# as written: https://github.com/TigreGotico/text2spoken/issues/134
# No source gives the gender of the first number, so it reads in the
# masculine, and text2spoken then reads the second number with its noun.
# text2spoken also leaves a pair that it should read when a comma or a closing
# bracket follows the second number ("de 1 a 2, casas", "o valor (de 2 a 3)
# varia muito"): the mark does not end the pair, and a verb that ends in -a
# ("varia", "ajuda") reads as a feminine noun.
# https://github.com/TigreGotico/text2spoken/issues/272
# When a comma or a stop follows the second number, no noun counts the pair,
# and both numbers read in the masculine: "Venceu por 2 a 0, nesta
# terça-feira" -> "dois a zero" (text2spoken#272 and its pt-512 row).
# This rewrite runs on what text2spoken read, so a pair that text2spoken reads
# keeps its reading.
# ---------------------------------------------------------------------------
_OPENING_MARK = r"[(«\"“']?"
_PAUSE = r"[)»\"”']?[,;.!?](?![\dºª])"
_PAIR = re.compile(
    rf"(?<![\w.,])(?:(?<=\b[Ee]ntre\s)|(?<=\bENTRE\s))(?P<first>{_NUMBER})"
    rf"(?P<link>\s+[eE]\s+{_OPENING_MARK})(?P<second>{_NUMBER})(?P<pause>{_PAUSE})?"
    rf"|(?<![\w.,])(?P<first2>{_NUMBER})"
    rf"(?P<link2>\s+(?i:a|à|às|ao|aos)\s+{_OPENING_MARK})(?P<second2>{_NUMBER})"
    rf"(?P<pause2>{_PAUSE})?")


def read_number_pairs(text: str, lang: str = "pt-PT", scale: Optional[str] = None) -> str:
    """The pairs of numbers that text2spoken leaves as written, read: "de 1 a 2
    casas" -> "de um a duas casas"; "entre 1 e 2 casas" -> "entre um e duas
    casas"."""
    def read(m):
        first, link, second, pause = (m.group("first", "link", "second", "pause") if m.group("first")
                                      else m.group("first2", "link2", "second2", "pause2"))
        if pause:
            second = text2spoken_reading(second, lang, scale, gender="masculine")
        return text2spoken_reading(first, lang, scale, gender="masculine") + link + second + (pause or "")

    first_read = _PAIR.sub(read, text)
    return text2spoken_reading(first_read, lang, scale) if first_read != text else text


def read_numbers(text: str, lang: str = "pt-PT", scale: Optional[str] = None) -> str:
    """:func:`normalize_numbers` with no warning: text2spoken reads ``text``,
    the fallback rewrites above read the forms that it leaves as written, and
    text2spoken reads the digits that they leave."""
    spoken = text2spoken_reading(text, lang, scale)
    exposed = read_spoken_times(read_multiplication_signs(spoken, lang), text, lang)
    exposed = read_scientific_notation(exposed, lang)
    exposed = read_dot_numbers(exposed)
    exposed = separate_unit_symbols(exposed)
    exposed = split_number_ranges(exposed)
    exposed = expand_clock_times(exposed)
    if exposed != spoken:
        exposed = text2spoken_reading(exposed, lang, scale)
    exposed = read_number_pairs(exposed, lang, scale)
    exposed = read_unit_symbols(exposed, text, lang)
    return read_joined_numbers(exposed, lang)


def normalize_numbers(text: str, lang: str = "pt-PT", strict: bool = True,
                      scale: Optional[str] = None) -> str:
    """Rewrite the numbers, dates, times, money, measures and abbreviations of
    ``text`` as the words a speaker of ``lang`` says.

    "Nasceu a 25/12/2023." reads "Nasceu a vinte e cinco de dezembro de dois
    mil e vinte e três.". The rest of the text stays as written, so text that
    is already spelled out comes back unchanged.

    ``scale`` is ``"long"`` or ``"short"``. It overrides the scale of the
    variety: ``10^9`` is "mil milhões" in ``pt-PT`` and "um bilhão" in
    ``pt-BR``. A form that text2spoken leaves as written stays as written,
    and a form with digits gives an :class:`UnreadFormWarning`. With
    ``strict``, an error in text2spoken raises; without it, ``text`` comes
    back as written.
    """
    try:
        spoken = read_numbers(text, lang, scale)
    except Exception:
        if strict:
            raise
        return text
    warn_unread_digits(spoken, text, lang)
    return spoken


class _NumberParser:
    """Deprecated: :func:`normalize_numbers` reads numbers through text2spoken.

    The methods keep their signatures. ``pronounce_number_word`` and
    ``pronounce_scientific`` read the number through text2spoken.
    """

    # Symbols used in PT to denote ordinals (like the English 'st', 'nd', 'rd')
    ORDINAL_MALE = "º"  # e.g., 1º (primeiro)
    ORDINAL_FEMALE = "ª"  # e.g., 1ª (primeira)
    ORDINAL_TOKENS = [ORDINAL_MALE, ORDINAL_FEMALE]

    # Singular nouns that a cardinal follows as a label ("artigo 1",
    # "página 2"). In that position the cardinal stands for an ordinal and is
    # invariable: "página dois", "página duzentos e um", not "duas" or
    # "duzentas e uma". Cunha & Cintra and the Gulbenkian Gramática do
    # Português state this, as quoted by Ciberdúvidas:
    # https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/os-numerais-cardinais-usados-como-numerais-ordinais/33468
    # https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/pagina-trinta-e-um/33527
    # Plural heads are absent: with "páginas" or "folhas" the cardinal agrees
    # ("a páginas vinte e uma"), per Bechara as quoted in the second answer.
    # "casa" and "quarto" are absent because in running text they often
    # precede a number that is not their label.
    LABEL_HEADS = frozenset({
        "artigo", "número", "página", "folha", "capítulo", "alínea",
        "ponto", "parágrafo", "secção", "seção", "anexo", "figura", "tabela",
        "versículo", "apartamento", "cabine", "sala",
        "art.", "art.º", "n.º", "nº", "pág.", "cap.",
    })
    # Plural function words that can follow a label numeral ("artigo 2 das
    # disposições"). Any other plural word after the numeral is the noun the
    # numeral counts ("na sala 2 pessoas").
    PLURAL_FUNCTION_WORDS = frozenset({
        "as", "os", "das", "dos", "nas", "nos", "às", "aos", "pelas", "pelos",
    })
    # Articles, alone or contracted with "de", that set the gender of a
    # number when a word follows the number ("as 2 artistas", "os 2 artistas").
    FEMININE_DETERMINERS = frozenset({"a", "as", "da", "das"})
    MASCULINE_DETERMINERS = frozenset({"o", "os", "do", "dos"})
    # Function words that can follow a number ("os 2 da equipa", "uma das
    # casas"). They are not the counted noun, so the noun gender of their
    # spelling does not decide.
    FUNCTION_WORDS = frozenset({
        "a", "as", "o", "os", "da", "das", "do", "dos", "na", "nas", "no", "nos",
        "à", "às", "ao", "aos", "pela", "pelas", "pelo", "pelos", "de", "em",
        "e", "ou", "que", "para", "por", "com", "sem",
    })
    # Words that join the two numbers of a range ("de 1 a 2 dias", "das 2 às
    # 3 horas"); "e" joins them after "entre" ("entre 1 e 2 semanas").
    RANGE_LINKS = frozenset({"a", "à", "às", "ao", "aos"})

    UNIT_NAMES = UNIT_NAMES

    @classmethod
    def unit_name(cls, symbol: str, plural: bool, is_brazilian=False) -> str:
        """The spoken name of a unit symbol, in the singular or the plural."""
        name = cls.UNIT_NAMES[symbol][plural]
        return name.replace("quilómetro", "quilômetro") if is_brazilian else name

    @classmethod
    def unit_takes_plural(cls, value: float, is_decimal: bool, is_brazilian=False) -> bool:
        """Whether a unit name after the quantity ``value`` is plural.

        European Portuguese uses the plural after every cardinal except
        um/uma, zero included (Gramática do Português, Gulbenkian, as quoted
        by Ciberdúvidas, "Zero: com (ou sem) plural"), and after any decimal:
        "zero vírgula vinte e cinco moles", "um vírgula dois litros" (Peres &
        Móia, Áreas Críticas da Língua Portuguesa, pp. 512-517, as quoted by
        FLiP, "concordâncias com unidades (II)"). Brazilian usage keeps the
        singular up to one: "zero grau", "zero vírgula vinte e cinco mol"
        (same sources).
        """
        if is_brazilian:
            return value > 1
        return is_decimal or value != 1

    @classmethod
    def pronounce_number_word(cls, word: str,
                              prev_word: Optional[str] = None,
                              next_word: Optional[str] = None,
                              gender: Optional[str] = None,
                              as_ordinal: Optional[bool] = None,
                              is_brazilian=False,
                              scale: Optional[str] = None) -> str:
        """
        Convert a numeric token into its spelled-out Portuguese form using surrounding context.

        Parameters:
            word (str): Numeric string to convert (e.g., "1", "2.5", "10,4", "1e9").
            prev_word (Optional[str]): Word immediately before `word`, used to infer gender.
            next_word (Optional[str]): Word immediately after `word`, used to infer ordinality and gender.
            gender (Optional[str]): Explicit gender override ("masculine" or "feminine"); if omitted a heuristic is applied.
            as_ordinal (Optional[bool]): If provided, forces ordinal (`True`) or cardinal (`False`) interpretation; otherwise context is used.
            is_brazilian (bool): If True, use Brazilian Portuguese formatting rules (pt-BR); otherwise use pt-PT.
            scale (Optional[str]): "long" or "short", overriding the scale that `is_brazilian` would
                otherwise pick (long for pt-PT, short for pt-BR).

        Returns:
            Optional[str]: The spelled-out form of the number in Portuguese, or `None` if a textual form cannot be produced.
        """
        if cls.is_scientific_notation(word):
            return cls.pronounce_scientific(word, is_brazilian=is_brazilian, scale=scale)
        is_ord = cls.is_ordinal(word, next_word) if as_ordinal is None else as_ordinal
        gender = gender or cls.get_number_gender(word, prev_word, next_word)
        digits = word.replace(" º", "º").replace(" ª", "ª").strip()
        digits = digits.rstrip(cls.ORDINAL_MALE + cls.ORDINAL_FEMALE).replace(".", ",", 1)
        lang = "pt-BR" if is_brazilian else "pt-PT"
        if is_ord:
            marker = cls.ORDINAL_FEMALE if gender == "feminine" else cls.ORDINAL_MALE
            return normalize_numbers(digits + marker, lang, scale=scale)
        return text2spoken_reading(digits, lang, scale, gender)

    # Punctuation that can open or close a numeric token in running text
    # without being part of the number itself (brackets, quotes,
    # sentence-final marks, list commas). These are the sets that
    # text_normalization strips from a word's edges. Deliberately excludes
    # the ordinal markers (º/ª), which are handled separately and carry
    # meaning for gender/ordinality detection.
    LEADING_PUNCTUATION = "(“\"'¿¡«"
    TRAILING_PUNCTUATION = ".,;:!?)\"”»…"

    # A sign or a percent sign belongs to the number, not to the text around it.
    NUMBER_SIGNS = "+-−"
    NUMBER_SUFFIXES = "%‰"

    @classmethod
    def split_edges(cls, word: str) -> tuple:
        """
        Split a token into (lead, core, trail), where lead and trail are the
        punctuation and math or modifier symbols at its edges ("«7»", "[7]",
        "—7", "7;"). A sign right before a digit ("-7") stays in the core, and
        so does a percent sign at the end ("20%").
        """
        def is_mark(ch: str) -> bool:
            return unicodedata.category(ch) in ("Sm", "Sk") or unicodedata.category(ch)[0] == "P"

        i, j = 0, len(word)
        while (i < j and is_mark(word[i])
               and not (word[i] in cls.NUMBER_SIGNS and word[i + 1:i + 2].isdigit())):
            i += 1
        while j > i and is_mark(word[j - 1]) and word[j - 1] not in cls.NUMBER_SUFFIXES:
            j -= 1
        return word[:i], word[i:j], word[j:]

    @classmethod
    def split_trailing_punctuation(cls, word: str) -> tuple:
        """Split a numeric token from any trailing punctuation glued to it."""
        i = len(word)
        while i > 0 and word[i - 1] in cls.TRAILING_PUNCTUATION:
            i -= 1
        return word[:i], word[i:]

    # digit/string conversion
    @classmethod
    def to_int(cls, word: str) -> Optional[int]:
        """
        Parse a numeric token into an integer after stripping ordinal markers and surrounding punctuation/whitespace.

        Parameters:
            word (str): Input token which may contain ordinal symbols (º, ª), punctuation, or surrounding whitespace.

        Returns:
            int: The parsed integer value on success.
            None: If the token contains a decimal point (treated as a non-integer) or cannot be parsed as an integer after cleaning.
        """
        if "." in word or "," in word:
            return None  # may be a decimal
        try:
            # Remove ordinal markers and standard punctuation
            word = word.strip(cls.ORDINAL_MALE +
                              cls.ORDINAL_FEMALE +
                              string.whitespace)
            return int(word)
        except (ValueError, TypeError):
            return None

    @classmethod
    def is_int(cls, word: str) -> bool:
        """Determine whether a token represents an integer (no decimal point)."""
        return cls.to_int(word) is not None

    @classmethod
    def to_float(cls, word: str) -> Optional[float]:
        """
        Convert a numeric string (possibly containing ordinal markers, punctuation, PT/BR comma
        decimals, or surrounding whitespace) into a float.

        Parameters:
            word (str): The input string to parse; may include ordinal symbols (º, ª), punctuation,
                a comma or dot decimal separator, scientific notation, or whitespace.

        Returns:
            float: The parsed numeric value if conversion succeeds, `None` if the input cannot be converted to a float.
        """
        try:
            # Remove ordinal markers and standard punctuation
            word = word.strip(cls.ORDINAL_MALE +
                              cls.ORDINAL_FEMALE +
                              string.whitespace)
            # PT/BR write decimals with a comma; float() only accepts a dot
            word = word.replace(",", ".", 1)
            return float(word)
        except (ValueError, TypeError):
            return None

    @classmethod
    def is_float(cls, word: str) -> bool:
        """
        Determine whether a string represents any floating-point value: a plain integer, a
        decimal (comma or dot separator), or scientific notation.

        Returns:
            `true` if the string can be parsed as a float, `false` otherwise.
        """
        return cls.to_float(word) is not None

    @classmethod
    def is_decimal(cls, word: str) -> bool:
        """
        Determine whether a token is a plain decimal number -- an integer part plus a fractional
        part separated by a comma or dot -- as opposed to a bare integer or scientific notation.

        Parameters:
            word (str): Token to test.

        Returns:
            `true` if the token is a non-scientific decimal, `false` otherwise.
        """
        if cls.is_scientific_notation(word):
            return False
        return ("," in word or "." in word) and cls.is_float(word)

    @classmethod
    def is_scientific_notation(cls, word: str) -> bool:
        """
        Check whether a token uses scientific notation with a decimal mantissa and an integer exponent separated by 'e' (case-insensitive).

        Parameters:
            word (str): Token to test; the mantissa may include a decimal point, and the exponent must consist of digits.

        Returns:
            `true` if the token is scientific notation (e.g., "1.5e10"), `false` otherwise.
        """
        nums = word.lower().split("e")
        if len(nums) != 2:
            return False
        # NOTE: cant use .isdigit() in order to allow decimals and negative numbers
        return cls.is_float(nums[0]) and cls.is_int(nums[1])

    @classmethod
    def pronounce_scientific(cls, word: str, is_brazilian=False, scale: Optional[str] = None) -> str:
        """
        Convert a number in scientific notation into its Portuguese spoken form.

        Parameters:
        	word (str): A numeric string in scientific notation (e.g., "1.5e10", "2,5e3").
        	is_brazilian (bool): If True, use Brazilian Portuguese variants; otherwise use Portugal variants.
        	scale (Optional[str]): "long" or "short", overriding the scale `is_brazilian` would pick.

        Returns:
        	spoken (str): The spelled-out Portuguese phrase for the notation, combining mantissa and exponent (e.g., "um vírgula cinco vezes dez elevado a dez").

        Raises:
        	ValueError: If `word` is not valid scientific notation.
        """
        if not cls.is_scientific_notation(word):
            raise ValueError(f"word is not scientific notation: '{word}'")
        a, b = word.lower().split("e")
        a_str = cls.pronounce_number_word(a, is_brazilian=is_brazilian, scale=scale)
        b_str = cls.pronounce_number_word(b, is_brazilian=is_brazilian, scale=scale)
        return f"{a_str} vezes dez elevado a {b_str}"

    # contextual rules
    @classmethod
    def is_ordinal(cls, word: str, next_word: Optional[str] = None) -> bool:
        """Determine whether a token represents an ordinal number."""
        # Check if the symbol is a separate token or attached to the number
        if next_word in cls.ORDINAL_TOKENS:
            return True
        elif any(t in word for t in cls.ORDINAL_TOKENS):
            return True
        return False

    @classmethod
    def get_number_gender(cls, word: str,
                          prev_word: Optional[str] = None,
                          next_word: Optional[str] = None) -> str:
        """
        Determine the grammatical gender (masculine or feminine) that a numeric token should take in Portuguese.

        Parameters:
            word (str): The numeric token (may include ordinal symbols like 'º' or 'ª').
            prev_word (Optional[str]): The preceding word in context, used for heuristic cues (articles, label heads such as "artigo").
            next_word (Optional[str]): The following word in context, used to infer the gender of the counted noun.

        Returns:
            str: "feminine" if the number should agree as feminine, "masculine" otherwise.
        """
        # Rule A: Ordinal symbols explicitly dictate gender (º = masc, ª = fem)
        if (next_word and next_word == cls.ORDINAL_FEMALE) or cls.ORDINAL_FEMALE in word:
            return "feminine"
        if next_word == cls.ORDINAL_MALE or cls.ORDINAL_MALE in word:
            return "masculine"

        # Rule L: a cardinal after a singular label head ("artigo 1 da lei",
        # "página 2 da revista") is invariable, so it takes the masculine form
        # whatever word comes next. A plural content word after the numeral
        # is the noun it counts, and the rules below decide.
        if prev_word and prev_word.lower().lstrip("(«\"“") in cls.LABEL_HEADS:
            following = (next_word or "").lower()
            counts_next_word = (following.endswith("s")
                                and following not in cls.PLURAL_FUNCTION_WORDS)
            if not counts_next_word:
                return "masculine"

        noun = cls.split_trailing_punctuation(next_word or "")[0].lower()
        is_word = noun.replace("-", "").isalpha()
        consulted = is_word and noun not in cls.FUNCTION_WORDS
        listed = TugaLexicon.get_noun_gender(noun) if consulted else None

        # Rule N: the counted noun's gender in tugalex, from its exceptions
        # list or its suffix rules ("1 lei" -> "uma lei", "1 dia" -> "um
        # dia"). A single gender decides even against an article, which then
        # belongs to a later noun ("o 2 vezes campeão" -> "duas"). A noun of
        # both genders ("artista", "capital") falls through.
        if listed in ("m", "f"):
            return "feminine" if listed == "f" else "masculine"

        # Rule B: an article before the number sets its gender ("as 2
        # artistas", "os 2 artistas") -- but only when a word follows the
        # number. Without one, a bare "a"/"as" before the number is the
        # preposition "to", as in a score or range reading ("3 a 2").
        if prev_word and is_word:
            article = prev_word.lower()
            if article in cls.FEMININE_DETERMINERS:
                return "feminine"
            if article in cls.MASCULINE_DETERMINERS:
                return "masculine"

        # tugalex tries its own ending rules before it gives no gender, so the
        # next word is no noun ("300 ainda", "2 mas") and the default stands.
        if consulted and listed is None:
            return "masculine"

        # Rule C: the ending of the following word, for a function word or a
        # noun of both genders
        if noun:
            # Simple check: Words ending in 'a' are usually feminine (e.g., 'casa')
            # We strip 's' to account for plural nouns.
            if noun.strip("s").endswith("a"):
                # 1 casa (house) -> uma casa (female)
                # 1 cão (dog) -> um cão (male)
                return "feminine"

            # Rule D: Handle tricky '-e' endings
            # Words ending in -dade, -age, or -agem are consistently feminine.
            elif noun.rstrip("sm").endswith("e"):
                # words ending with "e" may be either male, female or both
                # 1 ponte (bridge) -> uma ponte  (female)
                # 1 dente (tooth) -> um dente  (male)
                # 1 cliente -> um(a) cliente
                female_endings = ["dade", "age", "agem"]
                # -dade (Feminine): Words like felicidade (happiness), cidade (city), and liberdade (freedom) are always feminine.
                # -age / -agem (Feminine): Words like viagem (trip) or coragem (courage) are feminine.
                if any(noun.endswith(f) for f in female_endings):
                    return "feminine"
        # by default numbers are male in portuguese
        return "masculine"


def __getattr__(name: str):
    if name == "NumberParser":
        warnings.warn(
            "tugaphone.number_utils.NumberParser is deprecated: use normalize_numbers, which "
            f"reads numbers through text2spoken. It will be removed in tugaphone "
            f"{NUMBER_PARSER_REMOVAL_VERSION}.", DeprecationWarning, stacklevel=2)
        return _NumberParser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
