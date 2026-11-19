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


MINUS_RANGE = _misreading("text2spoken reads '10−20' between two numbers as 'dez menos vinte', not a range", 250)
PRENOMINAL_CARDINAL = _misreading(
    "text2spoken reads 'O XXV Congresso' as 'O Vinte e cinco Congresso'; a numeral before its noun "
    "is an ordinal (Ciberdúvidas 11716)", 248)
NUMBER_SIGN = _misreading(
    "text2spoken reads the '#' of '#7#' as the word 'número' and keeps the closing '#' "
    "('número sete#'); a number between two marks reads alone ('#sete#')", 250)
SPACE_THOUSANDS = _misreading(
    "text2spoken leaves '100 000' as written; SI brochure (Inmetro/IPQ 2021) §5.4.4: 'os números "
    "com muitos algarismos podem ser divididos em grupos de três algarismos, separados por um espaço'", 252)
SCALE_PAIR = _misreading(
    "text2spoken reads 'entre 1 e 2 mil pessoas' as 'entre um e 2 mil pessoas': before a scale word it "
    "reads the first number of a pair and leaves the second as written", 283)
