"""Integrity checks for the POS-based HOMOGRAPHS table."""
from tugaphone.dialects import EuropeanPortuguese


def test_gosto_verb_keeps_final_vowel():
    homographs = EuropeanPortuguese().HOMOGRAPHS
    assert homographs["gosto"]["VERB"] == "ˈgɔʃtu"
    assert homographs["gosto"]["NOUN"] == "ˈgoʃtu"


def test_noun_verb_pairs_differ_only_in_vowel_quality():
    """Each noun/verb pair must have the same length: the alternation is a
    single open/closed vowel swap, never a dropped segment."""
    homographs = EuropeanPortuguese().HOMOGRAPHS
    for word, readings in homographs.items():
        if "NOUN" in readings and "VERB" in readings:
            assert len(readings["NOUN"]) == len(readings["VERB"]), word
