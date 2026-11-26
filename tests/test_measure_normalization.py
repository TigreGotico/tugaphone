"""Percentages, unit symbols, euro amounts, decimals and multiplication.

Each expected reading comes from a cited source, not from the code under test:

* SI brochure, "Sistema Internacional de Unidades (SI)", Inmetro/IPQ, 2021,
  ISBN 978-85-86920-28-8:
  unit symbols are invariable and are not abbreviations (§5.2, p. 23), unit
  names are common nouns (§5.3, p. 24), "%" reads "por cento" (p. 28).
* Inmetro, "Unidades Legais de Medida": "O grama pertence ao gênero
  masculino" -- "dois quilogramas", "quinhentos miligramas", "oitocentos e
  um gramas"; "quilograma; kg" is right and "quilo" wrong as the unit name.
* Plural agreement: every cardinal except um/uma takes a plural noun,
  including zero (Gramática do Português, Gulbenkian, as quoted by
  Ciberdúvidas, "Zero: com (ou sem) plural"). Decimals take the plural in
  European Portuguese: "zero vírgula vinte e cinco moles", "um vírgula dois
  litros" (Peres & Móia, Áreas Críticas da Língua Portuguesa, pp. 512-517, as
  quoted by FLiP, "concordâncias com unidades (II)"). In Brazil the singular
  is usual after zero ("zero vírgula vinte e cinco mol", same FLiP answer).
* A decimal from one to two: the CLDR 49 plural rules give pt "one: i =
  0..1" and pt_PT "one: i = 1 and v = 0", so "1,8 m" is "um vírgula oito
  metro" in Brazil and "um vírgula oito metros" in Portugal. The Senado
  Federal, Manual de Comunicação, "Números", writes "de 1,1 milhão a 1,7
  milhão de pessoas".
* Euro amounts: "cinquenta euros e trinta cêntimos" (Ciberdúvidas 25561).
* "vezes" between two numerals marks multiplication: "dois vezes dois são
  quatro" (Priberam DLPO, "vezes").
"""
import pytest
from text2spoken import normalize

# text2spoken #650 reads a pt-PT unit after a decimal under 2 in the singular
# (Ciberdúvidas 12132). Peres & Móia, Áreas Críticas, pp. 512-517 (FLiP,
# "concordâncias com unidades (II)") give the plural. The text2spoken owner rules.
DECIMAL_UNIT_DISPUTE = "text2spoken #650: singular after a pt-PT decimal under 2, against Peres & Móia"

from tugaphone.text_normalization import normalize_text



def read(text: str, lang: str = "pt-PT") -> str:
    return normalize_text(text, lang)


