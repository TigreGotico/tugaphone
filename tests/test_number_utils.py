"""Tests for tugaphone.number_utils public API."""
import pytest
from tugaphone.number_utils import normalize_numbers, NumberParser


class TestNormalizeNumbers:
    def test_cardinal_feminine(self):
        assert normalize_numbers("vou comprar 1 casa") == "vou comprar uma casa"

    def test_cardinal_masculine(self):
        assert normalize_numbers("vou adotar 1 cão") == "vou adotar um cão"

    def test_cardinal_two_feminine(self):
        assert normalize_numbers("comprei 2 casas") == "comprei duas casas"

    def test_cardinal_pt_vs_br_nineteen(self):
        assert normalize_numbers("tem 19 anos", lang="pt-PT") == "tem dezanove anos"
        assert normalize_numbers("tem 19 anos", lang="pt-BR") == "tem dezenove anos"

    def test_strict_false_leaves_unparseable(self):
        # a bare letter-only token is left as-is with strict=False
        result = normalize_numbers("abc", strict=False)
        assert result == "abc"

    def test_no_numeric_token_unchanged(self):
        assert normalize_numbers("o gato dorme") == "o gato dorme"

    def test_ordinal_feminine_indicator(self):
        assert normalize_numbers("1ª vez") == "primeira vez"

    def test_ordinal_masculine_indicator(self):
        assert normalize_numbers("1º lugar") == "primeiro lugar"

    def test_ordinal_feminine_indicator_second(self):
        assert normalize_numbers("2ª vez") == "segunda vez"

    def test_ordinal_masculine_indicator_second(self):
        assert normalize_numbers("2º lugar") == "segundo lugar"

    def test_ordinal_larger_number(self):
        assert normalize_numbers("10ª posição") == "décima posição"

    def test_trailing_period_glued(self):
        # "custa 25." -> the period stays glued to the spelled number
        assert normalize_numbers("custa 25.") == "custa vinte e cinco."

    def test_trailing_comma_glued(self):
        # "porta" (fem.) as next_word makes "2" feminine, per the existing
        # gender heuristic -- this test is about the comma staying glued.
        assert normalize_numbers("sala 2, porta 4") == "sala duas, porta quatro"

    def test_trailing_exclamation_glued(self):
        assert normalize_numbers("ganhei 5!") == "ganhei cinco!"

    def test_full_clock_pipeline_no_space_before_final_period(self):
        # Regression for #116: "16:54." must not become "16 e 54 ."
        from tugaphone.text_normalization import normalize_orthography
        result = normalize_numbers(
            normalize_orthography("Reunião às 9:05, sala 2."), "pt-PT"
        )
        assert result == "Reunião às nove e cinco, sala dois."


class TestNumberParserPronounce:
    def test_cardinal_masculine_default(self):
        result = NumberParser.pronounce_number_word("1", gender="masculine")
        assert result == "um"

    def test_cardinal_feminine(self):
        result = NumberParser.pronounce_number_word("1", gender="feminine")
        assert result == "uma"

    def test_ordinal_masculine(self):
        result = NumberParser.pronounce_number_word("1", as_ordinal=True, gender="masculine")
        assert result == "primeiro"

    def test_ordinal_feminine(self):
        result = NumberParser.pronounce_number_word("1", as_ordinal=True, gender="feminine")
        assert result == "primeira"

    def test_nineteen_pt(self):
        assert NumberParser.pronounce_number_word("19") == "dezanove"

    def test_nineteen_br(self):
        assert NumberParser.pronounce_number_word("19", is_brazilian=True) == "dezenove"


class TestNumberParserPredicates:
    def test_is_int(self):
        assert NumberParser.is_int("42")
        assert not NumberParser.is_int("abc")
        assert not NumberParser.is_int("3.14")

    def test_is_float(self):
        assert NumberParser.is_float("3.14")
        assert NumberParser.is_float("42")
        assert not NumberParser.is_float("abc")

    def test_is_ordinal_attached(self):
        assert NumberParser.is_ordinal("1º")
        assert NumberParser.is_ordinal("1ª")

    def test_is_ordinal_separated(self):
        assert NumberParser.is_ordinal("1", "º")

    def test_not_ordinal(self):
        assert not NumberParser.is_ordinal("1")

    def test_get_number_gender_feminine(self):
        assert NumberParser.get_number_gender("1", next_word="casa") == "feminine"

    def test_get_number_gender_masculine_default(self):
        assert NumberParser.get_number_gender("2", next_word="cães") == "masculine"

    def test_to_int(self):
        assert NumberParser.to_int("42") == 42
        assert NumberParser.to_int("1º") == 1

    def test_to_float(self):
        assert NumberParser.to_float("3.14") == pytest.approx(3.14)

    def test_to_float_comma_decimal(self):
        assert NumberParser.to_float("10,4") == pytest.approx(10.4)

    def test_to_int_rejects_comma_decimal(self):
        assert NumberParser.to_int("10,4") is None

    def test_is_decimal(self):
        assert NumberParser.is_decimal("10,4")
        assert NumberParser.is_decimal("10.4")
        assert not NumberParser.is_decimal("42")
        assert not NumberParser.is_decimal("1e6")

    def test_is_scientific_notation_comma_mantissa(self):
        assert NumberParser.is_scientific_notation("2,5e3")


