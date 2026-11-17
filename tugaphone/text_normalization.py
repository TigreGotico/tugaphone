"""Orthographic rewrites that run before text2spoken reads the text.

text2spoken (:func:`tugaphone.number_utils.normalize_numbers`) reads numbers,
dates, clock times, money, measures, ranges, Roman numerals and the
abbreviations of its own tables. These rules rewrite the written forms that it
leaves as written: the multiplication sign between two numbers, the
abbreviations of the tables below, letter-spelled acronyms and letter-digit
codes. They run in :func:`tugaphone.lattice_core._expander` ahead of
``normalize_numbers``, and the digits that they leave are read by text2spoken.

The abbreviation rules are ported from the European-Portuguese TTS front-end
tts_eu_pt (https://github.com/logus2k/tts_eu_pt), written by Antonio Cruz
and released under the Apache License 2.0. The rules from that project's
``tts_eu_pt/g2p.py`` were reimplemented here in tugaphone's own idiom.
"""
from __future__ import annotations

import re
from collections.abc import Callable

from tugalex import TugaLexicon

from tugaphone.number_utils import normalize_numbers

# ---------------------------------------------------------------------------
# A "x" or "×" between two numbers is multiplication, read "vezes": "dois
# vezes dois são quatro" (Priberam DLPO, "vezes"). Hex literals ("0x1F")
# and words ("o x da questão") have a letter on one side and are untouched.
# ---------------------------------------------------------------------------
_TIMES = re.compile(r"(?<![\w.,])(\d+(?:,\d+)?) ?[x×] ?(?=\d+(?:,\d+)?(?:[x×]\d|(?!\w)))")


def read_multiplication_signs(text: str) -> str:
    """"15x8" -> "15 vezes 8"; "2 x 2" -> "2 vezes 2"."""
    while True:
        expanded = _TIMES.sub(r"\1 vezes ", text)
        if expanded == text:
            return text
        text = expanded


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
# Reference markers stand before the number of a part of a text ("cap. 3",
# "art. 5.º", "séc. XIX"). Capitalised at the start of a sentence or a
# reference, they expand only before that number: "Cap." before a name is
# also the military rank, and "Art." a name.
_REFERENCE_MARKERS = frozenset({"cap.", "art.", "fig.", "pág.", "págs.", "séc.", "tel."})
_CAPITALISED_MARKERS = {
    key.capitalize(): _UNCONDITIONAL_ABBREVIATIONS[key].capitalize()
    for key in _REFERENCE_MARKERS
}
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
_ABBREVIATION_TRAIL = ",;:!?)\"”»"

_LEAD_PUNCT = "(“\"'¿¡«"


def _is_capitalised(word: str) -> bool:
    core = word.lstrip(_LEAD_PUNCT)
    return bool(core) and core[0].isupper()


def _abbreviation_edges(word: str) -> tuple[str, str, str]:
    """(leading punctuation, abbreviation with its own period, trailing
    punctuation) of a token: "(Cap." -> ("(", "Cap.", "")."""
    body = word.lstrip(_LEAD_PUNCT)
    core = body.rstrip(_ABBREVIATION_TRAIL)
    return word[:len(word) - len(body)], core, body[len(core):]


def _is_number(word: str) -> bool:
    """Whether *word* is a number in digits ("5", "5.º") or Roman numerals."""
    core = _split_edges(word)[1]
    return core[:1].isdigit() or _roman_value(core) is not None


def _expansion(words: list[str], i: int) -> str | None:
    """The words that the abbreviation ``words[i]`` stands for in its
    context, or None when ``words[i]`` is not read as an abbreviation there."""
    core = _abbreviation_edges(words[i])[1]
    following = _abbreviation_edges(words[i + 1])[1] if i + 1 < len(words) else None
    possessive = _POSSESSIVES.get(core)
    if possessive is not None and following in _EXCELENCIA_PLURAL:
        return possessive[_EXCELENCIA_PLURAL[following]]
    if core in _UNCONDITIONAL_ABBREVIATIONS:
        return _UNCONDITIONAL_ABBREVIATIONS[core]
    if core in _CAPITALISED_MARKERS and following is not None and _is_number(following):
        return _CAPITALISED_MARKERS[core]
    after_label = i > 0 and _abbreviation_edges(words[i - 1])[1].lower() in _LETTER_LABEL_NOUNS
    if (core in _HONORIFIC_ABBREVIATIONS and following is not None
            and _is_capitalised(words[i + 1]) and not after_label):
        if _name_gender(_split_edges(following)[1]) == "feminine":
            return "Dona"
        return _HONORIFIC_ABBREVIATIONS[core]
    return None


def _is_marker_number(words: list[str], j: int, is_foreign: Callable[[str], bool]) -> bool:
    """Whether ``words[j]`` is the number of the reference marker before it.

    A single I, V or X is also the English pronoun or a letter ("I wore a
    cap. I liked it.", "street art. V for Vendetta"), so it counts only when
    neither the word before the marker nor the two words after the numeral
    are foreign. The English evidence is the clause that the pronoun starts.
    Before the marker there is often a citation's author or year ("Gibbon
    1985, cap. I, p. 36"), which the router reads as foreign. A word before
    the marker that ends a sentence is outside the window, and punctuation
    ends the window after the numeral ("li o cap. I.")."""
    if not _is_number(words[j]):
        return False
    _, core, trail = _split_edges(words[j])
    if core not in ("I", "V", "X"):
        return True
    neighbours = words[max(j - 2, 0):j - 1]
    if neighbours and neighbours[0].rstrip("»”’\"')]").endswith((".", "!", "?", "…")):
        neighbours = []
    if not trail:
        for word in words[j + 1:j + 3]:
            neighbours.append(word)
            if _split_edges(word)[2]:
                break
    return not any(is_foreign(w) for w in neighbours)


