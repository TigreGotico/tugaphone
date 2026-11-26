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

from tugaphone.text_normalization import expand_letter_digit_codes, expand_regnal_numerals, normalize_text

# text2spoken #650 reads a pt-PT unit after a decimal under 2 in the singular
# (Ciberdúvidas 12132). Peres & Móia, Áreas Críticas, pp. 512-517 (FLiP,
# "concordâncias com unidades (II)") give the plural. The text2spoken owner rules.
DECIMAL_UNIT_DISPUTE = "text2spoken #650: singular after a pt-PT decimal under 2, against Peres & Móia"

from tests.text2spoken_gaps import PRENOMINAL_CARDINAL


def read(text: str, lang: str = "pt-PT") -> str:
    return normalize_text(text, lang)


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
        assert read(text).lower() == expected.lower()

    def test_pt_br_cardinal_spelling(self):
        assert read("o século XIX", "pt-BR") == "o século dezenove"

    def test_capitalised_part_of_work_heading(self):
        assert read("Capítulo XI").lower() == "capítulo onze"


class TestRomanBeforeNoun:
    @pytest.mark.parametrize("text,expected", [
        ("o XIX Congresso", "o Décimo Nono Congresso"),
        ("a II Guerra Mundial", "a Segunda Guerra Mundial"),
        ("na XXI edição", "na vigésima primeira edição"),
        pytest.param("O XXV Congresso decorreu em Lisboa.", "O Vigésimo Quinto Congresso decorreu em Lisboa.",
                     marks=PRENOMINAL_CARDINAL),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected


class TestRomanGuardRows:
    @pytest.mark.parametrize("text,expected", [
        ("eu vi X pessoas", "eu vi X pessoas"),
        ("a I entrada", "a I entrada"),
        ("Pizza Grande XL", "Pizza Grande XL"),
        ("um CD novo", "um CD novo"),
        ("o DL 10", "o DL dez"),
        ("o MIX", "o MIX"),
        ("Afonso I reinou", "Afonso Primeiro reinou"),
    ])
    def test_unchanged_or_as_before(self, text, expected):
        assert read(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("eu vi X pessoas", "eu vi X pessoas"),
        ("a I entrada", "a I entrada"),
        ("Pizza Grande XL", "Pizza Grande XL"),
        ("um CD novo", "um CD novo"),
        ("o DL 10", "o DL 10"),
        ("o MIX", "o MIX"),
        ("Afonso I reinou", "Afonso Primeiro reinou"),
    ])
    def test_expand_regnal_numerals_alone(self, text, expected):
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
        # a unit symbol is a unit, not a code, whatever comes before it
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


class TestCodeAfterANumber:
    """A letter-digit code after a number is still a code, so its letters are
    spelled by name; only a known unit symbol is left as written."""

    @pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
    @pytest.mark.parametrize("text,expected", [
        ("Imprimi 2 A4.", "Imprimi dois á quatro."),
        ("Imprimi 1.2 A4.", "Imprimi um ponto dois á quatro."),
        ("Lote 12.3 B2.", "Lote doze ponto três bê dois."),
        ("1.500 RTP2", "mil e quinhentos érre tê pê dois"),
        ("Ficou em -5 F1.", "Ficou em menos cinco éfe um."),
    ])
    def test_a_code_after_a_number_spells_out(self, text, expected, lang):
        assert read(text, lang) == expected

    @pytest.mark.parametrize("lang,expected", [
        pytest.param("pt-PT", "um vírgula cinco milímetros quadrados", marks=pytest.mark.xfail(strict=True, reason=DECIMAL_UNIT_DISPUTE)),
        ("pt-BR", "um vírgula cinco milímetro quadrado"),
    ])
    def test_mm2_reads_as_a_unit(self, lang, expected):
        assert read("1,5 mm2", lang) == expected

    @pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
    def test_a_unit_symbol_with_no_number_before_it_is_spelled(self, lang):
        # The unit reader reads a symbol only after digits, so elsewhere "m2" is
        # spelled rather than left with its digit unread.
        assert read("O m2 custa 2 euros.", lang) == "O éme dois custa dois euros."
