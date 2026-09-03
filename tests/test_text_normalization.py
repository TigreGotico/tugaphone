"""Tests for tugaphone.text_normalization: the orthographic transforms run
before number verbalisation (ranges, clock times, European separators,
abbreviations, regnal numerals, letter-spelled acronyms).

Expected strings are computed by hand from the rules, not read back from the
code under test.
"""
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.number_utils import normalize_numbers
from tugaphone.text_normalization import (
    expand_abbreviations,
    expand_acronyms,
    expand_clock_times,
    expand_regnal_numerals,
    normalize_number_separators,
    normalize_orthography,
    split_number_ranges,
)


class TestNumberRanges:
    def test_range_between_digits(self):
        assert split_number_ranges("1139-1185") == "1139 a 1185"

    def test_range_various_dash_glyphs(self):
        assert split_number_ranges("10–20") == "10 a 20"
        assert split_number_ranges("10—20") == "10 a 20"
        assert split_number_ranges("10−20") == "10 a 20"

    def test_word_hyphen_untouched(self):
        assert split_number_ranges("chamo-me") == "chamo-me"
        assert split_number_ranges("guarda-chuva") == "guarda-chuva"


class TestClockTimes:
    def test_whole_hour_16(self):
        assert expand_clock_times("16:00") == "16 horas"

    def test_whole_hour_1_singular(self):
        assert expand_clock_times("1:00") == "1 hora"

    def test_whole_hour_2(self):
        assert expand_clock_times("2:00") == "2 horas"

    def test_whole_hour_21(self):
        assert expand_clock_times("21:00") == "21 horas"

    def test_whole_hour_22(self):
        assert expand_clock_times("22:00") == "22 horas"

    def test_hh_mm(self):
        assert expand_clock_times("16:54") == "16 e 54"

    def test_out_of_range_hour_untouched(self):
        # 24 is not a valid hour of day; the colon is left for the caller.
        assert expand_clock_times("24:00") == "24:00"

    def test_note_colon_untouched(self):
        assert expand_clock_times("Nota: importante") == "Nota: importante"

    def test_full_pipeline_normalize_numbers(self):
        expanded = expand_clock_times("São 16:30.")
        assert expanded == "São 16 e 30."
        spelled = normalize_numbers(expanded, "pt-PT")
        assert spelled == "São dezasseis e trinta"


class TestNumberSeparators:
    def test_thousands_dot_dropped(self):
        assert normalize_number_separators("92.073") == "92073"

    def test_decimal_comma(self):
        assert normalize_number_separators("10,4") == "10 vírgula 4"

    def test_ordinal_mark_not_broken(self):
        assert normalize_number_separators("3.º lugar") == "3.º lugar"

    def test_full_pipeline_thousands(self):
        spelled = normalize_numbers(normalize_number_separators("92.073"), "pt-PT")
        assert spelled == "noventa e dois mil e setenta e três"

    def test_full_pipeline_decimal(self):
        spelled = normalize_numbers(normalize_number_separators("10,4"), "pt-PT")
        assert spelled == "dez vírgula quatro"


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
        # "Dr." not followed by a name-like capitalised word: left alone.
        assert expand_abbreviations("Dr. disse que sim") == "Dr. disse que sim"
        assert expand_abbreviations("ele é dr.") == "ele é dr."


class TestRegnalNumerals:
    def test_single_i_after_capitalised_name(self):
        assert expand_regnal_numerals("Afonso I reinou") == "Afonso Primeiro reinou"

    def test_multi_letter_always_converts(self):
        assert expand_regnal_numerals("João VI") == "João Sexto"
        assert expand_regnal_numerals("XX") == "Vigésimo"

    def test_single_letter_not_after_name_untouched(self):
        assert expand_regnal_numerals("eu vi X") == "eu vi X"

    def test_single_letter_after_short_word_untouched(self):
        # "a" is length 1: not a name-like word.
        assert expand_regnal_numerals("a I entrada") == "a I entrada"

    def test_trailing_punctuation_preserved(self):
        assert expand_regnal_numerals("Afonso I.") == "Afonso Primeiro."


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
