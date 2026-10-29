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
import json
from pathlib import Path

import pytest

import tugaphone
from tugaphone.number_utils import normalize_numbers
from tugaphone.text_normalization import (
    expand_abbreviations,
    expand_regnal_numerals,
    given_name_gender,
    normalize_orthography,
)

DATA = Path(tugaphone.__file__).parent / "data"


def read(text: str, lang: str = "pt-PT") -> str:
    return normalize_numbers(normalize_orthography(text, lang), lang)


class TestRulersAndPopes:
    @pytest.mark.parametrize("text,expected", [
        ("Afonso I", "Afonso Primeiro"),
        ("D. João V", "Dom João Quinto"),
        ("Henrique VIII", "Henrique Oitavo"),
        ("Luís XIV", "Luís Catorze"),
        ("Pio XII", "Pio Doze"),
        ("Bento XVI", "Bento Dezasseis"),
        ("João Paulo II", "João Paulo Segundo"),
        ("Leão X", "Leão Décimo"),
        ("Carlos V", "Carlos Quinto"),
    ])
    def test_masculine(self, text, expected):
        assert read(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("D. Maria II", "Dona Maria Segunda"),
        ("Isabel II", "Isabel Segunda"),
        ("Isabel I", "Isabel Primeira"),
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
        ("a II Guerra Mundial", "a Segunda Guerra Mundial"),
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
        "D. JOÃO V CHEGOU",
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
        assert expand_regnal_numerals(text) == text

    @pytest.mark.parametrize("text", ["220 V", "2 L"])
    def test_unit_after_number(self, text):
        assert expand_regnal_numerals(text) == text
        reading = read(text).lower()
        assert "quint" not in reading and "cinquenta" not in reading


class TestDataFiles:
    def test_given_names_record_source_and_licence(self):
        about = json.loads((DATA / "given_names.json").read_text(encoding="utf-8"))["about"]
        wikidata, ibge = about["sources"]
        assert "Wikidata" in wikidata and "CC0" in wikidata
        assert "IBGE" in ibge and "PDDL" in ibge
        assert about["build_script"] == "scripts/build_given_names.py"
        assert about["retrieved"]

    def test_given_names_genders(self):
        for name in ("Maria", "Isabel", "Beatriz", "Catarina", "Leonor", "Urraca"):
            assert given_name_gender(name) == "feminine"
        for name in ("Afonso", "Pedro", "Sebastião", "Clemente", "Pio", "Malcolm"):
            assert given_name_gender(name) == "masculine"
        for word in ("Raio", "Geração", "Sala", "Anexo", "século"):
            assert given_name_gender(word) is None

    def test_given_names_compact(self):
        data = json.loads((DATA / "given_names.json").read_text(encoding="utf-8"))
        names = data["masculine"] + data["feminine"] + data["both"]
        assert len(names) == len(set(names))
        assert all(len(name) >= 3 and name[0].isupper() for name in names)

    def test_letter_expressions_are_word_and_capital(self):
        data = json.loads((DATA / "letter_expressions.json").read_text(encoding="utf-8"))
        for phrase in data["expressions"]:
            word, letter = phrase.rsplit(" ", 1)
            assert word and len(letter) == 1 and letter.isupper()
