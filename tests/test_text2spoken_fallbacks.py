"""The fallback rewrites that read what text2spoken leaves as written.

text2spoken reads first. A fallback reads only a form that text2spoken leaves
as written, and it goes when text2spoken reads that form. The guard tests below
turn red on the day text2spoken reads a fallback form: the fallback then comes
out, with its ``TODO(text2spoken issue)`` marker.
"""
import re
import warnings
from pathlib import Path

import pytest
from text2spoken import normalize

from tugaphone import phonemize
from tugaphone import number_utils
from tugaphone.number_utils import UnreadFormWarning
from tugaphone.text_normalization import normalize_text

ROOT = Path(__file__).parent.parent
TODO = "TODO(text2spoken issue)"

# Forms that text2spoken leaves as written, with the written part it keeps.
LEFT_AS_WRITTEN = [
    ("15x8", "15x8"),
    ("2x3x4", "2x3x4"),
    ("2 x 2", " x "),
    ("1e6", "1e6"),
    ("2,5e3", "2,5e3"),
    ("casa /7/ casa", "/7/"),
    ("casa :7: casa", ":7:"),
    ("tem 10.4 graus", "10.4"),
    ("O jogo é 3-2.", "3-2"),
    ("10—20", "10—20"),
    ("São 16:30.", "16:30"),
    ("9:05", "9:05"),
    ("24:00", "24:00"),
    ("Afonso I reinou", " I "),
    ("a II Guerra Mundial", "II"),
    ("o XIX Congresso", "XIX"),
    ("figura XII", "XII"),
    ("80m2", "80m2"),
    *[(f"dez {unit}", f" {unit}") for unit in
      ["cm2", "m2", "km2", "cm3", "m3", "mg", "mL", "cl", "cL", "dl", "dL", "L"]],
]


@pytest.mark.parametrize("variety", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("text,kept", LEFT_AS_WRITTEN)
def test_text2spoken_still_leaves_the_fallback_form(text, kept, variety):
    # Red here means text2spoken reads the form: remove its fallback.
    assert kept in normalize(text, variety)


def test_text2spoken_reading_wins_over_a_fallback(monkeypatch):
    # The day text2spoken reads "10—20", its reading stands and the range
    # fallback has nothing left to rewrite.
    read = number_utils.text2spoken_reading

    def reads_the_dash(text, lang, scale=None, gender=None):
        return read(text.replace("10—20", "dez até vinte"), lang, scale, gender)

    monkeypatch.setattr(number_utils, "text2spoken_reading", reads_the_dash)
    assert normalize_text("de 10—20 metros") == "de dez até vinte metros"


def test_every_fallback_names_its_text2spoken_issue():
    # Each fallback comment and each misreading xfail names the URL of its
    # text2spoken issue. Until then they carry the marker, and this test fails.
    files = [*sorted((ROOT / "tugaphone").glob("*.py")), ROOT / "tests" / "text2spoken_gaps.py"]
    marked = [f"{path.relative_to(ROOT)}:{n}" for path in files
              for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
              if TODO in line]
    assert marked == []


# Unit names: the SI brochure (IPQ/Inmetro 2021, §5.2-5.3). European
# Portuguese puts the plural after every number but "um", decimals included;
# Brazilian usage keeps the singular up to one: "zero vírgula vinte e cinco
# mol" (Peres & Móia, Áreas Críticas da Língua Portuguesa, pp. 512-517, as
# quoted by FLiP, "concordâncias com unidades (II)").
@pytest.mark.parametrize("text,lang,expected", [
    ("80m2", "pt-PT", "oitenta metros quadrados"),
    ("2,5m2", "pt-PT", "dois vírgula cinco metros quadrados"),
    ("1 m2", "pt-PT", "um metro quadrado"),
    ("10 mg", "pt-PT", "dez miligramas"),
    ("2 cm3", "pt-PT", "dois centímetros cúbicos"),
    ("1 L", "pt-PT", "um litro"),
    ("0,5 L", "pt-PT", "zero vírgula cinco litros"),
    ("0,5 L", "pt-BR", "zero vírgula cinco litro"),
    ("2 km2", "pt-BR", "dois quilômetros quadrados"),
])
def test_unit_symbols_read(text, lang, expected):
    assert normalize_text(text, lang) == expected


@pytest.mark.parametrize("text", ["80 m2", "Uma casa de 80 m2.", "10 m3", "80m2", "10 mL", "1e6", "2x3x4"])
def test_reading_twice_changes_nothing(text):
    once = normalize_text(text)
    assert normalize_text(once) == once


# Ciberdúvidas 14648: "16:30" reads "dezasseis e trinta".
def test_a_clock_time_with_no_time_word_keeps_its_words():
    assert phonemize("São 16:30.", "pt-PT") == phonemize("São dezasseis e trinta.", "pt-PT")


@pytest.mark.parametrize("text", [
    "São 16:30.", "O jogo é 3-2.", "Tem 80m2.", "casa /7/ casa", "1e6", "às 24:00",
    "Afonso I reinou", "um filme 3D chegou", "o código XK-99 chegou", "Ligue 21 000 0000.",
])
def test_no_digit_goes_silently(text):
    # A form whose digits survive the expand step gives a warning that names
    # it; a form that loses its digits there has a spoken reading.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        spoken = normalize_text(text)
    unread = [str(w.message) for w in caught if issubclass(w.category, UnreadFormWarning)]
    for form in re.findall(r"\S*\d\S*", spoken):
        assert any(form.strip(".,;:!?") in message for message in unread), (form, unread)
    assert phonemize(text, "pt-PT").strip()


# Priberam DLPO "D.": the abbreviation of "Dom" (men) and "Dona" (women). The
# gender of the given name chooses it.
@pytest.mark.parametrize("text,expected", [
    ("A D. Raquel chegou.", "A Dona Raquel chegou."),
    ("A D. Carmen chegou.", "A Dona Carmen chegou."),
    ("A D. Inês chegou.", "A Dona Inês chegou."),
    ("O D. Garcia chegou.", "O Dom Garcia chegou."),
    ("O D. Luca chegou.", "O Dom Luca chegou."),
    ("O D. Elias chegou.", "O Dom Elias chegou."),
    ("O D. Nuno chegou.", "O Dom Nuno chegou."),
    ("D. Maria II reinou.", "Dona Maria Segunda reinou."),
    ("D. Pedro V reinou.", "Dom Pedro Quinto reinou."),
])
def test_the_title_d_follows_the_name(text, expected):
    assert normalize_text(text) == expected
