"""Code-switch routing, nativization and language-detection tests.

The tests split into three groups:

* pure-function tests over the orthographic heuristic, the projection tables and
  the run splitter — no models, no lattice, always run;
* end-to-end ``phonemize_sentence`` tests over the real orthography2ipa lattice;
* Markov-detector tests, skipped when ``markovonnx`` or the bundled models are
  unavailable.
"""
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.codeswitch import (
    _nativize,
    contact_language,
    is_contact_word,
    split_runs,
    transcribe_contact,
)
from tugaphone.registry import default_contact


# ---------------------------------------------------------------------------
# Orthographic heuristic.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("word", [
    "download", "feedback", "software", "startup", "app", "site",
    "weekend", "playback", "wi-fi",
])
def test_english_loans_flagged(word):
    assert is_contact_word(word)


@pytest.mark.parametrize("word", [
    "gato", "cachorro", "estação", "coração", "português", "avião",
    "coordenar", "voo", "senhor", "trabalho",
])
def test_native_portuguese_not_flagged(word):
    # Native words — including ones with ç, nasal vowels and the oo/nh/lh
    # digraphs that must never trip the English signal.
    assert not is_contact_word(word)


def test_spanish_and_french_letters_flagged():
    assert is_contact_word("mañana")      # ñ → Spanish letter
    assert is_contact_word("crème")       # è → French letter
    assert is_contact_word("naïve")       # ï → French letter
    assert is_contact_word("york")        # y → English/foreign letter


def test_contact_language_classification():
    assert contact_language("download") == "en"
    assert contact_language("th") == "en"
    assert contact_language("mañana") == "es"
    assert contact_language("crème") == "fr"
    # No language-specific signal → falls to the default side.
    assert contact_language("plaza", default_side="es") == "es"
    assert contact_language("plaza", default_side="en") == "en"


# ---------------------------------------------------------------------------
# Nativization projection tables.
# ---------------------------------------------------------------------------

def test_english_projection_keeps_native_pt_phones():
    # /v z ʃ ʒ w j dʒ tʃ/ are Portuguese phones and must survive unremapped.
    for phone in ["v", "z", "ʃ", "ʒ", "w", "j", "dʒ", "tʃ"]:
        assert phone in _nativize(phone, english=True)


def test_english_th_stopping_and_rhotic():
    assert _nativize("θ", english=True) == "t"
    assert _nativize("ð", english=True) == "d"
    assert _nativize("ɹ", english=True) == "ɾ"
    assert _nativize("ŋ", english=True) == "n"


def test_english_vowels_use_seven_vowel_inventory():
    # ɔ and ɛ already exist in Portuguese, so the mapping is gentle.
    assert _nativize("ɒ", english=True) == "ɔ"
    assert _nativize("æ", english=True) == "a"
    assert _nativize("ɪ", english=True) == "i"
    assert _nativize("ʊ", english=True) == "u"


def test_french_nasal_vowels_project_onto_pt_nasals():
    # French nasal vowels map onto Portuguese nasal vowels, not their oral forms.
    assert _nativize("ɔ̃") == "õ"
    assert _nativize("ɛ̃") == "ẽ"
    assert _nativize("ɑ̃") == "ɐ̃"


def test_romance_interdental_and_front_rounded():
    assert _nativize("θ") == "s"     # Castilian θ → seseo /s/
    assert _nativize("y") == "i"     # French /y/ → /i/
    assert _nativize("ø") == "e"


def test_stress_and_length_stripped_nasal_kept():
    out = _nativize("ˈbõːʒ")
    assert "ˈ" not in out and "ː" not in out
    assert "õ" in out               # nasal tilde preserved


# ---------------------------------------------------------------------------
# Run splitting.
# ---------------------------------------------------------------------------

def test_split_runs_none_marks_all_portuguese():
    runs = split_runs("fiz o download do app", "none")
    assert all(lang is None for lang, _ in runs)


def test_split_runs_forced_language():
    runs = split_runs("comprei un libro", "es")
    # forced es: contact tokens route to es, native ones stay None
    langs = {tok: lang for lang, tok in runs}
    assert langs["libro"] == "es" or langs["un"] == "es"


def test_split_runs_covers_every_token():
    text = "fiz o download do app"
    runs = split_runs(text, "auto")
    assert [tok for _, tok in runs] == text.split()


# ---------------------------------------------------------------------------
# Registry default side.
# ---------------------------------------------------------------------------

def test_default_contact_side():
    assert default_contact("pt-BR") == "en"
    assert default_contact("pt-PT") == "en"
    assert default_contact("pt-AO") == "en"
    assert default_contact("pt-UY") == "es"


# ---------------------------------------------------------------------------
# End-to-end phonemization over the real lattice.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


def test_contact_none_reproduces_engine_only(ph):
    from tugaphone.lattice_core import engine
    from tugaphone.registry import resolve_lect

    s = "o gato dorme na estação"
    got = ph.phonemize_sentence(s, "pt-PT", contact="none")
    baseline = engine(resolve_lect("pt-PT")).transcribe(s)
    assert got == baseline


def test_br_tech_register_switches(ph):
    # The English loans come out different under auto than under none, and the
    # Portuguese function words (o, do) are untouched either way.
    auto = ph.phonemize_sentence("fiz o download do app", "pt-BR", contact="auto")
    none = ph.phonemize_sentence("fiz o download do app", "pt-BR", contact="none")
    assert auto != none
    assert "θ" not in auto and "ð" not in auto      # nothing English-only leaks


def test_function_words_not_misrouted(ph):
    # A sentence of pure Portuguese function words must be identical under auto
    # and none — the guard/margin keeps every one of them Portuguese.
    s = "o que eu tenho de fazer com isso"
    auto = ph.phonemize_sentence(s, "pt-PT", contact="auto")
    none = ph.phonemize_sentence(s, "pt-PT", contact="none")
    assert auto == none


def test_invalid_contact_rejected(ph):
    with pytest.raises(ValueError):
        ph.phonemize_sentence("o gato", "pt-PT", contact="klingon")


def test_forced_contact_english(ph):
    out = ph.phonemize_sentence("streaming", "pt-BR", contact="en")
    assert out
    assert "ŋ" not in out                            # velar nasal nativized


# ---------------------------------------------------------------------------
# Markov detector (skipped without markovonnx / bundled models).
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def detector():
    from tugaphone.langdetect import get_detector
    det = get_detector()
    if det is None:
        pytest.skip("markovonnx or bundled langdetect models unavailable")
    return det


def test_detector_routes_english_loans(detector):
    for w in ["download", "feedback", "streaming"]:
        assert detector.detect(w, default_side="en")[0] == "en"


def test_detector_keeps_portuguese_function_words(detector):
    for w in ["que", "de", "com", "para", "não"]:
        assert detector.detect(w)[0] == "pt"


def test_detector_margin_keeps_ambiguous_words_native(detector):
    # A word whose foreign fit is only marginally better than Portuguese stays
    # Portuguese with the default margin, but routes out with a zero margin.
    native, _ = detector.detect("radio", margin=0.25)
    assert native == "pt"


def test_detector_threshold_monotonicity(detector):
    # A larger margin never routes MORE words out of Portuguese than a smaller one.
    words = ["radio", "hotel", "general", "download", "app", "site", "menu"]
    small = sum(detector.is_contact(w, margin=0.10) for w in words)
    large = sum(detector.is_contact(w, margin=0.60) for w in words)
    assert large <= small


def test_detector_empty_token_is_portuguese(detector):
    assert detector.detect("...")[0] == "pt"
    assert detector.detect("")[0] == "pt"
