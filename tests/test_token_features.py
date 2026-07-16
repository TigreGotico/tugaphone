"""Phonological feature API on CharToken / GraphemeToken / WordToken.

The feature properties are read-only annotations: the TestIpaUnchanged guard
pins execution-captured IPA across the five major dialects to prove the layer
never changes transcription output.
"""

import pytest

from tugaphone.dialects import EuropeanPortuguese, BrazilianPortuguese
from tugaphone.tokenizer import Sentence


def _word(surface, dialect=None):
    return Sentence(surface, dialect=dialect or EuropeanPortuguese()).words[0]


def _chars(surface, dialect=None):
    return [c for g in _word(surface, dialect).graphemes for c in g.characters]


def _char(surface, index, dialect=None):
    return _chars(surface, dialect)[index]


class TestConsonantFeatures:
    @pytest.mark.parametrize("word,idx,manner", [
        ("bola", 0, "plosive"),
        ("faca", 0, "fricative"),
        ("mapa", 0, "nasal"),
        ("lata", 0, "lateral"),
        ("caro", 2, "rhotic"),
    ])
    def test_manner(self, word, idx, manner):
        assert _char(word, idx).manner_of_articulation == manner

    @pytest.mark.parametrize("word,idx,place", [
        ("bola", 0, "bilabial"),
        ("faca", 0, "labiodental"),
        ("dado", 0, "alveolar"),
        ("gato", 0, "velar"),
        ("já", 0, "postalveolar"),
    ])
    def test_place(self, word, idx, place):
        assert _char(word, idx).place_of_articulation == place

    def test_manner_none_for_vowel(self):
        assert _char("bola", 1).manner_of_articulation is None
        assert _char("bola", 1).place_of_articulation is None

    def test_voicing(self):
        assert _char("pato", 0).voicing == "voiceless"
        assert _char("bato", 0).voicing == "voiced"
        assert _char("bola", 1).voicing == "voiced"

    def test_intervocalic_s_is_voiced(self):
        s = _char("casa", 2)
        assert s.surface == "s"
        assert s.voicing == "voiced"

    def test_initial_s_is_voiceless(self):
        assert _char("sapo", 0).voicing == "voiceless"

    def test_sonorant_and_obstruent(self):
        assert _char("mapa", 0).is_sonorant and not _char("mapa", 0).is_obstruent
        assert _char("bola", 1).is_sonorant  # vowels are sonorant
        assert _char("pato", 0).is_obstruent and not _char("pato", 0).is_sonorant

    def test_class_predicates(self):
        assert _char("lata", 0).is_liquid
        assert _char("caro", 2).is_liquid and _char("caro", 2).is_rhotic
        assert not _char("mapa", 0).is_liquid
        assert _char("mapa", 0).is_nasal_consonant
        assert _char("sapo", 0).is_sibilant
        assert _char("faca", 0).is_fricative
        assert _char("pato", 0).is_plosive
        assert not _char("pato", 0).is_rhotic


class TestVowelQuality:
    def test_height(self):
        assert _char("vi", 1).vowel_height == "high"
        assert _char("pé", 1).vowel_height == "mid-low"
        assert _char("lá", 1).vowel_height == "low"

    def test_backness(self):
        assert _char("vi", 1).vowel_backness == "front"
        assert _char("tu", 1).vowel_backness == "back"
        assert _char("lá", 1).vowel_backness == "central"

    def test_roundedness(self):
        assert _char("tu", 1).vowel_roundedness == "rounded"
        assert _char("vi", 1).vowel_roundedness == "unrounded"

    def test_boolean_helpers(self):
        assert _char("vi", 1).is_front_vowel and not _char("vi", 1).is_back_vowel
        assert _char("tu", 1).is_back_vowel and _char("tu", 1).is_rounded_vowel

    def test_none_for_consonants(self):
        c = _char("pato", 0)
        assert c.vowel_height is None
        assert c.vowel_backness is None
        assert c.vowel_roundedness is None
        assert not c.is_front_vowel and not c.is_back_vowel and not c.is_rounded_vowel

    def test_ep_reduction_is_honoured(self):
        # EP unstressed e reduces to [ɨ]: high central
        e = _char("pedir", 1)
        assert e.ipa == "ɨ"
        assert e.vowel_height == "high"
        assert e.vowel_backness == "central"

    def test_br_keeps_full_vowel(self):
        e = _char("pedir", 1, BrazilianPortuguese())
        assert e.ipa == "e"
        assert e.vowel_height == "mid-high"
        assert e.vowel_backness == "front"


