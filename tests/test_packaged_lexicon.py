"""The lexicon each lect takes: its o2i-lexicons lexicon for pt-PT and pt-BR,
and no lexicon for any other lect."""
import o2i_lexicons
import pytest
from orthography2ipa.lexicon import get_lexicon, parse_lexicon_text

from tugaphone import lattice_core, list_dialects, phonemize


def packaged(lect):
    text = o2i_lexicons.tsv_path(lect).read_text(encoding="utf-8")
    return parse_lexicon_text(text)


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
def test_a_national_lect_takes_its_packaged_lexicon(lect):
    lattice_core.engine(lect)
    assert get_lexicon(lect) == packaged(lect)


@pytest.mark.parametrize("word", ["antidumping", "indemnizar", "basebol"])
def test_a_packaged_entry_reaches_the_pt_pt_output(word):
    # The pt-PT rules get each of these words wrong, so the lexicon answers.
    assert phonemize(word, "pt-PT") == packaged("pt-PT")[word]


def test_a_packaged_entry_reaches_the_pt_br_output():
    # The pt-BR rules read this ⟨x⟩ as a fricative. The reading below is the
    # Brazilian one written by hand, so it does not come from the packaged file.
    assert phonemize("táxi", "pt-BR") == "ˈtaksi"


def test_every_pt_br_entry_reaches_the_output():
    entries = packaged("pt-BR")
    assert {word: phonemize(word, "pt-BR") for word in entries} == entries


@pytest.mark.parametrize(
    "lect", [lect for lect in list_dialects() if lect not in {"pt-PT", "pt-BR"}])
def test_every_other_lect_takes_no_lexicon(lect):
    lattice_core.engine(lect)
    assert get_lexicon(lect) == {}
