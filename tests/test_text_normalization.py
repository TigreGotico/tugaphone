"""Tests for tugaphone.text_normalization: the public rewrites, and the
reading of ranges, clock times, European separators and regnal numerals
through normalize_text, where text2spoken reads first and the rewrites read
what it leaves.

Expected strings are computed by hand from the rules, not read back from the
code under test.
"""
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.text_normalization import (
    expand_abbreviations,
    expand_acronyms,
    expand_clock_times,
    expand_regnal_numerals,
    normalize_number_separators,
    normalize_text,
    separate_unit_symbols,
    split_number_ranges,
)

from tests.text2spoken_gaps import MINUS_RANGE


def read(text: str, lang: str = "pt-PT") -> str:
    return normalize_text(text, lang)


class TestPublicRewrites:
    """The rewrites that normalize_text runs on what text2spoken leaves, called
    alone. They leave the digits for a number reader."""

    def test_split_number_ranges(self):
        assert split_number_ranges("1139-1185") == "1139 a 1185"
        assert split_number_ranges("10–20") == "10 a 20"
        assert split_number_ranges("10—20") == "10 a 20"
        assert split_number_ranges("10−20") == "10 a 20"
        assert split_number_ranges("chamo-me") == "chamo-me"

    @pytest.mark.parametrize("text,expected", [
        ("16:00", "16 horas"), ("1:00", "1 hora"), ("21:00", "21 horas"),
        ("16:54", "16 e 54"), ("9:05", "9 e 5"), ("9:05, sala 2.", "9 e 5, sala 2."),
        ("24:00", "24 horas"), ("25:00", "25:00"), ("Nota: importante", "Nota: importante"),
        ("O comboio parte às 16:54.", "O comboio parte às 16 e 54."),
        ("São 12:00 horas.", "São 12 horas."), ("à 1:00 hora", "à 1 hora"),
    ])
    def test_expand_clock_times(self, text, expected):
        assert expand_clock_times(text) == expected

    def test_normalize_number_separators(self):
        assert normalize_number_separators("92.073") == "92073"
        assert normalize_number_separators("10,4") == "10 vírgula 4"
        assert normalize_number_separators("3.º lugar") == "3.º lugar"

    def test_separate_unit_symbols(self):
        assert separate_unit_symbols("Pesa 7kg e custa €20.") == "Pesa 7 kg e custa 20 €."
        assert separate_unit_symbols("Custa 2,50 €.") == "Custa 2 € e 50 cêntimos."
        assert separate_unit_symbols("15x8") == "15 vezes 8"

    @pytest.mark.parametrize("text,expected", [
        ("Afonso I reinou", "Afonso Primeiro reinou"),
        ("João VI", "João Sexto"),
        ("XX", "Vigésimo"),
        ("eu vi X", "eu vi X"),
        ("a I entrada", "a I entrada"),
        ("Afonso I.", "Afonso Primeiro."),
        ("o século XIX", "o século dezanove"),
        ("Isabel II", "Isabel Segunda"),
    ])
    def test_expand_regnal_numerals(self, text, expected):
        assert expand_regnal_numerals(text) == expected

    def test_expand_regnal_numerals_follows_the_variety(self):
        assert expand_regnal_numerals("o século XIX", "pt-BR") == "o século dezenove"


class TestNumberRanges:
    @pytest.mark.parametrize("text,expected", [
        ("1139-1185", "mil cento e trinta e nove a mil cento e oitenta e cinco"),
        ("10–20", "dez a vinte"),
        ("10—20", "dez a vinte"),
        pytest.param("10−20", "dez a vinte", marks=MINUS_RANGE),
    ])
    def test_range_between_digits(self, text, expected):
        assert read(text) == expected

    def test_word_hyphen_untouched(self):
        assert read("chamo-me") == "chamo-me"
        assert read("guarda-chuva") == "guarda-chuva"

    def test_full_pipeline_score_reading(self):
        # "3-2" is "três a dois": the "a" is the preposition "to", not the
        # feminine article, so "2" stays masculine ("dois", not "duas").
        assert read("O jogo é 3-2.") == "O jogo é três a dois."


