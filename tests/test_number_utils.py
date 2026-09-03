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
