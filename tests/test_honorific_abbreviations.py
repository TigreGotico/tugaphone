"""Honorific and plural abbreviations.

Expansions come from the Vocabulário Ortográfico da Língua Portuguesa of the
Academia das Ciências de Lisboa (abbreviation list: "Sr.ª" senhora, "V. Ex.ª"
Vossa Excelência, "S. Ex.ª" Sua Excelência, "Ex.mo"/"Ex.ma"
Excelentíssimo/Excelentíssima, "Dr.ª" Doutora, "Eng.ª" Engenheira, "prof.ª"
professora), and from two Ciberdúvidas answers that quote the vocabularies:
33650 (Carlos Rocha: "Srs.", "Sr.as", "VV. Ex.as", "V. Exas.", "Exmos.",
"Exmas.") and 15826 (D'Silvas Filho: "n.os" números, "Ex.as" Excelências).
"""
import pytest

from tugaphone.number_utils import normalize_numbers
from tugaphone.text_normalization import expand_abbreviations, normalize_orthography


@pytest.mark.parametrize("text,expected", [
    ("a Sr.ª Ana chegou", "a Senhora Ana chegou"),
    ("a Sr.ª disse que sim", "a Senhora disse que sim"),
    ("os Srs. Silva e Costa", "os Senhores Silva e Costa"),
    ("as Sr.as Costa e Lima", "as Senhoras Costa e Lima"),
    ("as Sras. Costa e Lima", "as Senhoras Costa e Lima"),
    ("V. Ex.ª sabe", "Vossa Excelência sabe"),
    ("V. Exa. sabe", "Vossa Excelência sabe"),
    ("Vv. Ex.as sabem", "Vossas Excelências sabem"),
    ("VV. Ex.as sabem", "Vossas Excelências sabem"),
    ("V. Ex.as sabem", "Vossas Excelências sabem"),
    ("V. Exas. sabem", "Vossas Excelências sabem"),
    ("S. Ex.ª o Presidente", "Sua Excelência o Presidente"),
    ("Ex.mo Senhor", "Excelentíssimo Senhor"),
    ("Ex.ma Senhora", "Excelentíssima Senhora"),
    ("Exmos. Senhores", "Excelentíssimos Senhores"),
    ("Exmas. Senhoras", "Excelentíssimas Senhoras"),
    ("a Dr.ª Marta", "a Doutora Marta"),
    ("a Eng.ª Rita", "a Engenheira Rita"),
    ("a Prof.ª Inês", "a Professora Inês"),
    ("os n.os 3 e 4", "os números 3 e 4"),
    ("os N.os 3 e 4", "os números 3 e 4"),
    # trailing punctuation other than the abbreviation's own period
    ("Obrigado, V. Ex.ª, pela visita", "Obrigado, Vossa Excelência, pela visita"),
])
def test_expansion(text, expected):
    assert expand_abbreviations(text) == expected


def test_full_pipeline_numbers_after_plural_numero():
    assert normalize_numbers(normalize_orthography("os n.os 3 e 4"), "pt-PT") == \
        "os números três e quatro"


@pytest.mark.parametrize("text,expected", [
    # rows these rules must leave as they were
    ("Sr. Silva chegou", "Senhor Silva chegou"),
    ("Dr. disse que sim", "Dr. disse que sim"),
    ("D. Afonso", "Dom Afonso"),
    ("nos dias de hoje", "nos dias de hoje"),
    ("os Srs. deputados", "os Srs. deputados"),
    ("a letra V. Depois", "a letra V. Depois"),
    ("o S. Pedro", "o S. Pedro"),
])
def test_guard_rows(text, expected):
    assert expand_abbreviations(text) == expected


def test_regnal_numeral_after_dom_still_reads():
    assert normalize_orthography("D. João V reinou") == "Dom João Quinto reinou"