class TestSyllablePosition:
    def test_casa(self):
        c, a1, s, a2 = _chars("casa")
        assert c.is_onset and not c.is_coda and not c.is_nucleus
        assert a1.is_nucleus and not a1.is_onset
        assert s.is_onset  # ca.sa: s opens the second syllable
        assert a2.is_nucleus

    def test_mar_coda(self):
        m, a, r = _chars("mar")
        assert m.is_onset
        assert a.is_nucleus
        assert r.is_coda and not r.is_onset

    def test_festa(self):
        f, e, s, t, a = _chars("festa")
        assert f.is_onset
        assert s.is_coda  # fes.ta
        assert t.is_onset

    def test_diphthong_glide_is_not_nucleus(self):
        p, a, i = _chars("pai")
        assert a.is_nucleus
        assert not i.is_nucleus

    def test_idx_in_syllable_resets_per_syllable(self):
        idxs = [(c.surface, c.idx_in_syllable) for c in _chars("casa")]
        assert idxs == [("c", 0), ("a", 1), ("s", 0), ("a", 1)]

    def test_idx_in_syllable_with_doubled_consonant(self):
        # carro normalizes car.ro → ca.rro; rr starts the second syllable
        idxs = [(c.surface, c.idx_in_syllable) for c in _chars("carro")]
        assert idxs == [("c", 0), ("a", 1), ("r", 0), ("r", 1), ("o", 2)]

    def test_silent_h_is_neither_onset_nor_coda(self):
        h = _char("hora", 0)
        assert h.is_silent
        assert not h.is_onset and not h.is_coda


class TestGraphemeFeatures:
    def test_vowel_and_consonant_graphemes(self):
        w = _word("pai")
        p, ai = w.graphemes
        assert p.is_consonant_grapheme and not p.is_vowel_grapheme
        assert ai.is_vowel_grapheme and not ai.is_consonant_grapheme

    def test_syllable_position(self):
        w = _word("prato")
        positions = [(g.surface, g.syllable_position) for g in w.graphemes]
        assert positions == [("p", "onset"), ("r", "onset"), ("a", "nucleus"),
                             ("t", "onset"), ("o", "nucleus")]

    def test_coda_position(self):
        w = _word("mar")
        assert [g.syllable_position for g in w.graphemes] == ["onset", "nucleus", "coda"]

    def test_silent_h_classifies_as_onset(self):
        w = _word("hora")
        assert w.graphemes[0].syllable_position == "onset"

    def test_phonological_weight(self):
        w = _word("pai")
        assert w.graphemes[0].phonological_weight == 1
        assert w.graphemes[1].phonological_weight == 2  # diphthong

    def test_silent_grapheme_weighs_zero(self):
        w = _word("hora")
        assert w.graphemes[0].phonological_weight == 0

    def test_complex_onset(self):
        w = _word("prato")
        p, r = w.graphemes[0], w.graphemes[1]
        assert p.has_complex_onset and r.has_complex_onset
        assert p.is_onset_cluster
        assert not w.graphemes[3].has_complex_onset  # plain t onset

    def test_no_cluster_across_syllables(self):
        # fes.ta: s (coda) + t (onset) are adjacent but not an onset cluster
        w = _word("festa")
        assert not any(g.has_complex_onset for g in w.graphemes)

    def test_palatal_digraphs(self):
        assert any(g.is_palatal for g in _word("vinho").graphemes)
        assert any(g.is_palatal for g in _word("milho").graphemes)
        assert not any(g.is_palatal for g in _word("casa").graphemes)

    def test_triggers_palatalization(self):
        w = _word("dia", BrazilianPortuguese())
        i = w.graphemes[1]
        assert i.surface == "i"
        assert i.triggers_palatalization
        assert not w.graphemes[2].triggers_palatalization  # final a


class TestWordFeatures:
    @pytest.mark.parametrize("word,pattern", [
        ("sol", "monosyllable"),
        ("café", "oxytone"),
        ("casa", "paroxytone"),
        ("médico", "proparoxytone"),
    ])
    def test_stress_pattern(self, word, pattern):
        assert _word(word).stress_pattern == pattern

    def test_syllable_structure_pattern(self):
        assert _word("casa").syllable_structure_pattern == "CV.CV"
        assert _word("sol").syllable_structure_pattern == "CVC"
        assert _word("prato").syllable_structure_pattern == "CCV.CV"

    def test_sequences(self):
        w = _word("casa")
        assert w.vowel_sequence == "a.a"
        assert w.consonant_sequence == "c.s"

    def test_phoneme_count(self):
        assert _word("casa").phoneme_count == 4
        assert _word("pai").phoneme_count == 3

    def test_boolean_summaries(self):
        assert _word("pai").has_diphthongs
        assert not _word("casa").has_diphthongs
        assert _word("pão").has_nasal_sounds
        assert not _word("casa").has_nasal_sounds
        assert _word("vinho").has_palatal_sounds
        assert _word("prato").has_consonant_clusters
        assert not _word("casa").has_consonant_clusters

    def test_homograph_and_irregular(self):
        assert _word("gosto").is_homograph
        assert not _word("casa").is_homograph
        # the lexicon backs IRREGULAR_WORDS, so common words are lexical;
        # an out-of-lexicon neologism is not
        assert _word("muito").is_irregular
        assert not _word("zubralho").is_irregular


