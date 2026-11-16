"""Roman numerals after centuries, rulers, popes and parts of a work, and
letter-digit codes ("T2", "A3", "RTP2", "mp3").

Roman numerals. "Como é sabido, na fala, até 10 (Celso Cunha e Lindley
Cintra) inclusive, usam-se os ordinais e depois os cardinais, sempre que o
numeral vier depois do substantivo" (Ciberdúvidas 14284, on kings, popes and
centuries). Examples: "Bento XVI será «dezasseis», tal como o único papa
português, João XXI, é «vinte e um», tal como Luís XIV é «catorze», tal como
o século XV é o século «quinze»"; "João Paulo II (segundo), Paulo VI (sexto),
Clemente X (décimo), D. Pedro IV (quarto), D. João V (quinto)" (Ciberdúvidas
14167). The Nova Gramática do Português Contemporâneo applies the rule "a
todas as partes em que se divide uma obra", and "Se o numeral antecede o
substantivo, é usual continuar a usar-se o ordinal, mesmo depois de dez"
(Ciberdúvidas 11716).

Case does not change the transcription. The numeral takes the case of the
name it belongs to ("Pio Doze", "a Segunda Guerra Mundial", the idiom of the
existing table) and is lowercase after a common noun ("o século dezanove"),
as numerals are in running text.

Letter-digit codes are read as their letter names, then the number as a
cardinal label, which is invariable: "sente-se a omissão da palavra número"
(Cunha & Cintra, quoted by Ciberdúvidas 33468).
"""
import pytest

from tugaphone.number_utils import normalize_numbers
from tugaphone.text_normalization import (
    expand_letter_digit_codes,
    expand_regnal_numerals,
    normalize_orthography,
)


def read(text: str, lang: str = "pt-PT") -> str:
    return normalize_numbers(normalize_orthography(text, lang), lang)


class TestRomanAfterNoun:
    @pytest.mark.parametrize("text,expected", [
        ("o século XIX", "o século dezanove"),
        ("o século XV", "o século quinze"),
        ("o século V", "o século quinto"),
        ("o século XXI", "o século vinte e um"),
        ("no século XXI da nossa era", "no século vinte e um da nossa era"),
        ("o séc. XX", "o século vinte"),
        ("o capítulo IV", "o capítulo quarto"),
        ("o capítulo XLII", "o capítulo quarenta e dois"),
        ("o cap. XI", "o capítulo onze"),
        ("Pio XII", "Pio Doze"),
        ("Bento XVI", "Bento Dezasseis"),
        ("João XXI", "João Vinte e Um"),
        ("Luís XIV", "Luís Catorze"),
        ("João XXII era francês", "João Vinte e Dois era francês"),
        ("João Paulo II", "João Paulo Segundo"),
        ("Paulo VI", "Paulo Sexto"),
        ("Clemente X", "Clemente Décimo"),
        ("D. Pedro IV", "Dom Pedro Quarto"),
        ("D. João V reinou", "Dom João Quinto reinou"),
        ("D. Afonso I.", "Dom Afonso Primeiro."),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected

    def test_pt_br_cardinal_spelling(self):
        assert read("o século XIX", "pt-BR") == "o século dezenove"

    def test_capitalised_part_of_work_heading(self):
        assert read("Capítulo XI") == "Capítulo Onze"


class TestRomanBeforeNoun:
    @pytest.mark.parametrize("text,expected", [
        ("o XIX Congresso", "o Décimo Nono Congresso"),
        ("a II Guerra Mundial", "a Segunda Guerra Mundial"),
        ("na XXI edição", "na vigésima primeira edição"),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected


class TestRomanGuardRows:
    @pytest.mark.parametrize("text,expected", [
        ("eu vi X pessoas", "eu vi X pessoas"),
        ("a I entrada", "a I entrada"),
        ("Pizza Grande XL", "Pizza Grande XL"),
        ("um CD novo", "um CD novo"),
        ("o DL 10", "o DL 10"),
        ("o MIX", "o MIX"),
        ("Afonso I reinou", "Afonso Primeiro reinou"),
    ])
    def test_unchanged_or_as_before(self, text, expected):
        assert expand_regnal_numerals(text) == expected


class TestLetterDigitCodes:
    @pytest.mark.parametrize("text,expected", [
        ("um T0", "um tê zero"),
        ("um T2", "um tê dois"),
        ("o T2 na cidade", "o tê dois na cidade"),
        ("a A3", "a á três"),
        ("a RTP2", "a érre tê pê dois"),
        ("um mp3", "um éme pê três"),
        ("o G20", "o gê vinte"),
        ("o CO2", "o cê ó dois"),
        ("(T2)", "(tê dois)"),
        ("o T1.", "o tê um."),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected

    def test_pt_br_cardinal_spelling(self):
        assert read("a BR16", "pt-BR") == "a bê érre dezesseis"


class TestLetterDigitGuardRows:
    @pytest.mark.parametrize("text,expected", [
        # after a number the letters are a unit symbol, not a code
        ("10 m2", "10 m2"),
        ("5 km2", "5 km2"),
        ("4G", "4G"),
        ("B2B", "B2B"),
        ("COVID19", "COVID19"),
        ("1º", "1º"),
        ("abc123", "abc123"),
    ])
    def test_unchanged(self, text, expected):
        assert expand_letter_digit_codes(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("o artigo 1 da lei", "o artigo um da lei"),
        ("às 16:00", "às dezasseis horas"),
        ("1139-1185", "mil cento e trinta e nove a mil cento e oitenta e cinco"),
        ("a IA aprende", "a i á aprende"),
    ])
    def test_pipeline_unchanged(self, text, expected):
        assert read(text) == expected
