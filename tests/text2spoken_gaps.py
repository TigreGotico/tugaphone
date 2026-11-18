"""Readings where text2spoken differs from the value that a test cites.

Each mark names one class of misreading of a form that text2spoken reads, and
the text2spoken issue for it. tugaphone has no fallback for these: text2spoken
fixes them. A strict xfail turns red when text2spoken gives the cited reading,
so the mark comes off.
"""
import pytest


def _misreading(reason: str):
    return pytest.mark.xfail(strict=True, reason=f"{reason}. TODO(text2spoken issue)")


LABEL = _misreading(
    "text2spoken makes a label numeral agree with its noun ('sala duas'); the Gulbenkian "
    "Gramática do Português, quoted by Ciberdúvidas 33468: 'ocorrem geralmente em forma invariável "
    "à direita do nome'")
PLURAL_HEAD = _misreading(
    "text2spoken reads 'a páginas 21' as 'vinte e um'; Bechara via Ciberdúvidas 33527: "
    "'a páginas vinte e uma'")
HOURS = _misreading("text2spoken reads 'são 2 da tarde' as 'dois'; the number counts the feminine 'horas'")
TIMES = _misreading(
    "text2spoken reads '2 vezes 2' as 'duas vezes dois'; Priberam DLPO 'vezes': "
    "'dois vezes dois são quatro'")
RANGE = _misreading(
    "text2spoken gives the first number of a range its default gender ('de um a três semanas'); "
    "both numbers agree with the noun after the range")
EURO_CENTS = _misreading(
    "text2spoken reads '2,5 €' as 'dois vírgula cinco euros'; Ciberdúvidas 25561 reads an amount "
    "as euros and cents")
MINUS_RANGE = _misreading("text2spoken reads '10−20' between two numbers as 'dez menos vinte', not a range")
PRENOMINAL_CARDINAL = _misreading(
    "text2spoken reads 'O XXV Congresso' as 'O Vinte e cinco Congresso'; a numeral before its noun "
    "is an ordinal (Ciberdúvidas 11716)")
LETTER_AS_TITLE = _misreading(
    "text2spoken reads the letter after a label noun as a title: 'a vitamina D. Boa noite' gives "
    "'Dona Boa', 'a vitamina D. Depois' gives 'Dom Depois'")
SPELLED_DECIMAL = _misreading(
    "text2spoken reads 'vírgula' after a digit as the counted noun ('1 vírgula 5' gives 'uma "
    "vírgula cinco') and leaves a fraction with a leading zero ('0 vírgula 02') as written")
NUMBER_SIGN = _misreading(
    "text2spoken reads the '#' of '#7#' as the word 'número' and keeps the closing '#' "
    "('número sete#'); a number between two marks reads alone ('#sete#')")
DROPPED_ZERO = _misreading(
    "text2spoken drops the final zero of a decimal part: '1,80 m' gives 'um vírgula oito metros'; "
    "the text2spoken owner rules that the decimal part reads as written, 'um vírgula oitenta'")
SPACE_THOUSANDS = _misreading(
    "text2spoken leaves '100 000' as written; SI brochure (IPQ/Inmetro 2021) §5.4.4: 'os números "
    "com muitos algarismos podem ser divididos em grupos de três algarismos, separados por um espaço'")
# Pending a ruling of the text2spoken owner on the Brazilian singular below 2.
# Drop this mark and its rows if the source backs the singular.
BR_DECIMAL_SINGULAR = _misreading(
    "pending a ruling: pt-BR '1,8 m' gives the singular 'um vírgula oito metro'; the FLiP answer "
    "quoted in test_measure_normalization keeps the Brazilian singular up to one, and 1,8 is above one")

# Not a text2spoken defect: the sources disagree, and the reading waits for a ruling.
BR_TENTH = pytest.mark.xfail(strict=True, reason=(
    "source conflict, open for a ruling: text2spoken reads the pt-BR tenth after its noun as 'dez' "
    "(Ciberdúvidas 9067); the sentence set cites Cunha & Cintra p. 388: 'décimo'"))