class TestFeatureDicts:
    def test_char_feature_keys(self):
        feats = _char("casa", 0).features
        for key in ["manner_of_articulation", "place_of_articulation", "voicing",
                    "vowel_height", "vowel_backness", "vowel_roundedness",
                    "idx_in_syllable", "is_nucleus", "is_onset", "is_coda",
                    "is_sonorant", "is_obstruent", "is_liquid", "is_sibilant",
                    "is_rhotic", "is_plosive", "is_fricative"]:
            assert key in feats

    def test_grapheme_feature_keys(self):
        feats = _word("vinho").graphemes[2].features
        for key in ["syllable_position", "phonological_weight",
                    "has_complex_onset", "is_onset_cluster", "is_palatal",
                    "triggers_palatalization", "is_vowel_grapheme",
                    "is_consonant_grapheme", "idx_in_syllable"]:
            assert key in feats

    def test_word_feature_keys(self):
        feats = _word("casa").features
        for key in ["text", "ipa", "syllables", "stress_pattern",
                    "syllable_structure_pattern", "phoneme_count",
                    "vowel_sequence", "consonant_sequence", "has_diphthongs",
                    "has_nasal_sounds", "has_palatal_sounds",
                    "has_consonant_clusters", "is_homograph", "is_irregular"]:
            assert key in feats

    def test_sentence_features_build(self):
        s = Sentence("O gato dorme", dialect=EuropeanPortuguese())
        assert s.features


@pytest.fixture(scope="module")
def pho():
    from tugaphone import TugaPhonemizer
    return TugaPhonemizer()


GUARD = [
    # Pinned from dev, so the assertion below means what it says: adding the
    # feature layer changes no transcription. Re-pin from dev, never from this
    # branch — pinning from the branch would make the test assert nothing.
    ("pt-PT", "O gato dorme.", "ˈu gˈa·tu ˈdoɾ·mɨ"),
    ("pt-BR", "O gato dorme.", "ˈu gˈa·tʊ ˈdoɾ·mɪ"),
    ("pt-AO", "O gato dorme.", "ˈu gˈa·tʊ ˈdoɾ·me"),
    ("pt-MZ", "O gato dorme.", "ˈu gˈa·tu ˈdoɾ·me"),
    ("pt-TL", "O gato dorme.", "ˈu gˈa·tʊ ˈdoɾ·me"),
    ("pt-PT", "A menina comeu o pão todo.", "ɐ mɨ·nˈi·nɐ ku·ˈmew ˈu pˈɐ̃w tˈo·du"),
    ("pt-BR", "A menina comeu o pão todo.", "a mẽ·nˈĩ·nɐ ko·ˈmew ˈu pˈɐ̃w tˈo·dɐ"),
    ("pt-AO", "A menina comeu o pão todo.", "a me·nˈi·nɐ ko·ˈmew ˈu pˈɐ̃w tˈo·dɐ"),
    ("pt-MZ", "A menina comeu o pão todo.", "ɐ me·nˈi·nɐ ku·ˈmew ˈu pˈãw tˈo·du"),
    ("pt-TL", "A menina comeu o pão todo.", "ə mɨ·nˈi·nə ko·ˈmew ˈu pˈə̃w tˈo·də"),
    ("pt-PT", "Choveu muito ontem à noite.", "ʃu·ˈvew mˈũj·tu ˈõ·tɐ̃j ˈa nˈojt"),
    ("pt-BR", "Choveu muito ontem à noite.", "ʃo·ˈvew mwˈĩ·tʊ ˈõ·tẽj ˈa nˈoj·tʃɪ"),
    ("pt-AO", "Choveu muito ontem à noite.", "ʃo·ˈvew mˈũjn·tʊ ˈõn·tẽj ˈa nˈoj·tɨ"),
    ("pt-MZ", "Choveu muito ontem à noite.", "ʃu·ˈvew mˈũj·tu ˈõ·tẽj ˈa nˈɔj·tɨ"),
    ("pt-TL", "Choveu muito ontem à noite.", "ʃo·ˈvew mˈuj·tʊ ˈõn·tɐ̃j ˈa nˈojtʰ"),
]


class TestIpaUnchanged:
    """The feature layer is inert: the grapheme cascade's per-token IPA is
    pinned per dialect, so exposing manner/place/height features off the tokens
    changes no transcription.

    This guards the token-cascade (``Sentence.ipa``), not the phonemization
    path — the public ``phonemize_sentence`` drives the orthography2ipa lattice
    (see ``tugaphone.lattice_core``) and is guarded by the gold benchmark.
    """

    @pytest.mark.parametrize("code,sentence,expected", GUARD)
    def test_output_pinned(self, code, sentence, expected):
        from tugaphone.registry import get_dialect_inventory
        from tugaphone.tokenizer import Sentence
        inv = get_dialect_inventory(code)
        assert Sentence(sentence, dialect=inv).ipa == expected
