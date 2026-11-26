"""The lexicon each engine holds: its o2i-lexicons exceptions and patches for
pt-PT and pt-BR, an empty one for any other lect, and nothing outside
tugaphone's engines."""
import subprocess
import sys
import textwrap

import o2i_lexicons
import pytest
from orthography2ipa import G2P, clear_lexicons, register_lexicon
from orthography2ipa import parse_lexicon_text

from tugaphone import lattice_core, list_dialects, phonemize


def read(path):
    return parse_lexicon_text(path.read_text(encoding="utf-8"))


def packaged(lect):
    """The exceptions and the patches of *lect*; an exception wins."""
    return {**read(o2i_lexicons.patch_tsv_path(lect)), **read(o2i_lexicons.tsv_path(lect))}


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
def test_a_national_lect_holds_its_packaged_lexicon(lect):
    assert lattice_core.engine(lect).pipeline.lexicon == packaged(lect)


@pytest.mark.parametrize("word", ["antidumping", "indemnizar", "basebol"])
def test_a_packaged_entry_reaches_the_pt_pt_output(word):
    # The pt-PT rules get each of these words wrong, so the lexicon answers.
    assert phonemize(word, "pt-PT") == packaged("pt-PT")[word]


@pytest.mark.parametrize("lect, kind, word", [
    ("pt-PT", "exception", "táxi"),      # ⟨x⟩ as [ks]: the spelling cannot show it
    ("pt-PT", "patch", "indemnizar"),    # a rule could reach it
    ("pt-BR", "exception", "foto"),      # the height of a stressed mid vowel
    ("pt-BR", "patch", "joga"),          # the stem vowel of a rhizotonic verb form
])
def test_both_kinds_of_entry_reach_the_output(lect, kind, word):
    path = o2i_lexicons.tsv_path(lect) if kind == "exception" else o2i_lexicons.patch_tsv_path(lect)
    entry = read(path)[word]
    assert phonemize(word, lect) == entry
    assert G2P(lect).transcribe_word(word) != entry


def test_a_packaged_entry_reaches_the_pt_br_output():
    # The pt-BR rules read this ⟨x⟩ as a fricative. The reading below is the
    # Brazilian one written by hand, so it does not come from the packaged file.
    assert phonemize("táxi", "pt-BR") == "ˈtaksi"


# VOP lemma 56027: "fractura - nome feminino ... Brasil ... variante AO de : fratura". The
# pt-PT lexicon keys fractura, fracturamento and fracturar are pre-AO1990 spellings, so the
# spelling step reads them as fratura, fraturamento and fraturar before the lexicon.
PRE_AO1990_KEYS = {"pt-PT": {"fractura": "fratura", "fracturamento": "fraturamento",
                             "fracturar": "fraturar"}, "pt-BR": {}}


# bifonia marks these words with a trema before the lexicon step, so the marked
# form misses its lexicon key and the rules answer instead.
MARKED_BEFORE_LEXICON = {"pt-PT": {"equitativo"}, "pt-BR": set()}


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
def test_every_entry_reaches_the_output(lect):
    entries = {word: ipa for word, ipa in packaged(lect).items()
               if word not in PRE_AO1990_KEYS[lect].keys() | MARKED_BEFORE_LEXICON[lect]}
    assert {word: phonemize(word, lect) for word in entries} == entries


# Not strict: orthography2ipa #2644 fixes it, and its consumer check runs this file.
@pytest.mark.xfail(strict=False, reason="the bifonia trema hides the lexicon key "
                   "(orthography2ipa #2643)")
def test_a_marked_word_reaches_its_lexicon_entry():
    assert phonemize("equitativo", "pt-PT") == packaged("pt-PT")["equitativo"]


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
def test_a_pre_ao1990_key_reads_as_its_ao1990_form(lect):
    rewritten = {word: lattice_core.normalize_spelling(word, lect) for word in packaged(lect)}
    assert {word: new for word, new in rewritten.items() if new != word} == PRE_AO1990_KEYS[lect]
    for old, new in PRE_AO1990_KEYS[lect].items():
        assert phonemize(old, lect) == phonemize(new, lect)


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


# AO1990 Nota Explicativa 4.2 b): a mute c or p does not keep the vowel before it open
# (corar, padeiro stay open with no consonant; accionar, actual reduce beside it), so the
# vowel is lexical and comes from the o2i-lexicons entry. The readings are Infopédia's in the
# spec's symbols: afetar ɐfɛˈtar, receção ʀəsɛˈsɐ̃w̃, respetivo ʀəʃpɛˈtivu. The spelling step
# gives the pre-AO1990 spellings the same reading.
@pytest.mark.parametrize("word, reading", [
    ("afetar", "ɐfɛˈtaɾ"),
    ("receção", "ʁɨsɛˈsɐ̃w̃"),
    ("respetivo", "ʁɨʃpɛˈtivu"),
    ("afectar", "ɐfɛˈtaɾ"),
    ("recepção", "ʁɨsɛˈsɐ̃w̃"),
    ("respectivo", "ʁɨʃpɛˈtivu"),
])
def test_the_vowel_before_a_dropped_c_or_p_reads_open(word, reading):
    assert phonemize(word, "pt-PT") == reading