class TestPercent:
    @pytest.mark.parametrize("text,expected", [
        ("20%", "vinte por cento"),
        ("100%", "cem por cento"),
        ("1%", "um por cento"),
        ("0,02%", "zero vírgula zero dois por cento"),
        ("20 %", "vinte por cento"),
        ("subiu 2%.", "subiu dois por cento."),
        # "a" before the number is the preposition, never a feminine article
        ("de 1% a 2%", "de um por cento a dois por cento"),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected


class TestUnits:
    @pytest.mark.parametrize("text,expected", [
        ("7kg", "sete quilogramas"),
        ("1 kg", "um quilograma"),
        ("3,5 km", "três vírgula cinco quilómetros"),
        ("2,5 km", "dois vírgula cinco quilómetros"),
        ("1 km", "um quilómetro"),
        pytest.param("1,5 km", "um vírgula cinco quilómetros", marks=pytest.mark.xfail(strict=True, reason=DECIMAL_UNIT_DISPUTE)),
        pytest.param("1,2 l", "um vírgula dois litros", marks=pytest.mark.xfail(strict=True, reason=DECIMAL_UNIT_DISPUTE)),
        ("0 km", "zero quilómetros"),
        ("5 ml", "cinco mililitros"),
        ("10 m2", "dez metros quadrados"),
        ("10 m²", "dez metros quadrados"),
        ("1 m2", "um metro quadrado"),
        ("200 g", "duzentos gramas"),
        ("201 g", "duzentos e um gramas"),
        ("2 g", "dois gramas"),
        ("1 L", "um litro"),
        ("120 km/h", "cento e vinte quilómetros por hora"),
        ("1.500 m", "mil e quinhentos metros"),
        ("a 2 m da porta", "a dois metros da porta"),
        ("pesa 7kg.", "pesa sete quilogramas."),
        ("2,5 anos", "dois vírgula cinco anos"),
        # the decimal part reads as written, with its final zero
        pytest.param("Mede 1,80 m.", "Mede um vírgula oitenta metros.", marks=pytest.mark.xfail(strict=True, reason=DECIMAL_UNIT_DISPUTE)),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("3,5 km", "três vírgula cinco quilômetros"),
        ("1 km", "um quilômetro"),
        ("0 km", "zero quilômetro"),
        ("0,25 l", "zero vírgula vinte e cinco litro"),
        ("2 g", "dois gramas"),
    ])
    def test_reading_pt_br(self, text, expected):
        assert read(text, "pt-BR") == expected

    @pytest.mark.parametrize("text,lang,expected", [
        pytest.param("1,8 m", "pt-PT", "um vírgula oito metros", marks=pytest.mark.xfail(strict=True, reason=DECIMAL_UNIT_DISPUTE)),
        ("1,8 m", "pt-BR", "um vírgula oito metro"),
        ("1,8 L", "pt-PT", "um vírgula oito litros"),
        ("1,8 L", "pt-BR", "um vírgula oito litro"),
    ])
    def test_a_decimal_from_one_to_two(self, text, lang, expected):
        assert read(text, lang) == expected


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("text,expected", [
    ("Há 100 000 pessoas.", "Há cem mil pessoas."),
])
def test_a_space_groups_thousands(text, expected, lang):
    assert read(text, lang) == expected


class TestEuro:
    @pytest.mark.parametrize("text,expected", [
        ("20 €", "vinte euros"),
        ("20€", "vinte euros"),
        ("€20", "vinte euros"),
        ("€ 20", "vinte euros"),
        ("1 €", "um euro"),
        ("1.500 €", "mil e quinhentos euros"),
        ("50,30 €", "cinquenta euros e trinta cêntimos"),
        # one decimal is tens of cents (Ciberdúvidas 25561)
        ("2,5 €", "dois euros e cinquenta cêntimos"),
        ("1,01 €", "um euro e um cêntimo"),
        ("0,50 €", "cinquenta cêntimos"),
        ("€2,50", "dois euros e cinquenta cêntimos"),
        ("custa 20 €.", "custa vinte euros."),
        # a round million takes "de": "2,5 milhões de euros" (Ciberdúvidas 25561)
        ("€ 1.000.000", "um milhão de euros"),
        ("3.000.000 €", "três milhões de euros"),
        ("1.200 €", "mil e duzentos euros"),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected


class TestDecimals:
    @pytest.mark.parametrize("text,expected", [
        ("0,02", "zero vírgula zero dois"),
        ("3,05", "três vírgula zero cinco"),
        ("2,5", "dois vírgula cinco"),
        ("10,4", "dez vírgula quatro"),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected


class TestMultiplication:
    @pytest.mark.parametrize("text,expected", [
        ("15x8", "quinze vezes oito"),
        ("15 x 8", "quinze vezes oito"),
        ("2×2", "dois vezes dois"),
        ("2x3x4", "dois vezes três vezes quatro"),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected

    @pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
    @pytest.mark.parametrize("text", [
        "A sala tem 4 x 5 m e comprei 2 x 3 caixas.",
        "Comprei 2 x 3 caixas e a sala tem 4 x 5 m.",
    ])
    def test_each_product_reads_alone(self, text, lang):
        # text2spoken reads "4 x 5 m"; its reading stands, and "2 x 3" still
        # reads "vezes".
        room = normalize("4 x 5 m", lang)
        assert read(text, lang) == text.replace("4 x 5 m", room).replace("2 x 3", "dois vezes três")

    @pytest.mark.parametrize("text,expected", [
        # A product the author wrote in words keeps its "x"; only the product
        # in digits reads "vezes", whichever comes first.
        ("dois x três e 2 x 3", "dois x três e dois vezes três"),
        ("2 x 3 e dois x três", "dois vezes três e dois x três"),
        ("dois x três, 2 x 3 e dois x três", "dois x três, dois vezes três e dois x três"),
        ("2 x 3, dois x três e 2 x 3", "dois vezes três, dois x três e dois vezes três"),
    ])
    def test_product_in_words_keeps_its_x(self, text, expected):
        assert read(text) == expected

    @pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
    def test_products_text2spoken_reads_keep_its_reading(self, lang):
        text = "A sala tem 4 x 5 m e a outra 3 x 6 m."
        assert read(text, lang) == normalize(text, lang)


class TestGuardRows:
    """Rows that these rules must leave as they were."""

    @pytest.mark.parametrize("text,expected", [
        ("o x da questão", "o x da questão"),
        ("eu vi X pessoas", "eu vi X pessoas"),
        ("o código 0x1F", "o código 0x1F"),
        ("a letra m", "a letra m"),
        ("às 16:00", "às dezasseis horas"),
        ("1139-1185", "mil cento e trinta e nove a mil cento e oitenta e cinco"),
        ("o artigo 1 da lei", "o artigo um da lei"),
        ("comprei 2 casas", "comprei duas casas"),
        ("tem 2 cães", "tem dois cães"),
        ("5 min", "cinco minutos"),
        ("O jogo é 3-2.", "O jogo é três a dois."),
    ])
    def test_unchanged(self, text, expected):
        assert read(text) == expected
