"""Readings where text2spoken differs from the value that a test cites.

Each mark names one difference that goes to text2spoken as an issue. A strict
xfail turns red when text2spoken gives the cited reading, so the mark comes off.
"""
import pytest

LABEL = pytest.mark.xfail(strict=True, reason=(
    "text2spoken makes a label numeral agree with its noun ('sala duas'); Cunha & Cintra via "
    "Ciberdúvidas 33468: the label numeral is invariable"))
PLURAL_HEAD = pytest.mark.xfail(strict=True, reason=(
    "text2spoken reads 'a páginas 21' as 'vinte e um'; Bechara via Ciberdúvidas 33527: "
    "'a páginas vinte e uma'"))
HOURS = pytest.mark.xfail(strict=True, reason=(
    "text2spoken reads 'são 2 da tarde' as 'dois'; the number counts the feminine 'horas'"))
TIMES = pytest.mark.xfail(strict=True, reason=(
    "text2spoken reads '2 vezes 2' as 'duas vezes dois'; Priberam DLPO 'vezes': "
    "'dois vezes dois são quatro'"))
RANGE = pytest.mark.xfail(strict=True, reason=(
    "text2spoken gives the first number of a range its default gender ('de um a três semanas'); "
    "both numbers agree with the noun after the range"))
SCIENTIFIC = pytest.mark.xfail(strict=True, reason="text2spoken leaves scientific notation ('1e6') as written")
DOT_DECIMAL = pytest.mark.xfail(strict=True, reason="text2spoken leaves a decimal with a dot ('10.4') as written")
UNITS = pytest.mark.xfail(strict=True, reason=(
    "text2spoken leaves the unit symbols 'm2' and 'L' as written; SI brochure (IPQ/Inmetro 2021): "
    "'L' is the litre"))
EURO_CENTS = pytest.mark.xfail(strict=True, reason=(
    "text2spoken reads '2,5 €' as 'dois vírgula cinco euros'; Ciberdúvidas 25561 reads an amount "
    "as euros and cents"))
SCORE = pytest.mark.xfail(strict=True, reason="text2spoken leaves the score '3-2' as written")
DASH_RANGE = pytest.mark.xfail(strict=True, reason=(
    "text2spoken leaves '10—20' as written and reads '10−20' as 'dez menos vinte'"))
CLOCK = pytest.mark.xfail(strict=True, reason=(
    "text2spoken leaves '24:00', and a clock time with no time word before it ('São 16:30.'), "
    "as written"))
ROMAN = pytest.mark.xfail(strict=True, reason=(
    "text2spoken leaves a Roman numeral as written after a name with no title ('Afonso I'), "
    "before its noun ('a II Guerra Mundial') and after 'figura'; Ciberdúvidas 14167, 11716"))
JOINED = pytest.mark.xfail(strict=True, reason=(
    "text2spoken leaves a number that one character joins to other text ('/7/', ':7:') as written"))
BR_TENTH = pytest.mark.xfail(strict=True, reason=(
    "text2spoken reads the pt-BR tenth after its noun as 'dez' (Ciberdúvidas 9067); "
    "the sentence set cites Cunha & Cintra p. 388: 'décimo'"))