class TestClockTimes:
    @pytest.mark.parametrize("text,expected", [
        ("às 16:00", "às dezasseis horas"),
        ("à 1:00", "à uma hora"),
        ("às 2:00", "às duas horas"),
        ("às 21:00", "às vinte e uma horas"),
        ("às 22:00", "às vinte e duas horas"),
        ("às 16:54", "às dezasseis e cinquenta e quatro"),
        ("às 9:05", "às nove e cinco"),
        ("às 9:05, sala 2.", "às nove e cinco, sala dois."),
        # Priberam, "meia-noite": "Fim da vigésima quarta hora do dia civil que
        # acaba às 24h00 (ou 00h00 ...)". "às 24:00" reads "à meia-noite" in both
        # varieties.
        ("às 24:00", "à meia-noite"),
        ("São 16:30.", "São dezasseis e trinta."),
        ("Reunião às 9:05, sala 2.", "Reunião às nove e cinco, sala dois."),
        ("O comboio parte às 16:54.", "O comboio parte às dezasseis e cinquenta e quatro."),
        ("24:00", "vinte e quatro horas"),
        ("São 12:00 horas.", "São doze horas."),
        ("à 1:00 hora", "à uma hora"),
    ])
    def test_clock_time(self, text, expected):
        assert read(text) == expected

    def test_hour_25_untouched(self):
        # 25 is not a valid hour of day.
        assert "25:00" in read("às 25:00")

    def test_note_colon_untouched(self):
        assert read("Nota: importante") == "Nota: importante"


class TestNumberSeparators:
    def test_thousands_dot(self):
        assert read("92.073") == "noventa e dois mil e setenta e três"

    def test_decimal_comma(self):
        assert read("10,4") == "dez vírgula quatro"

    def test_ordinal_mark_not_broken(self):
        assert read("3.º lugar") == "terceiro lugar"


class TestAbbreviations:
    def test_sr_before_capitalised_name(self):
        assert expand_abbreviations("Sr. Silva chegou") == "Senhor Silva chegou"

    def test_sra(self):
        assert expand_abbreviations("Sra. Costa") == "Senhora Costa"

    def test_dr(self):
        assert expand_abbreviations("Dr. Santos") == "Doutor Santos"

    def test_dra(self):
        assert expand_abbreviations("Dra. Marques") == "Doutora Marques"

    def test_eng(self):
        assert expand_abbreviations("Eng. Pereira") == "Engenheiro Pereira"

    def test_prof(self):
        assert expand_abbreviations("Prof. Oliveira") == "Professor Oliveira"

    def test_av(self):
        assert expand_abbreviations("mora na Av. Liberdade") == "mora na Avenida Liberdade"

    def test_r(self):
        assert expand_abbreviations("fica na R. Augusta") == "fica na Rua Augusta"

    def test_lx(self):
        assert expand_abbreviations("viajo para Lx. Rossio") == "viajo para Lisboa Rossio"

    def test_d_dot(self):
        assert expand_abbreviations("D. Afonso") == "Dom Afonso"

    def test_numero(self):
        assert expand_abbreviations("apartamento n.º 4") == "apartamento número 4"
        assert expand_abbreviations("apartamento nº 4") == "apartamento número 4"

    def test_not_followed_by_capital_untouched(self):
        # "Dr." stands for "Doutor" wherever it appears.
        assert expand_abbreviations("Dr. disse que sim") == "Doutor disse que sim"
        assert expand_abbreviations("ele é dr.") == "ele é dr."

    def test_unconditional_reference_markers(self):
        assert expand_abbreviations("gatos vs. cães") == "gatos versus cães"
        assert expand_abbreviations("ver pág. 12") == "ver página 12"
        assert expand_abbreviations("ver págs. 12 a 15") == "ver páginas 12 a 15"
        assert expand_abbreviations("tel. 212345678") == "telefone 212345678"
        assert expand_abbreviations("art. 5") == "artigo 5"
        assert expand_abbreviations("fig. 3") == "figura 3"
        assert expand_abbreviations("cap. 2") == "capítulo 2"
        assert expand_abbreviations("séc. XX") == "século XX"

    def test_place_abbreviations_before_lowercase_word(self):
        # Place abbreviations expand unconditionally, unlike the personal
        # honorifics: a lowercase word or end of sentence still triggers them.
        assert expand_abbreviations("A avenida R. de Lisboa fica em Lx.") ==             "A avenida Rua de Lisboa fica em Lisboa"

    def test_place_abbreviation_at_sentence_end(self):
        assert expand_abbreviations("fica em Lx.") == "fica em Lisboa"