class TestNumberCeiling:
    """
    The ceiling is not an arbitrary round number: IEEE-754 doubles only
    represent every integer exactly up to 2**53 - 1. unicode_rbnf's
    RbnfEngine.format_number() casts its argument through float() (see
    unicode_rbnf/engine.py), so beyond that value some magnitudes are
    silently rounded to a *different* integer before being spelled out.
    Verified by execution: 9007199254741103 (2**53 + 111) is spelled as
    if it were 9007199254741104 -- a silent off-by-one corruption, not
    an error.
    """

    def test_ceiling_value(self):
        assert NumberParser.MAX_SAFE_INTEGER == 2 ** 53 - 1 == 9007199254740991

    def test_pronounce_at_ceiling_pt(self):
        result = NumberParser.pronounce_number_word(str(NumberParser.MAX_SAFE_INTEGER))
        assert result == (
            "nove mil biliões sete biliões cento e noventa e nove mil milhões "
            "duzentos e cinquenta e quatro milhões setecentos e quarenta mil "
            "novecentos e noventa e um"
        )

    def test_pronounce_at_ceiling_br(self):
        result = NumberParser.pronounce_number_word(
            str(NumberParser.MAX_SAFE_INTEGER), is_brazilian=True
        )
        assert result == (
            "nove quatrilhões sete trilhões cento e noventa e nove bilhões "
            "duzentos e cinquenta e quatro milhões setecentos e quarenta mil "
            "novecentos e noventa e um"
        )

    def test_pronounce_beyond_ceiling_raises(self):
        with pytest.raises(ValueError):
            NumberParser.pronounce_number_word(str(NumberParser.MAX_SAFE_INTEGER + 1))

    def test_normalize_beyond_ceiling_strict_raises(self):
        with pytest.raises(ValueError):
            normalize_numbers(str(NumberParser.MAX_SAFE_INTEGER + 1), strict=True)

    def test_normalize_beyond_ceiling_lenient_leaves_digits(self):
        word = str(NumberParser.MAX_SAFE_INTEGER + 1)
        assert normalize_numbers(word, strict=False) == word

    def test_normalize_at_ceiling_does_not_raise(self):
        # sanity: the ceiling itself is still fully supported
        normalize_numbers(str(NumberParser.MAX_SAFE_INTEGER), strict=True)


class TestScaleParameter:
    def test_default_long_scale_pt_pt(self):
        assert normalize_numbers("1000000000000", lang="pt-PT") == "um bilião"

    def test_default_short_scale_pt_br(self):
        assert normalize_numbers("1000000000000", lang="pt-BR") == "um trilhão"

    def test_scale_override_short_on_pt_pt(self):
        assert (
            normalize_numbers("1000000000000", lang="pt-PT", scale="short")
            == "um trilhão"
        )

    def test_scale_override_long_on_pt_br(self):
        assert (
            normalize_numbers("1000000000000", lang="pt-BR", scale="long")
            == "um bilião"
        )

    def test_pronounce_number_word_scale_kwarg(self):
        assert (
            NumberParser.pronounce_number_word(
                "1000000000000", is_brazilian=False, scale="short"
            )
            == "um trilhão"
        )


class TestScientificNotation:
    def test_simple_exponent(self):
        assert normalize_numbers("1e6") == "um vezes dez elevado a seis"

    def test_comma_decimal_mantissa(self):
        assert (
            normalize_numbers("2,5e3")
            == "dois vírgula cinco vezes dez elevado a três"
        )

    def test_dot_decimal_mantissa(self):
        assert (
            normalize_numbers("1.5e10")
            == "um vírgula cinco vezes dez elevado a dez"
        )


class TestDecimalCommaReading(object):
    def test_comma_decimal_in_sentence(self):
        assert normalize_numbers("tem 10,4 graus") == "tem dez vírgula quatro graus"

    def test_dot_decimal_still_works(self):
        assert normalize_numbers("tem 10.4 graus") == "tem dez vírgula quatro graus"
