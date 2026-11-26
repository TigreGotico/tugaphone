"""tugaphone's stress and silabificador's stress must agree.

Two libraries compute Portuguese stress, and they do it differently.
silabificador derives it from phonotactics (2.x); tugaphone reads the declarative
``StressRules`` of the dialect's orthography2ipa spec — written accent, then
oxytone endings, then the paroxytone default.

Two independent routes to the same answer is a good thing: it means a bug in
either shows up as a disagreement rather than as a silently wrong transcription.
This pins that. On the syllabifier's own 500-word held-out gold they agree on
**every** word, so any disagreement is a regression in one of them.

The comparison is on the stressed SYLLABLE, not its index: the two engines must
be given the same split before their answers can be compared at all.
"""
import json
import os
import re
import unicodedata

import pytest
from silabificador import Syllabifier

from tugaphone import phonemize

# A syllable nucleus: a run of vowel symbols. The glides [j w] are not nuclei.
NUCLEUS = re.compile("[aɐeɛəɨioɔuʊɪ]\u0303?(?:[aɐeɛəɨioɔuʊɪ]\u0303?)*")


def stressed_index(word, syllables):
    """The index in ``syllables`` of the syllable that carries ``ˈ``.

    The syllables from the mark to the end of the word are its nuclei.
    """
    after = unicodedata.normalize("NFD", phonemize(word, "pt-PT")).partition("ˈ")[2]
    return len(syllables) - len(NUCLEUS.findall(after))

GOLD = os.path.join(
    os.path.dirname(__file__), "..", "..", "silabificador",
    "tests", "gold_sample.json",
)


def _gold():
    if not os.path.exists(GOLD):
        pytest.skip("silabificador's gold is not checked out beside this repo")
    with open(GOLD, encoding="utf-8") as fh:
        return json.load(fh)["entries"]


def test_the_two_stress_engines_agree():
    syllabifier = Syllabifier()
    disagreements = []

    for entry in _gold():
        word = entry["word"]
        syllables = syllabifier.syllabify(word)  # one split, so the indices mean the same thing
        ours = stressed_index(word, syllables)
        theirs = syllabifier.stressed_index(word)
        if ours != theirs:
            disagreements.append(
                f"{word}: {'-'.join(syllables)} — tugaphone {syllables[ours]!r}, "
                f"silabificador {syllables[theirs]!r}"
            )

    assert not disagreements, (
        "tugaphone and silabificador disagree on where the stress falls. One of "
        "them has regressed:\n  " + "\n  ".join(disagreements)
    )


@pytest.mark.parametrize("word,expected", [
    ("café", "fé"),          # written accent wins
    ("menina", "ni"),        # paroxytone default
    ("comeu", "meu"),        # oxytone ending
    ("fantástico", "tás"),   # proparoxytone by accent
])
def test_the_stress_rules_themselves(word, expected):
    """A handful of cases spelled out, so the invariant above cannot pass vacuously."""
    syllabifier = Syllabifier()
    syllables = syllabifier.syllabify(word)
    idx = stressed_index(word, syllables)
    assert syllables[idx] == expected
