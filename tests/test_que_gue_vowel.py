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
import pytest

from tugaphone.registry import get_dialect_inventory
from tugaphone.tokenizer import Sentence

FULL, REDUCED = {"e", "ɛ"}, {"ɨ"}


@pytest.fixture(scope="module")
def inventories():
    out = {}
    for code in ("pt-PT", "pt-BR"):
        inv = get_dialect_inventory(code)
        object.__setattr__(inv, "IRREGULAR_WORDS", {})
        out[code] = inv
    return out


def vowel_after(word, onset, inv):
    """The vowel written right after the ⟨qu gu⟩ onset and its glide."""
    ipa = Sentence(word, dialect=inv).ipa.strip()
    for ch in "ˈˌ·":
        ipa = ipa.replace(ch, "")
    at = ipa.index(onset) + len(onset)
    return ipa[at], ipa


# dialect, word, gold transcription, consonant + glide onset, vowel class
ROWS = [
    ("pt-PT", "queda", "ˈkɛdɐ", "k", FULL),
    ("pt-PT", "sequer", "sɨˈkɛɾ", "k", FULL),
    ("pt-PT", "qualquer", "kwaɫˈkɛr", "lk", FULL),
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
def test_que_gue_vowel(dialect, word, gold, onset, allowed, inventories):
    vowel, ipa = vowel_after(word, onset, inventories[dialect])
    assert vowel in allowed, ipa
