"""Digits that touch punctuation, and the warning for a form with no reading.

The phoneme lattice has no reading for a digit and drops it, so a number that
normalize_numbers leaves as digits is lost from the phonemes. These tests hold
the number reading at the edge marks of a token, and the warning that names
any form still left with digits.
"""
import warnings

import pytest

from tugaphone import phonemize
from tugaphone.number_utils import UnreadFormWarning, normalize_numbers
from tugaphone.text_normalization import normalize_text

from tests.text2spoken_gaps import NUMBER_SIGN



def spoken(text, lang):
    return normalize_text(text, lang)


class TestNumberTouchingPunctuation:
    @pytest.mark.parametrize("mark", [
        *"'\"*_@/\\&[]{}<>‹›«»—–;:!?…“”‘’",
        pytest.param("#", marks=NUMBER_SIGN)])
    @pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
    def test_number_keeps_its_reading(self, mark, lang):
        for text in (f"casa {mark}7{mark} casa", f"casa {mark}7 casa", f"casa 7{mark} casa"):
            assert spoken(text, lang) == text.replace("7", "sete")
            assert phonemize(text, lang) == phonemize("casa sete casa", lang)

    def test_a_sign_before_the_digit_stays_a_sign(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", UnreadFormWarning)
            assert spoken("-5 graus", "pt-PT") == "menos cinco graus"
            assert phonemize("-5 graus", "pt-PT") == phonemize("menos cinco graus", "pt-PT")

    def test_a_glued_percent_stays_with_its_number(self):
        assert normalize_numbers("subiu 20%", "pt-PT") == "subiu vinte por cento"
        assert spoken("subiu 20%", "pt-PT") == "subiu vinte por cento"


class TestUnreadFormWarning:
    def test_the_warning_names_the_form_and_the_text(self):
        with pytest.warns(UnreadFormWarning) as caught:
            spoken("um filme 3D chegou", "pt-PT")
        assert [str(w.message) for w in caught] == [
            "pt-PT: no reading for '3D' in 'um filme 3D chegou'; its digits are dropped"]

    def test_the_public_path_warns_too(self):
        with pytest.warns(UnreadFormWarning, match="3D"):
            phonemize("um filme 3D", "pt-PT")

    def test_text_with_every_number_read_does_not_warn(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", UnreadFormWarning)
            assert spoken("tenho 2 casas", "pt-PT") == "tenho duas casas"
