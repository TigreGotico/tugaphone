"""The lexicon each engine holds: its o2i-lexicons lexicon for pt-PT and pt-BR,
an empty one for any other lect, and nothing outside tugaphone's engines."""
import subprocess
import sys
import textwrap

import o2i_lexicons
import pytest
from orthography2ipa import G2P, clear_lexicons, register_lexicon
from orthography2ipa.lexicon import parse_lexicon_text

from tugaphone import lattice_core, list_dialects, phonemize


def packaged(lect):
    text = o2i_lexicons.tsv_path(lect).read_text(encoding="utf-8")
    return parse_lexicon_text(text)


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
def test_a_national_lect_holds_its_packaged_lexicon(lect):
    assert lattice_core.engine(lect).pipeline.lexicon == packaged(lect)


@pytest.mark.parametrize("word", ["antidumping", "indemnizar", "basebol"])
def test_a_packaged_entry_reaches_the_pt_pt_output(word):
    # The pt-PT rules get each of these words wrong, so the lexicon answers.
    assert phonemize(word, "pt-PT") == packaged("pt-PT")[word]


def test_a_packaged_entry_reaches_the_pt_br_output():
    # The pt-BR rules read this ⟨x⟩ as a fricative. The reading below is the
    # Brazilian one written by hand, so it does not come from the packaged file.
    assert phonemize("táxi", "pt-BR") == "ˈtaksi"


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
def test_every_entry_reaches_the_output(lect):
    entries = packaged(lect)
    assert {word: phonemize(word, lect) for word in entries} == entries


@pytest.mark.parametrize(
    "lect", [lect for lect in list_dialects() if lect not in {"pt-PT", "pt-BR"}])
def test_every_other_lect_holds_an_empty_lexicon(lect):
    assert lattice_core.engine(lect).pipeline.lexicon == {}


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_a_process_wide_lexicon_does_not_reach_a_lect_without_one(tmp_path):
    source = tmp_path / "pt-AO.tsv"
    source.write_text("gato\tˈzzz\n", encoding="utf-8")
    register_lexicon("pt-AO", str(source))
    try:
        assert G2P("pt-AO").transcribe_word("gato") == "ˈzzz"
        lattice_core.clear_caches()
        assert phonemize("gato", "pt-AO") != "ˈzzz"
    finally:
        clear_lexicons()
        lattice_core.clear_caches()


def test_a_plain_engine_stays_on_the_rules_in_a_fresh_process():
    # A fresh process, because pytest shares its process with every other test.
    # A plain G2P reads each word the same before and after tugaphone runs.
    script = textwrap.dedent("""
        from orthography2ipa import G2P
        before = G2P("pt-BR").transcribe_word("táxi"), G2P("pt-PT").transcribe_word("basebol")
        from tugaphone import phonemize
        tugaphone = phonemize("táxi", "pt-BR"), phonemize("basebol", "pt-PT")
        after = G2P("pt-BR").transcribe_word("táxi"), G2P("pt-PT").transcribe_word("basebol")
        print(*before, *tugaphone, *after)
    """)
    run = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True,
                         check=True)
    rules_br, rules_pt, lexicon_br, lexicon_pt, after_br, after_pt = run.stdout.split()
    assert (after_br, after_pt) == (rules_br, rules_pt)
    assert (lexicon_br, lexicon_pt) == (packaged("pt-BR")["táxi"], packaged("pt-PT")["basebol"])
    assert (rules_br, rules_pt) != (lexicon_br, lexicon_pt)
