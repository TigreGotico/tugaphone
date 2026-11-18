"""Readings where text2spoken differs from the value that a test cites.

Each mark names one class of misreading of a form that text2spoken reads, and
the text2spoken issue for it. tugaphone has no fallback for these: text2spoken
fixes them. A strict xfail turns red when text2spoken gives the cited reading,
so the mark comes off.
"""
import pytest


ISSUES = "https://github.com/TigreGotico/text2spoken/issues"


def _misreading(reason: str, issue: int):
    return pytest.mark.xfail(strict=True, reason=f"{reason}. {ISSUES}/{issue}")


LABEL = _misreading(
    "text2spoken makes a label numeral agree with its noun ('sala duas'); the Gulbenkian "
    "Gramática do Português, quoted by Ciberdúvidas 33468: 'ocorrem geralmente em forma invariável "
    "à direita do nome'", 232)
PLURAL_HEAD = _misreading(
    "text2spoken reads 'a páginas 21' as 'vinte e um'; Bechara via Ciberdúvidas 33527: "
    "'a páginas vinte e uma'", 232)
HOURS = _misreading("text2spoken reads 'são 2 da tarde' as 'dois'; the number counts the feminine 'horas'", 233)
TIMES = _misreading(
    "text2spoken reads '2 vezes 2' as 'duas vezes dois'; Priberam DLPO 'vezes': "
    "'dois vezes dois são quatro'. Ciberdúvidas 33489 quotes the Academia das Ciências de Lisboa "
    "dictionary, 'Um vezes três (1x3)', but itself recommends 'duas vezes um, dois, três, etc.'", 240)
EURO_CENTS = _misreading(
    "text2spoken reads '2,5 €' as 'dois vírgula cinco euros'; Ciberdúvidas 25561 reads an amount "
    "as euros and cents", 133)
MINUS_RANGE = _misreading("text2spoken reads '10−20' between two numbers as 'dez menos vinte', not a range", 250)
PRENOMINAL_CARDINAL = _misreading(
    "text2spoken reads 'O XXV Congresso' as 'O Vinte e cinco Congresso'; a numeral before its noun "
    "is an ordinal (Ciberdúvidas 11716)", 248)
LETTER_AS_TITLE = _misreading(
    "text2spoken reads the letter after a label noun as a title: 'a vitamina D. Boa noite' gives "
    "'Dona Boa', 'a vitamina D. Depois' gives 'Dom Depois'", 241)
SPELLED_DECIMAL = _misreading(
    "text2spoken reads 'vírgula' after a digit as the counted noun ('1 vírgula 5' gives 'uma "
    "vírgula cinco') and leaves a fraction with a leading zero ('0 vírgula 02') as written", 242)
NUMBER_SIGN = _misreading(
    "text2spoken reads the '#' of '#7#' as the word 'número' and keeps the closing '#' "
    "('número sete#'); a number between two marks reads alone ('#sete#')", 250)
DROPPED_ZERO = _misreading(
    "text2spoken drops the final zero of a decimal part: '1,80 m' gives 'um vírgula oito metros'; "
    "the text2spoken owner rules that the decimal part reads as written, 'um vírgula oitenta'", 242)
SPACE_THOUSANDS = _misreading(
    "text2spoken leaves '100 000' as written; SI brochure (Inmetro/IPQ 2021) §5.4.4: 'os números "
    "com muitos algarismos podem ser divididos em grupos de três algarismos, separados por um espaço'", 252)