def _is_portuguese_abbreviation(words: list[str], i: int,
                                is_foreign: Callable[[str], bool]) -> bool:
    core = _abbreviation_edges(words[i])[1]
    if core == "R." or _expansion(words, i) is None:
        return False
    if core.lower() in _REFERENCE_MARKERS:
        return i + 1 < len(words) and _is_marker_number(words, i + 1, is_foreign)
    return True


def stays_portuguese(words: list[str], i: int,
                     is_foreign: Callable[[str], bool] = lambda word: False) -> bool:
    """Whether code-switch routing must keep ``words[i]`` Portuguese because
    only Portuguese reads it in its context.

    That is an abbreviation :func:`expand_abbreviations` expands there, with
    two limits. A reference marker counts only before its number, because
    "art." and "cap." are also English words at a sentence end ("street
    art."), and its number then stays with it ("Cap. X"). "R." never counts,
    because it is also an initial ("George R. R. Martin"). ``is_foreign``
    is the router's decision for a single word; it decides whether a single
    I, V or X after a marker is its number."""
    if _is_portuguese_abbreviation(words, i, is_foreign):
        return True
    previous = _abbreviation_edges(words[i - 1])[1].lower() if i > 0 else None
    return (previous in _REFERENCE_MARKERS
            and _is_portuguese_abbreviation(words, i - 1, is_foreign))


# The abbreviations that text2spoken reads before a name ("Sr. Silva", "D.
# João V", "Av. Liberdade"). They expand after text2spoken, so that it sees
# the title, which gives the gender of a Roman numeral after the name ("A
# Dra. IV saiu"). tugaphone expands them where text2spoken leaves them as
# written ("o Sr. presidente", "falei com o Dr.").
_READ_BY_TEXT2SPOKEN = frozenset({
    "Sr.", "Sra.", "Sr.ª", "Dr.", "Dra.", "Dr.ª", "Eng.", "Prof.", "D.", "Av.",
})


def expand_abbreviations(text: str, keep: frozenset[str] = frozenset()) -> str:
    """"Sr. Silva" -> "Senhor Silva"; "D. Maria" -> "Dona Maria"; "n.º 4" ->
    "número 4"; "Av. Liberdade"
    or a bare "R." at sentence end both -> "Avenida"/"Rua" regardless of
    capitalisation, since these stand for the same word either way.
    "Cap. 3" -> "Capítulo 3"; "(art. 5.º)" -> "(artigo 5.º)". The
    abbreviations in ``keep`` stay as written."""
    words = text.split()
    out = []
    for i, w in enumerate(words):
        expansion = None if _abbreviation_edges(w)[1] in keep else _expansion(words, i)
        if expansion is None:
            out.append(w)
            continue
        lead, _, trail = _abbreviation_edges(w)
        out.append(lead + expansion + trail)
    return " ".join(out)


# ---------------------------------------------------------------------------
# A reference marker counts as one before its number in Roman numerals too
# ("cap. XIX", "séc. XX"). text2spoken reads the numeral.
# ---------------------------------------------------------------------------
_ROMAN = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _roman_value(numeral: str) -> int | None:
    if not numeral or not _ROMAN.fullmatch(numeral):
        return None
    values = [_ROMAN_VALUES[c] for c in numeral]
    return sum(-v if v < nxt else v for v, nxt in zip(values, values[1:] + [0]))

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

_TRAIL_PUNCT_WIDE = ".,;:!?)\"”»…"


def _split_edges(w: str) -> tuple[str, str, str]:
    """(leading punctuation, core, trailing punctuation) of a token."""
    i, j = 0, len(w)
    while i < j and w[i] in _LEAD_PUNCT:
        i += 1
    while j > i and w[j - 1] in _TRAIL_PUNCT_WIDE:
        j -= 1
    return w[:i], w[i:j], w[j:]


def _is_caps_word(core: str) -> bool:
    return any(c.isalpha() for c in core) and core == core.upper()


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
# before a feminine word ("o T2 na cidade" -> "tê dois"). text2spoken reads
# the digits alone, with no context, so they take its default gender, the
# masculine. Codes take one to three capitals or one or two lowercase
# letters, so longer capitalised words ("COVID19") and ordinary lowercase
# words are left alone.
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
        number = normalize_numbers(digits, lang)
        out.append(f"{lead}{_spell_letters(letters.upper())} {number}{trail}")
    return " ".join(out)


def normalize_orthography(text: str, lang: str = "pt-PT") -> str:
    """Apply the rules above that run before text2spoken, in the order that
    keeps them from interfering: the multiplication sign first (digit-only),
    then abbreviations, acronyms and letter-digit codes (word-token rules).
    The abbreviations that text2spoken reads before a name stay as written."""
    text = read_multiplication_signs(text)
    text = expand_abbreviations(text, keep=_READ_BY_TEXT2SPOKEN)
    text = expand_acronyms(text)
    text = expand_letter_digit_codes(text, lang)
    return text


def normalize_text(text: str, lang: str = "pt-PT") -> str:
    """The words a speaker of ``lang`` says for ``text``.

    :func:`normalize_orthography` runs first, then text2spoken
    (:func:`tugaphone.number_utils.normalize_numbers`). Last, the titles that
    text2spoken leaves as written expand: "Nasceu a 25/12/2023." reads "Nasceu
    a vinte e cinco de dezembro de dois mil e vinte e três.", and "falei com o
    Dr." reads "falei com o Doutor". Text that is already spelled out comes
    back unchanged.
    """
    return expand_abbreviations(normalize_numbers(normalize_orthography(text, lang), lang))
