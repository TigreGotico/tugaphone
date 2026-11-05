"""The lexicon each lect takes: the o2i-lexicons pt-PT lexicon for pt-PT, and
no lexicon for any other lect."""
import o2i_lexicons
import pytest
from orthography2ipa.lexicon import get_lexicon, parse_lexicon_text

from tugaphone import lattice_core, list_dialects, phonemize


def packaged_pt_pt():
    text = o2i_lexicons.tsv_path("pt-PT").read_text(encoding="utf-8")
    return parse_lexicon_text(text)


def test_pt_pt_takes_the_packaged_lexicon():
    lattice_core.engine("pt-PT")
    assert get_lexicon("pt-PT") == packaged_pt_pt()


@pytest.mark.parametrize("word", ["antidumping", "indemnizar", "basebol"])
def test_a_packaged_entry_reaches_the_pt_pt_output(word):
    # The pt-PT rules get each of these words wrong, so the lexicon answers.
    assert phonemize(word, "pt-PT") == packaged_pt_pt()[word]


@pytest.mark.parametrize("lect", [lect for lect in list_dialects() if lect != "pt-PT"])
def test_every_other_lect_takes_no_lexicon(lect):
    lattice_core.engine(lect)
    assert get_lexicon(lect) == {}
