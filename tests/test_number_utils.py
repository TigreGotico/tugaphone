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
        # "sala 2" is a label numeral, so it stays "dois" whatever follows.
        assert normalize_numbers("sala 2, porta 4") == "sala dois, porta quatro"

    def test_trailing_exclamation_glued(self):
        assert normalize_numbers("ganhei 5!") == "ganhei cinco!"

    def test_full_clock_pipeline_no_space_before_final_period(self):
        # Regression for #116: "16:54." must not become "16 e 54 ."
        from tugaphone.text_normalization import normalize_orthography
        result = normalize_numbers(
            normalize_orthography("Reunião às 9:05, sala 2."), "pt-PT"
        )
        assert result == "Reunião às nove e cinco, sala dois."


class TestLabelNumeralGender:
    """A cardinal after a singular head noun is a label and is invariable.

    Source: NumberParser.LABEL_HEADS. A cardinal that quantifies a noun still
    agrees with it.
    """

    @pytest.mark.parametrize("text,expected", [
        # rows from issue #133
        ("o artigo 1 da lei", "o artigo um da lei"),
        ("o número 1 da alínea", "o número um da alínea"),
        ("o número 2 da lista", "o número dois da lista"),
        # feminine heads: "na página dois", "página duzentos e um"
        ("na página 2 da revista", "na página dois da revista"),
        ("a página 201 da obra", "a página duzentos e um da obra"),
        ("na folha 2 da ata", "na folha dois da ata"),
        ("o capítulo 2 da obra", "o capítulo dois da obra"),
        ("o artigo 22 da lei", "o artigo vinte e dois da lei"),
        ("o artigo 200 da lei", "o artigo duzentos da lei"),
        ("o artigo 2 das disposições", "o artigo dois das disposições"),
        ("o n.º 2 da lista", "o n.º dois da lista"),
        ("Artigo 1 da lei", "Artigo um da lei"),
    ])
    def test_label_numeral_is_invariable(self, text, expected):
        assert normalize_numbers(text) == expected

    @pytest.mark.parametrize("text,expected", [
        # º spells the masculine ending: "1.º" is "primeiro"
        ("o artigo 1º da lei", "o artigo primeiro da lei"),
        ("o 2º da lista", "o segundo da lista"),
    ])
    def test_masculine_ordinal_marker(self, text, expected):
        assert normalize_numbers(text) == expected

    @pytest.mark.parametrize("text,expected", [
        # a quantifying cardinal agrees with the noun it counts
        ("vou comprar 2 casas", "vou comprar duas casas"),
        ("comprei 1 casa", "comprei uma casa"),
        ("tenho 2 cães", "tenho dois cães"),
        ("na sala 2 pessoas esperam", "na sala duas pessoas esperam"),
        # with a plural head the cardinal agrees: "a páginas vinte e uma"
        ("a páginas 21 da obra", "a páginas vinte e uma da obra"),
        # ordinals inflect: "página primeira"
        ("na página 1ª do livro", "na página primeira do livro"),
        ("a 1ª página", "a primeira página"),
        ("a página 1 do livro", "a página um do livro"),
        ("são 2 da tarde", "são duas da tarde"),
        ("custa 25.", "custa vinte e cinco."),
    ])
    def test_unaffected_rows(self, text, expected):
        assert normalize_numbers(text) == expected


