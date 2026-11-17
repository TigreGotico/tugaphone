"""When a capital letter is a Roman numeral, and the gender of its reading.

Expected values come from the grammar, not from the engine:

* After its noun, a numeral up to ten reads as an ordinal and above ten as
  a cardinal (Cunha & Cintra, quoted by Ciberdúvidas 14284 and 14167: "D.
  João V (quinto)", "Luís XIV é «catorze»", "Bento XVI será «dezasseis»").
* An ordinal agrees in gender with the name it follows, as ordinals agree
  with their noun ("a II Guerra Mundial" is "a Segunda Guerra Mundial"), so
  a queen's numeral is feminine: "Isabel II" is "Isabel Segunda".
* "D." is the abbreviation "de dom e de dona"; "dona" is the title that
  "precede o nome próprio de senhoras" (Priberam DLPO, "D." and "dona").
* A capital letter in a fixed expression is a letter: "raio X" (Priberam
  DLPO, "raio X"), "geração X" (Priberam DLPO, "geração X"), "Malcolm X",
  "vitamina C".
* Headline text in capitals is not a regnal context: in "EU VI O FILME" the
  word "VI" is the verb "ver".
* After a number, a capital letter is a unit symbol ("220 V", "2 L").
"""
import re

import pytest

from tugaphone.text_normalization import expand_abbreviations, normalize_orthography, normalize_text

from tests.text2spoken_gaps import ROMAN

ROMAN_RUN = re.compile(r"\b[IVXLCDM]+\b")


def read(text: str, lang: str = "pt-PT") -> str:
    return normalize_text(text, lang)


class TestRulersAndPopes:
    @pytest.mark.parametrize("text,expected", [
        pytest.param("Afonso I", "Afonso Primeiro", marks=ROMAN),
        ("D. João V", "Dom João Quinto"),
        ("Henrique VIII", "Henrique Oitavo"),
        ("Luís XIV", "Luís Catorze"),
        ("Pio XII", "Pio Doze"),
        ("Bento XVI", "Bento Dezasseis"),
        ("João Paulo II", "João Paulo Segundo"),
        pytest.param("Leão X", "Leão Décimo", marks=ROMAN),
        pytest.param("Carlos V", "Carlos Quinto", marks=ROMAN),
    ])
    def test_masculine(self, text, expected):
        assert read(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("D. Maria II", "Dona Maria Segunda"),
        ("Isabel II", "Isabel Segunda"),
        pytest.param("Isabel I", "Isabel Primeira", marks=ROMAN),
        ("a rainha D. Maria I morreu no Brasil", "a rainha Dona Maria Primeira morreu no Brasil"),
    ])
    def test_feminine(self, text, expected):
        assert read(text) == expected


class TestHonorificD:
    @pytest.mark.parametrize("text,expected", [
        ("D. Maria", "Dona Maria"),
        ("D. Isabel de Aragão", "Dona Isabel de Aragão"),
        ("D. Sebastião", "Dom Sebastião"),
        ("D. Afonso Henriques", "Dom Afonso Henriques"),
    ])
    def test_gender_of_the_name(self, text, expected):
        assert expand_abbreviations(text) == expected


class TestPartsOfAWork:
    @pytest.mark.parametrize("text,expected", [
        ("o século XIX", "o século dezanove"),
        ("o século V", "o século quinto"),
        ("capítulo XLII", "capítulo quarenta e dois"),
        ("a parte V", "a parte quinta"),
        pytest.param("a II Guerra Mundial", "a Segunda Guerra Mundial", marks=ROMAN),
    ])
    def test_reading(self, text, expected):
        assert read(text) == expected

    def test_headline_after_part_of_work_noun(self):
        assert read("O SÉCULO XIX").lower() == "o século dezanove"


class TestUnchanged:
    @pytest.mark.parametrize("text", [
        # headline text in capitals
        "EU VI O FILME",
        "ELE LI O LIVRO",
        # fixed expressions
        "Raio X", "raio X", "os raios X", "Geração X", "Malcolm X", "Fator X",
        "Projeto X", "Twitter/X", "o Twitter X", "o cromossoma X",
        "vitamina C", "Vitamina D", "complexo B", "o Dia D",
        # acronyms, sizes and codes
        "o CD do álbum", "o CV dele", "o DL n.º 12/2020", "tamanho XL",
        "o MDC de 12 e 18", "a CML", "o MIX",
        # lowercase verbs and a capital that is not after a name
        "eu vi X", "Vi o filme", "a Sala V", "o Anexo I",
    ])
    def test_not_a_numeral(self, text):
        written = normalize_orthography(text)
        assert ROMAN_RUN.findall(read(text)) == ROMAN_RUN.findall(written)

    @pytest.mark.parametrize("text", ["220 V", "2 L"])
    def test_unit_after_number(self, text):
        reading = read(text).lower()
        assert "quint" not in reading and "cinquenta" not in reading


def test_a_title_and_a_name_in_capitals_read_the_numeral():
    # "D. João V (quinto)" (Ciberdúvidas 14167), written in capitals.
    assert read("D. JOÃO V CHEGOU").lower() == "dom joão quinto chegou"


class TestGivenNameGender:
    """Name genders come from tugalex. Simone and Elisabete are feminine and
    Rui masculine in Portuguese: tugalex corrects their Wikidata genders in
    scripts/given_name_overrides.csv."""

    @pytest.mark.parametrize("text,expected", [
        ("D. Maria", "Dona Maria"),
        ("D. Simone", "Dona Simone"),
        ("D. Elisabete", "Dona Elisabete"),
        ("D. Rui", "Dom Rui"),
        ("D. Afonso", "Dom Afonso"),
    ])
    def test_title_follows_the_name(self, text, expected):
        assert expand_abbreviations(text) == expected


@pytest.mark.parametrize("text,expected", [
    # "EU" in all-caps text is the pronoun; alone in mixed case, the acronym.
    ("EU VI O FILME", "EU VI O FILME"),
    ("ELA E EU", "ELA E EU"),
    ("a EU decidiu", "a e u decidiu"),
    ("A IA aprende", "A i á aprende"),
    # "IA" is the acronym in mixed case and the verb "ia" in all-caps text.
    ("a IA aprende", "a i á aprende"),
    ("ELE IA SAIR", "ELE IA SAIR"),
])
def test_acronyms_that_spell_a_word(text, expected):
    assert normalize_orthography(text) == expected
