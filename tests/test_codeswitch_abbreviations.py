"""Abbreviations under code-switching.

The normalizer expands an abbreviation and reads a Roman numeral after a
part-of-work noun from its neighbours. After its noun, a numeral up to ten is
an ordinal and from eleven on a cardinal, for kings, popes, centuries and
chapters (Silveira Bueno, Questões de Português, 1957, vol. II, p. 318, quoted
by José Maria da Costa in Migalhas "Gramatigalhas: Numeral"), so "Cap. XII" is
"capítulo doze". Code-switch routing splits the text into words before the
normalizer runs. An abbreviation that only Portuguese reads in its context
stays Portuguese; every other token is left to the router.
"""
import pytest

from tugaphone import TugaPhonemizer
from tugaphone.codeswitch import _classify, _is_contact, split_runs, transcribe_contact
from tugaphone.text_normalization import normalize_orthography

SENTENCE = "Tenho 23 anos, Sr. Silva; li o Cap. XII."
# The sentence as a reader says it, written out by hand.
SPOKEN = "Tenho vinte e três anos, Senhor Silva; li o capítulo doze."


@pytest.fixture(scope="module")
def ph():
    return TugaPhonemizer()


def _router(token, contact):
    """The route the classifier alone gives *token*, with no abbreviation
    guard: what ``split_runs`` must give a token the guard does not claim."""
    if contact == "auto":
        return _classify(token, "en")
    return contact if _is_contact(token) else None


def _route(text, contact, index):
    return split_runs(text, contact)[index]


@pytest.mark.parametrize("lect", ["pt-PT", "pt-BR"])
@pytest.mark.parametrize("contact", ["none", "en", "auto"])
@pytest.mark.parametrize("written,spoken", [
    (SENTENCE, SPOKEN),
    ("ver (Cap. XII) e (art. 5.º)", "ver (capítulo doze) e (artigo quinto)"),
    ("«Cap. XII»", "«capítulo doze»"),
    ("li o Cap. X.", "li o capítulo décimo."),
    ("de D. Maria I no baú", "de Dona Maria Primeira no baú"),
    ("S. Ex.ª o Presidente", "Sua Excelência o Presidente"),
])
def test_reads_as_spoken(ph, lect, contact, written, spoken):
    expected = ph.phonemize_sentence(spoken, lect, contact="none")
    assert ph.phonemize_sentence(written, lect, contact=contact) == expected


@pytest.mark.parametrize("contact", ["en", "auto"])
@pytest.mark.parametrize("text,index", [
    ("Cap. XII", 0), ("cap. 3", 0), ("(art. 5.º)", 0), ("«Cap. XII»", 0),
    ("Art. 5", 0), ("pág. 4", 0), ("Séc. XIX", 0), ("Tel. 21", 0),
    ("a Av. da Liberdade", 1), ("o Dr. Silva", 1), ("o Eng. Costa", 1),
    ("os Srs. deputados", 1), ("Exmo. Senhor", 0), ("Ex.mo Senhor", 0),
    ("Benfica vs. Porto", 1), ("D. Maria", 0), ("S. Ex.ª", 0),
    # the number of a reference marker stays with it
    ("Cap. X", 1), ("Séc. X", 1),
])
def test_abbreviation_stays_portuguese(classifier, contact, text, index):
    assert _route(text, contact, index) == (None, text.split()[index])


@pytest.mark.parametrize("contact", ["en", "auto"])
@pytest.mark.parametrize("text,index", [
    # an English word with a sentence period
    ("Ela adora street art.", 3),
    ("Eu jogo com os elementos da natureza quando pratico land art.", 10),
    ("Ela adora street art. Depois saiu.", 3),
    ("Ela usa sempre um cap.", 4),
    # "Cap." before a name is also the military rank
    ("O Cap. Salgueiro Maia saiu do quartel.", 1),
    # initials
    ("o livro de George R. R. Martin", 4),
    ("o livro de George R. R. Martin", 5),
    ("S. Pedro", 0),
    ("a vitamina D. Depois", 2),
    # a contact word that ends in a period
    ("fiz o download.", 2),
    ("Gosto de jazz.", 2),
])
def test_router_decides(classifier, contact, text, index):
    token = text.split()[index]
    assert _route(text, contact, index) == (_router(token, contact), token)


def test_english_art_reads_english(ph):
    # The detector (a test dependency) routes "art."; the spelling fallback
    # keeps it Portuguese, as it did before the abbreviation guard.
    assert _router("art.", "en") == "en"
    ipa = ph.phonemize_sentence("Ela adora street art.", "pt-PT", contact="en")
    assert ipa.split()[-1] == transcribe_contact("art.", "en")


@pytest.mark.parametrize("contact", ["en", "auto"])
def test_period_final_contact_word_routes(classifier, contact):
    assert _route("fiz o download.", contact, 2) == ("en", "download.")


@pytest.mark.parametrize("text,expected", [
    ("li o Cap. XII.", "li o Capítulo Doze."),
    ("Cap. 3 descreve", "Capítulo 3 descreve"),
    ("Art. 5 da lei", "Artigo 5 da lei"),
    ("Fig. 2 mostra", "Figura 2 mostra"),
    ("Séc. XIX", "Século Dezanove"),
    ("Tel. 21 000 000", "Telefone 21 000 000"),
    ("o N.º 4", "o número 4"),
    ("ver (Cap. XII)", "ver (Capítulo Doze)"),
    ("«Cap. XII»", "«Capítulo Doze»"),
    ("(art. 5.º)", "(artigo 5.º)"),
    ("ver Fig. II", "ver Figura Segunda"),
    ("a Pág. IV", "a Página Quarta"),
    ("ver fig. XII", "ver figura doze"),
    # a capitalised marker that no number follows is left as written
    ("O Cap. Salgueiro Maia saiu", "O Cap. Salgueiro Maia saiu"),
    ("Conheci o Art.", "Conheci o Art."),
    ("Batman Vs. Superman", "Batman Vs. Superman"),
])
def test_capitalised_abbreviation_expands(text, expected):
    assert normalize_orthography(text) == expected
