"""Percentages, unit symbols, euro amounts, decimals and multiplication.

Each expected reading comes from a cited source, not from the code under test:

* SI brochure, "Tradução luso-brasileira de 2021 do SI" (IPQ/Inmetro):
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
* Euro amounts: "cinquenta euros e trinta cêntimos" (Ciberdúvidas 25561).
* "vezes" between two numerals marks multiplication: "dois vezes dois são
  quatro" (Priberam DLPO, "vezes").
"""
import pytest

from tugaphone.number_utils import normalize_numbers
from tugaphone.text_normalization import normalize_orthography


def read(text: str, lang: str = "pt-PT") -> str:
    return normalize_numbers(normalize_orthography(text), lang)


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
        ("1,5 km", "um vírgula cinco quilómetros"),
        ("1,2 l", "um vírgula dois litros"),
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


class TestEuro:
    @pytest.mark.parametrize("text,expected", [
        ("20 €", "vinte euros"),
        ("20€", "vinte euros"),
        ("€20", "vinte euros"),
        ("€ 20", "vinte euros"),
        ("1 €", "um euro"),
        ("1.500 €", "mil e quinhentos euros"),
        ("50,30 €", "cinquenta euros e trinta cêntimos"),
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
        ("5 min", "cinco min"),
        ("O jogo é 3-2.", "O jogo é três a dois."),
    ])
    def test_unchanged(self, text, expected):
        assert read(text) == expected
