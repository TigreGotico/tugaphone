"""The vowel of ⟨que gue⟩ follows the stress like any other ⟨e⟩.

European Portuguese reduces an unstressed ⟨e⟩ to [ɨ] and keeps a stressed
one as a full mid vowel, [e] or [ɛ]. The ⟨qu gu⟩ digraph does not change
that: *queda* has a stressed [ɛ] and *querer* an unstressed [ɨ] in the
same onset. Each expected vowel below is read off the Infopédia (pt-PT) or
Portal (pt-BR) transcription in the unified gold
(``TigreGotico/portuguese-unified-pronunciation-lexicon``). Whether a
stressed ⟨e⟩ is open or closed is lexical and the spelling does not show
it, so a stressed row accepts either mid vowel.
"""
import unicodedata

import pytest

from tugaphone import phonemize

FULL, REDUCED = {"e", "ɛ"}, {"ɨ"}


def vowel_after(word, onset, lect):
    """The vowel written right after the ⟨qu gu⟩ onset and its glide."""
    ipa = unicodedata.normalize("NFD", phonemize(word, lect).strip())
    for ch in "ˈˌ":
        ipa = ipa.replace(ch, "")
    at = ipa.index(onset) + len(onset)
    return ipa[at], ipa


# dialect, word, gold transcription, consonant + glide onset, vowel class
ROWS = [
    ("pt-PT", "queda", "ˈkɛdɐ", "k", FULL),
    ("pt-PT", "sequer", "sɨˈkɛɾ", "k", FULL),
    ("pt-PT", "qualquer", "kwaɫˈkɛr", "ɫk", FULL),
    ("pt-PT", "guerra", "ˈɡɛʀɐ", "ɡ", FULL),
    ("pt-PT", "aquele", "ɐˈkel", "k", FULL),
    ("pt-PT", "pequeno", "pɨˈkenu", "pɨk", FULL),
    ("pt-PT", "foguete", "fuˈɡet", "ɡ", FULL),
    ("pt-PT", "frequente", "frəˈkwẽt", "kw", FULL),
    ("pt-PT", "querer", "kɨˈɾeɾ", "k", REDUCED),
    ("pt-PT", "guerreiro", "ɡəˈʀɐjru", "ɡ", REDUCED),
    ("pt-BR", "qualquer", "kwawˈkɛɾ", "wk", FULL),
]


@pytest.mark.parametrize("dialect,word,gold,onset,allowed", ROWS)
def test_que_gue_vowel(dialect, word, gold, onset, allowed):
    vowel, ipa = vowel_after(word, onset, dialect)
    assert vowel in allowed, ipa


# The function word *que* is atonic and keeps [ɨ]; only *quê* is stressed.
# Infopédia: que "kə", quê "ˈke", quer "ˈkɛr" (its ə is the [ɨ] written
# elsewhere in this file). Each row lists the vowel after [k] in every word
# of the sentence that starts with ⟨qu⟩, in order.
SENTENCE_ROWS = [
    ("que", [REDUCED]),
    ("quê", [FULL]),
    ("eu sei que vens", [REDUCED]),
    ("o que é que queres", [REDUCED, REDUCED, FULL]),
]


@pytest.mark.parametrize("sentence,classes", SENTENCE_ROWS)
def test_function_word_que_keeps_the_reduced_vowel(sentence, classes):
    ipa = phonemize(sentence, "pt-PT").strip()
    words = [w for w in sentence.split() if w.startswith("qu")]
    spoken = [w.strip("ˈˌ")
              for w, o in zip(ipa.split(), sentence.split()) if o.startswith("qu")]
    assert len(spoken) == len(words) == len(classes), ipa
    for word, allowed in zip(spoken, classes):
        assert word[1] in allowed, ipa


# The other atonic monosyllables of ``stress.cliticless_words`` keep [ɨ] too.
# Infopédia: se "sə", me "mə", te "tə", lhe "ʎə", de "də".
@pytest.mark.parametrize("word,onset", [
    ("se", "s"), ("me", "m"), ("te", "t"), ("lhe", "ʎ"), ("de", "d")])
def test_clitic_keeps_the_reduced_vowel(word, onset):
    vowel, ipa = vowel_after(word, onset, "pt-PT")
    assert vowel in REDUCED, ipa
