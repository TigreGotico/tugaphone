"""A ``<phoneme>`` element keeps its forced reading in every contact mode.

The code-switch router splits the text into tokens before it routes them. A
``<phoneme ph="…">…</phoneme>`` element holds a space between the tag name and
``ph``, so the element must stay one token; the Portuguese engine reads its
markup. The forced word is never routed to a contact lattice. Malformed markup
raises the same error as the engine raises with contact ``"none"``.
"""
import pytest
import orthography2ipa.g2p
from orthography2ipa.markup import MarkupError

from tugaphone.codeswitch import split_runs
from tugaphone.lattice_core import phonemize

CONTACT_MODES = ["en", "auto", "es", "fr"]


@pytest.fixture(scope="module", autouse=True)
def cached_inventory():
    """Compute the inventory that a forced word is checked against once per engine.

    The engine checks each forced word against the phoneme inventory of its spec
    and lexicon, and it computes that inventory again for every forced word. With
    the packaged pt-PT lexicon this takes several seconds each time. The engines
    are cached, so their spec and lexicon do not change, and one result per
    engine gives the same check.
    """
    compute = orthography2ipa.g2p.phoneme_inventory
    cache = {}

    def phoneme_inventory(spec, lexicon=None):
        # The cache holds spec and lexicon, so their ids stay theirs.
        key = (id(spec), id(lexicon))
        if key not in cache:
            cache[key] = (spec, lexicon, compute(spec, lexicon))
        return cache[key][2]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(orthography2ipa.g2p, "phoneme_inventory", phoneme_inventory)
        yield

# Each sentence is Portuguese apart from the forced word, so contact routing
# must leave the whole sentence to the Portuguese engine: the contact-mode
# output equals the contact "none" output of the same text.
FORCED = [
    # the forced word starts the sentence
    '<phoneme ph="ˈʒoɡu">jogo</phoneme> o jogo 2 vezes.',
    # the forced word sits in the middle of the sentence
    'Ela viu <phoneme ph="ˈfoɾsɐ">força</phoneme> a força dele.',
    # two forced words
    'O <phoneme ph="ˈʒoɡu">jogo</phoneme> e a <phoneme ph="ˈfoɾsɐ">força</phoneme> dele.',
]

UNCLOSED = '<phoneme ph="ˈʒoɡu">jogo o jogo 2 vezes.'


@pytest.mark.parametrize("contact", CONTACT_MODES)
@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("text", FORCED)
def test_forced_word_reads_as_with_contact_none(text, lang, contact, classifier):
    assert phonemize(text, lang, contact) == phonemize(text, lang, "none")


@pytest.mark.parametrize("contact", CONTACT_MODES)
@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
def test_forced_ipa_reaches_the_output(lang, contact, classifier):
    words = phonemize(FORCED[2], lang, contact).split()
    assert words[1] == "ˈʒoɡu"
    assert words[4] == "ˈfoɾsɐ"


@pytest.mark.parametrize("contact", CONTACT_MODES + ["none"])
def test_element_is_one_portuguese_token(contact, classifier):
    runs = split_runs(FORCED[1], contact)
    assert runs[2] == (None, '<phoneme ph="ˈfoɾsɐ">força</phoneme>')
    assert [token for _, token in runs] == [
        "Ela", "viu", '<phoneme ph="ˈfoɾsɐ">força</phoneme>', "a", "força", "dele."]


@pytest.mark.parametrize("contact", CONTACT_MODES)
def test_english_spelling_in_an_element_is_not_routed(contact, classifier):
    # "Google" alone routes to a contact lattice; inside an element its
    # reading is the forced one.
    text = 'Abri o <phoneme ph="ˈɡuɡɫ">Google</phoneme>, ontem.'
    assert split_runs(text, contact)[2] == (None, '<phoneme ph="ˈɡuɡɫ">Google</phoneme>,')
    assert phonemize(text, "pt-PT", contact).split()[2] == "ˈɡuɡɫ"


@pytest.mark.parametrize("contact", CONTACT_MODES)
@pytest.mark.parametrize("text", [
    UNCLOSED,
    'jogo</phoneme> o jogo 2 vezes.',
    '<phoneme alphabet="x-sampa" ph="Zogu">jogo</phoneme> o jogo.',
])
def test_malformed_markup_raises_as_with_contact_none(text, contact, classifier):
    with pytest.raises(MarkupError) as none_error:
        phonemize(text, "pt-PT", "none")
    with pytest.raises(MarkupError) as contact_error:
        phonemize(text, "pt-PT", contact)
    assert str(contact_error.value) == str(none_error.value)


@pytest.mark.parametrize("text", [
    "fiz o download do app",
    "  dois\tespaços\n e um nbsp em\x1cfim  ",
    "a <b> c < phoneme d",
    "",
])
def test_text_without_markup_splits_as_str_split(text):
    assert [token for _, token in split_runs(text, "en")] == text.split()