class TestCountedNounGender:
    """A cardinal agrees with the gender of the noun it counts.

    The expected genders do not come from tugaphone. Each noun has the same
    gender in MorphoBr (LR-POR/MorphoBr, nouns/*.dict, +F or +M) and, for
    "tarde" and "planeta", which MorphoBr lists without a gender, in the
    Gender feature of the UD Portuguese-Bosque treebank. "um"/"uma",
    "dois"/"duas" and the hundreds take the gender of the noun.
    """

    @pytest.mark.parametrize("text,expected", [
        # feminine nouns that do not end in -a
        ("1 lei", "uma lei"),
        ("2 leis", "duas leis"),
        ("um número 2 vezes maior", "um número duas vezes maior"),
        ("1 vez", "uma vez"),
        ("200 vezes", "duzentas vezes"),
        ("1 mãe", "uma mãe"),
        ("1 flor", "uma flor"),
        ("1 cor", "uma cor"),
        ("1 luz", "uma luz"),
        ("1 nação", "uma nação"),
        ("2 nações", "duas nações"),
        ("1 ponte", "uma ponte"),
        ("1 tarde", "uma tarde"),
        ("1 lei.", "uma lei."),
        # masculine nouns that end in -a
        ("1 dia", "um dia"),
        ("2 dias", "dois dias"),
        ("1 mapa", "um mapa"),
        ("1 problema", "um problema"),
        ("2 problemas", "dois problemas"),
        ("2 sistemas", "dois sistemas"),
        ("1 clima", "um clima"),
        ("1 programa", "um programa"),
        ("1 planeta", "um planeta"),
        # a masculine article decides for a noun of both genders
        ("os 2 artistas", "os dois artistas"),
        # "a" before a masculine noun is the preposition, not the article
        ("estamos a 2 dias do fim", "estamos a dois dias do fim"),
    ])
    def test_listed_gender(self, text, expected):
        assert normalize_numbers(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("2 casas", "duas casas"),
        ("1 imagem", "uma imagem"),
        ("1 hora", "uma hora"),
        ("2 cães", "dois cães"),
        ("o artigo 1 da lei", "o artigo um da lei"),
        ("a 1.ª vez", "a primeira vez"),
        ("a 1ª vez", "a primeira vez"),
        ("o 1º dia", "o primeiro dia"),
        ("as 2 artistas", "as duas artistas"),
        ("são 2 da tarde", "são duas da tarde"),
        # "vezes" between two numbers is the multiplication sign
        ("2 vezes 2 são 4", "dois vezes dois são quatro"),
    ])
    def test_unchanged_rows(self, text, expected):
        assert normalize_numbers(text) == expected

    @pytest.mark.parametrize("text,expected", [
        # the number counts "vezes"; "o" belongs to "campeão"
        ("o 2 vezes campeão", "o duas vezes campeão"),
        ("a 2 metros", "a dois metros"),
        # an article still decides for a noun of both genders
        ("os 2 artistas", "os dois artistas"),
        ("as 2 artistas", "as duas artistas"),
    ])
    def test_single_gender_noun_beats_article(self, text, expected):
        assert normalize_numbers(text) == expected

    @pytest.mark.parametrize("text,expected", [
        # both numbers of a range agree with the noun after the second
        ("de 1 a 2 dias", "de um a dois dias"),
        ("1 a 2 dias", "um a dois dias"),
        ("de 1 a 3 semanas", "de uma a três semanas"),
        ("das 2 às 3 horas", "das duas às três horas"),
        ("entre 1 e 2 semanas", "entre uma e duas semanas"),
        ("entre 1 e 2 dias", "entre um e dois dias"),
        ("de 1 a 2", "de um a dois"),
        ("3 a 2", "três a dois"),
    ])
    def test_range_agrees_with_final_noun(self, text, expected):
        assert normalize_numbers(text) == expected

    @pytest.mark.parametrize("text,expected", [
        # "cores" is the plural of "a cor"; "o core" is a computing loan
        ("2 cores", "duas cores"),
        ("as 2 cores", "as duas cores"),
    ])
    def test_loanword_sense_does_not_decide(self, text, expected):
        assert normalize_numbers(text) == expected


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

    def test_get_number_gender_preposition_a_not_article(self):
        # "3 a 2." (a score/range reading): the "a" before "2" is the
        # preposition "to", not the feminine article "a" -- there is no
        # following noun for it to introduce, so the number stays masculine.
        assert NumberParser.get_number_gender("2", prev_word="a", next_word=".") == "masculine"
        assert NumberParser.get_number_gender("2", prev_word="a", next_word=None) == "masculine"

    def test_get_number_gender_article_a_before_noun(self):
        # "a 1 casa": here "a" really is the feminine article.
        assert NumberParser.get_number_gender("1", prev_word="a", next_word="casa") == "feminine"

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


