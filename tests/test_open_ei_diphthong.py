"""AO1990 Base IX 3.º dropped the accent of the open ``éi`` in Brazilian paroxytones.

In Brazilian Portuguese the accent removal changed only the spelling: the vowel stays
open, so ``ideia`` reads as ``idéia``. tugaphone restores that open vowel for the
Brazilian lects only.
"""
import pytest

from tugaphone import lattice_core, phonemize

# pt-BR-x-rio is a legacy alias of the canonical pt-BR-x-rj.
BR_LECTS = ["pt-BR", "pt-BR-x-rj"]


@pytest.mark.parametrize("word, accented", [
    ("ideia", "idéia"),
    ("estreia", "estréia"),
    ("traqueia", "traquéia"),
])
@pytest.mark.parametrize("lect", BR_LECTS)
def test_ao1990_open_ei_reads_as_the_accented_form(lect, word, accented):
    # Michaelis transcribes the open vowel; AO1990 Base IX 3.º removed only the accent.
    assert phonemize(word, lect) == phonemize(accented, lect)


@pytest.mark.parametrize("word, accented", [
    ("ideias", "idéias"),
    ("plateias", "platéias"),
])
@pytest.mark.parametrize("lect", BR_LECTS)
def test_ao1990_open_ei_plural_reads_as_the_accented_form(lect, word, accented):
    # desacordo holds only the singular, so the plural is restored through its stem.
    assert phonemize(word, lect) == phonemize(accented, lect)


@pytest.mark.parametrize("word, expected", [
    ("feia", "ˈfejɐ"),
    ("feias", "ˈfejɐs"),
    ("baleia", "baˈlejɐ"),
    ("baleias", "baˈlejɐs"),
    ("cheia", "ˈʃejɐ"),
    ("cheias", "ˈʃejɐs"),
])
def test_closed_ei_stays_closed_in_pt_br(word, expected):
    # These had no accent before AO1990 either, and their vowel is closed.
    assert phonemize(word, "pt-BR") == expected


def test_pt_pt_output_does_not_change():
    # The step runs for the Brazilian lects only; the pt-PT reading is unchanged.
    assert phonemize("ideia", "pt-PT") == "iˈdejɐ"


def test_normalize_spelling_restores_the_accent_in_the_br_group():
    assert lattice_core.normalize_spelling("A Ideia, a estreia.", "pt-BR") == "A Idéia, a estréia."


def test_normalize_spelling_restores_the_accent_in_the_br_plural():
    assert lattice_core.normalize_spelling("As Ideias.", "pt-BR") == "As Idéias."


def test_single_accent_guard_rejects_a_multi_change_rewrite(monkeypatch):
    # A conversion that changes more than one ``e`` → ``é`` must be rejected, so the
    # word stays as written. desacordo would rewrite ``autoestreia`` to ``auto-estréia``.
    real = lattice_core.convert_spelling

    def wrapper(word, *args, **kwargs):
        if word == "autoestreia" and args == ("ao1990-br", "br_1971"):
            return "auto-estréia"
        return real(word, *args, **kwargs)

    monkeypatch.setattr(lattice_core, "convert_spelling", wrapper)
    assert lattice_core.normalize_spelling("autoestreia", "pt-BR") == "autoestreia"


def test_token_count_stays():
    assert len(phonemize("a ideia nova", "pt-BR").split()) == 3
