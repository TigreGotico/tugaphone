"""Numeric dates, the hour symbol, fractions, "$", "+", digits that touch
punctuation, and the warning for a form with no reading.

Each expected reading is written by hand from the source cited next to it,
and the phonemes are checked against the phonemes of that reading, so the
test does not read its answer back from the code under test.

Sources:
- Cunha & Cintra, Nova Gramática do Português Contemporâneo, p. 374, quoted
  by Ciberdúvidas 32700: cardinals for the days of the month, "salvo na
  designação do primeiro dia, em que é de regra o uso do numeral ordinal",
  and cardinals for years and hours.
- Acordo Ortográfico de 1990, Base XIX, 1.º, b): month names in lowercase.
- Ciberdúvidas 14648 and 14586: "h" is the hour symbol, "min" the minute.
- Ciberdúvidas 3267 (Guilherme de Almeida): "onze horas e trinta minutos".
- Ciberdúvidas 11493: "um meio", "um terço", "um quarto", "um décimo",
  "dois onze avos", "um dois mil avos".
- Priberam DLPO, "dólar": symbol "$", plural "dólares".
- Priberam DLPO, "mais", sense 13: "dois mais dois são quatro".
"""
import warnings

import pytest

from tugaphone import phonemize
from tugaphone.number_utils import UnreadFormWarning, normalize_numbers
from tugaphone.text_normalization import normalize_orthography


def spoken(text, lang):
    return normalize_numbers(normalize_orthography(text, lang), lang)


def assert_reads(text, words, lang):
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnreadFormWarning)
        assert spoken(text, lang) == words
        assert phonemize(text, lang) == phonemize(words, lang)


class TestNumericDates:
    @pytest.mark.parametrize("text", ["25/12/2023", "25-12-2023", "25.12.2023", "2023-12-25"])
    def test_day_month_year(self, text):
        assert_reads(text, "vinte e cinco de dezembro de dois mil e vinte e três", "pt-PT")

    def test_pt_br_spells_the_numbers_its_own_way(self):
        assert_reads("19/12/2016", "dezenove de dezembro de dois mil e dezesseis", "pt-BR")
        assert_reads("19/12/2016", "dezanove de dezembro de dois mil e dezasseis", "pt-PT")

    @pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
    def test_the_first_day_is_an_ordinal(self, lang):
        assert_reads("1/5/2024", "primeiro de maio de dois mil e vinte e quatro", lang)

    def test_a_date_in_a_sentence_keeps_its_stop(self):
        assert_reads("Nasceu a 12/03/2024.",
                     "Nasceu a doze de março de dois mil e vinte e quatro.", "pt-PT")

    def test_day_and_year_stay_masculine_before_a_feminine_noun(self):
        assert_reads("a 2/2/2022 as pessoas votaram",
                     "a dois de fevereiro de dois mil e vinte e dois as pessoas votaram", "pt-PT")

    def test_a_day_the_month_lacks_is_no_date_and_warns(self):
        with pytest.warns(UnreadFormWarning, match="31/02/2024"):
            assert spoken("31/02/2024", "pt-PT") == "31/02/2024"


class TestHourSymbol:
    def test_hours_and_minutes(self):
        assert_reads("às 19h30", "às dezanove horas e trinta minutos", "pt-PT")
        assert_reads("às 19h30", "às dezenove horas e trinta minutos", "pt-BR")

    def test_the_si_spacing(self):
        assert_reads("19 h 30 min", "dezanove horas e trinta minutos", "pt-PT")

    def test_hours_agree_with_the_feminine_hora(self):
        assert_reads("às 21h", "às vinte e uma horas", "pt-PT")
        assert_reads("à 1h01", "à uma hora e um minuto", "pt-PT")

    def test_minutes_drop_their_leading_zero(self):
        assert_reads("às 9h05", "às nove horas e cinco minutos", "pt-PT")

    def test_two_times_joined_by_a_dash(self):
        assert_reads("das 9h-17h", "das nove horas a dezassete horas", "pt-PT")

    def test_no_minutes_after_24_hours(self):
        with pytest.warns(UnreadFormWarning, match="24h30"):
            assert spoken("24h30", "pt-PT") == "24h30"

    def test_a_unit_that_starts_with_h_is_not_the_hour(self):
        with pytest.warns(UnreadFormWarning, match="5ha"):
            assert spoken("o 5ha", "pt-PT") == "o 5ha"


class TestFractions:
    @pytest.mark.parametrize("text,words", [
        ("1/2", "um meio"),
        ("1/3", "um terço"),
        ("1/4", "um quarto"),
        ("3/4", "três quartos"),
        ("1/10", "um décimo"),
        ("2/11", "dois onze avos"),
        ("1/2000", "um dois mil avos"),
    ])
    def test_reading(self, text, words):
        assert_reads(text, words, "pt-PT")

    def test_pt_br_avos(self):
        assert_reads("1/16", "um dezesseis avos", "pt-BR")
        assert_reads("1/16", "um dezasseis avos", "pt-PT")

    @pytest.mark.parametrize("text", ["3/2", "01/02", "25/12"])
    def test_a_slash_that_may_be_a_day_and_month_warns(self, text):
        with pytest.warns(UnreadFormWarning, match=text):
            assert spoken(text, "pt-PT") == text


class TestDollarAndPlus:
    def test_dollar_sign_before_the_number(self):
        assert_reads("custa $5", "custa cinco dólares", "pt-PT")
        assert_reads("custa $1", "custa um dólar", "pt-PT")

    def test_dollar_glued_after_digits_is_the_escudo_separator_and_warns(self):
        with pytest.warns(UnreadFormWarning, match=r"2\$50"):
            assert spoken("custa 2$50", "pt-PT") == "custa 2$50"

    def test_dollar_glued_after_a_number_is_not_read_and_warns(self):
        # "100$" may be escudos, so the glued sign has no clear reading.
        with pytest.warns(UnreadFormWarning, match=r"100\$"):
            assert spoken("custa 100$", "pt-PT") == "custa 100$"

    def test_plus_between_numbers(self):
        assert_reads("5+3", "cinco mais três", "pt-PT")
        assert_reads("1 + 1 são 2", "um mais um são dois", "pt-PT")


class TestNumberTouchingPunctuation:
    @pytest.mark.parametrize("mark", list("'\"#*_@/\\&[]{}<>‹›«»—–;:!?…“”‘’"))
    @pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
    def test_number_keeps_its_reading(self, mark, lang):
        for text in (f"casa {mark}7{mark} casa", f"casa {mark}7 casa", f"casa 7{mark} casa"):
            assert spoken(text, lang) == text.replace("7", "sete")
            assert phonemize(text, lang) == phonemize("casa sete casa", lang)

    def test_a_sign_before_the_digit_stays_a_sign(self):
        assert_reads("-5 graus", "menos cinco graus", "pt-PT")


class TestUnreadFormWarning:
    def test_the_warning_names_the_form_and_the_text(self):
        with pytest.warns(UnreadFormWarning) as caught:
            spoken("o vírus COVID-19 chegou", "pt-PT")
        assert [str(w.message) for w in caught] == [
            "pt-PT: no reading for 'COVID-19' in 'o vírus COVID-19 chegou'; its digits are dropped"]

    def test_the_public_path_warns_too(self):
        with pytest.warns(UnreadFormWarning, match="3D"):
            phonemize("um filme 3D", "pt-PT")

    def test_text_with_every_number_read_does_not_warn(self):
        assert_reads("tenho 2 casas", "tenho duas casas", "pt-PT")