class TestLargeNumbers:
    """
    ovos-number-parser spells out arbitrarily large Python integers
    correctly in both scales; there is no ceiling. Expected strings below
    were computed against these scale tables and verified by execution
    against ovos-number-parser 0.19.13:

    pt-PT/pt-AO/pt-MZ/pt-TL long scale: milhão 10^6, mil milhões 10^9,
    bilião 10^12, mil biliões 10^15, trilião 10^18, quatrilião 10^24.

    pt-BR short scale: milhão 10^6, bilhão 10^9, trilhão 10^12,
    quatrilhão 10^15, quintilhão 10^18, sextilhão 10^21, septilhão 10^24.
    """

    def test_beyond_2_53_long_scale(self):
        assert NumberParser.pronounce_number_word("9007199254740991") == (
            "nove mil e sete biliões cento e noventa e nove mil duzentos e "
            "cinquenta e quatro milhões setecentos e quarenta mil novecentos "
            "e noventa e um"
        )

    def test_beyond_2_53_short_scale(self):
        assert NumberParser.pronounce_number_word(
            "9007199254740991", is_brazilian=True
        ) == (
            "nove quatrilhões sete trilhões cento e noventa e nove bilhões "
            "duzentos e cinquenta e quatro milhões setecentos e quarenta mil "
            "novecentos e noventa e um"
        )

    def test_10_15_long_scale(self):
        assert normalize_numbers("1000000000000000", lang="pt-PT") == "mil biliões"

    def test_10_15_short_scale(self):
        assert normalize_numbers("1000000000000000", lang="pt-BR") == "um quatrilhão"

    def test_10_18_long_scale(self):
        assert normalize_numbers("1000000000000000000", lang="pt-PT") == "um trilião"

    def test_10_18_short_scale(self):
        assert normalize_numbers("1000000000000000000", lang="pt-BR") == "um quintilhão"

    def test_10_24_long_scale(self):
        assert (
            normalize_numbers("1000000000000000000000000", lang="pt-PT")
            == "um quatrilião"
        )

    def test_10_24_short_scale(self):
        assert (
            normalize_numbers("1000000000000000000000000", lang="pt-BR")
            == "um septilhão"
        )

    def test_27_digit_long_scale(self):
        assert normalize_numbers(
            "123456789012345678901234567", lang="pt-PT"
        ) == (
            "cento e vinte e três quatriliões quatrocentos e cinquenta e "
            "seis mil setecentos e oitenta e nove triliões doze mil "
            "trezentos e quarenta e cinco biliões seiscentos e setenta e "
            "oito mil novecentos e um milhões duzentos e trinta e quatro "
            "mil quinhentos e sessenta e sete"
        )

    def test_27_digit_short_scale(self):
        assert normalize_numbers(
            "123456789012345678901234567", lang="pt-BR"
        ) == (
            "cento e vinte e três septilhões quatrocentos e cinquenta e "
            "seis sextilhões setecentos e oitenta e nove quintilhões doze "
            "quatrilhões trezentos e quarenta e cinco trilhões seiscentos e "
            "setenta e oito bilhões novecentos e um milhões duzentos e "
            "trinta e quatro mil quinhentos e sessenta e sete"
        )


class TestScaleParameter:
    def test_default_long_scale_pt_pt(self):
        assert normalize_numbers("1000000000000", lang="pt-PT") == "um bilião"

    def test_default_short_scale_pt_br(self):
        assert normalize_numbers("1000000000000", lang="pt-BR") == "um trilhão"

    def test_scale_override_short_on_pt_pt(self):
        # scale overrides only the magnitude word, keeping pt-PT spelling
        # ("trilião", not the pt-BR "trilhão")
        assert (
            normalize_numbers("1000000000000", lang="pt-PT", scale="short")
            == "um trilião"
        )

    def test_scale_override_long_on_pt_br(self):
        # scale overrides only the magnitude word, keeping pt-BR spelling
        # ("bilhão", not the pt-PT "bilião")
        assert (
            normalize_numbers("1000000000000", lang="pt-BR", scale="long")
            == "um bilhão"
        )

    def test_pronounce_number_word_scale_kwarg(self):
        assert (
            NumberParser.pronounce_number_word(
                "1000000000000", is_brazilian=False, scale="short"
            )
            == "um trilião"
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