class TestRegnalNumerals:
    def test_single_i_after_capitalised_name(self):
        assert read("Afonso I reinou").lower() == "afonso primeiro reinou"

    def test_multi_letter_after_name(self):
        assert read("João VI").lower() == "joão sexto"

    def test_single_letter_not_after_name_untouched(self):
        assert read("eu vi X") == "eu vi X"

    def test_single_letter_after_short_word_untouched(self):
        # "a" is length 1: not a name-like word.
        assert read("a I entrada") == "a I entrada"

    def test_trailing_punctuation_preserved(self):
        assert read("Afonso I.").lower() == "afonso primeiro."


class TestAcronyms:
    def test_ia(self):
        assert expand_acronyms("a IA aprende") == "a i á aprende"

    def test_llm(self):
        assert expand_acronyms("o LLM responde") == "o éle éle éme responde"

    def test_utc(self):
        assert expand_acronyms("hora UTC") == "hora u tê cê"

    def test_tts(self):
        assert expand_acronyms("motor TTS") == "motor tê tê ésse"

    def test_pt(self):
        assert expand_acronyms("PT e BR") == "pê tê e BR"

    def test_eu_uppercase(self):
        assert expand_acronyms("a EU decidiu") == "a e u decidiu"

    def test_lowercase_ia_untouched(self):
        assert expand_acronyms("ele ia embora") == "ele ia embora"

    def test_lowercase_eu_untouched(self):
        assert expand_acronyms("eu vou") == "eu vou"

    def test_general_letter_acronym(self):
        assert expand_acronyms("liguei ao GPS") == "liguei ao gê pê ésse"
        assert expand_acronyms("porta USB") == "porta u ésse bê"

    def test_punctuation_preserved(self):
        assert expand_acronyms("(IA)") == "(i á)"
        assert expand_acronyms("IA.") == "i á."


class TestFullPipelineEndToEnd:
    def test_range_and_regnal_pt_lisbon_no_empty_output(self):
        # "D. Afonso I reinou de 1139 a 1185." normalizes to "Dom Afonso
        # Primeiro reinou de mil cento e trinta e nove a mil cento e oitenta
        # e cinco." -- both range endpoints ("mil...") and the abbreviation
        # ("Dom") and regnal ordinal ("Primeiro") must have been spoken, and
        # no raw digit may reach the IPA output.
        ps = TugaPhonemizer().phonemize_sentence(
            "D. Afonso I reinou de 1139 a 1185.", "pt-PT-x-lisbon")
        assert ps
        assert not any(c.isdigit() for c in ps)
        assert "dõ" in ps          # Dom
        assert "ɐˈfõsu" in ps      # Afonso
        assert "pɾiˈmɐjɾu" in ps   # Primeiro
        assert ps.count("ˈmiɫ") == 2   # "mil" for both range endpoints

    def test_clock_time_pt_lisbon(self):
        # "São 16:30." normalizes to "São 16 e 30." -> "dezasseis e trinta";
        # without the clock-time rule the colon splits the utterance and
        # phonemize_sentence returns empty.
        ps = TugaPhonemizer().phonemize_sentence("São 16:30.", "pt-PT-x-lisbon")
        assert ps
        assert not any(c.isdigit() for c in ps)
        assert "dɨzɐˈsɐjz" in ps   # dezasseis
        assert "ˈtɾĩtɐ" in ps      # trinta

    def test_minutes_with_leading_zero_pt_lisbon_no_empty_output(self):
        # "Reunião às 9:05." must not go silent on the "05" minute.
        ps = TugaPhonemizer().phonemize_sentence("Reunião às 9:05.", "pt-PT-x-lisbon")
        assert ps
        assert not any(c.isdigit() for c in ps)
        assert "ˈnɔv" in ps    # nove
        assert "ˈsĩku" in ps   # cinco

    def test_whole_hour_24_pt_lisbon_no_empty_output(self):
        ps = TugaPhonemizer().phonemize_sentence("24:00.", "pt-PT-x-lisbon")
        assert ps
        assert not any(c.isdigit() for c in ps)
        assert "ˈvĩt" in ps    # vinte
        assert "ˈkwatɾu" in ps  # quatro
        assert "ˈɔɾɐʃ" in ps    # horas: Infopédia hora [ˈɔrɐ], open o
