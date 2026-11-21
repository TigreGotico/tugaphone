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


def test_areia_reads_with_a_closed_ei():
    # Michaelis transcribes areia closed; the ABL VOLP gives it no "(é)" mark.
    ipa = phonemize("areia", "pt-BR")
    assert "ej" in ipa
    assert "ɛj" not in ipa


def test_ideia_still_reads_with_an_open_ei():
    # The control: an AO1990 open-éi paroxytone still reads open.
    ipa = phonemize("ideia", "pt-BR")
    assert "ɛj" in ipa


def test_pt_pt_output_does_not_change():
    # The step runs for the Brazilian lects only; the pt-PT reading is unchanged.
    assert phonemize("ideia", "pt-PT") == "iˈdejɐ"


def test_normalize_spelling_restores_the_accent_in_the_br_group():
    assert lattice_core.normalize_spelling("A Ideia, a estreia.", "pt-BR") == "A Idéia, a estréia."


def test_normalize_spelling_restores_the_accent_in_the_br_plural():
    assert lattice_core.normalize_spelling("As Ideias.", "pt-BR") == "As Idéias."


def test_normalize_spelling_leaves_areia_unaccented():
    # areia reads closed (Michaelis, ABL VOLP), so the step leaves it as written.
    assert lattice_core.normalize_spelling("areia", "pt-BR") == "areia"
    assert lattice_core.normalize_spelling("areias", "pt-BR") == "areias"


def test_guard_rejects_a_two_change_rewrite():
    # desacordo converts "sarigueia" to "sarigüéia": that is two changes, not one
    # e → é, so the guard leaves the word as written.
    assert lattice_core.normalize_spelling("sarigueia", "pt-BR") == "sarigueia"


def test_guard_rejects_a_change_that_is_not_e_to_acute():
    # desacordo converts "feiura" to "feiúra": the change is not e → é.
    assert lattice_core.normalize_spelling("feiura", "pt-BR") == "feiura"


@pytest.mark.parametrize("word, restored, expected", [
    ("ideia", "idéia", True),
    ("IDEIA", "IDÉIA", True),
    ("ideia", "ideia", False),
    ("sarigueia", "sarigüéia", False),
    ("feiura", "feiúra", False),
    ("ideia", "idéias", False),
    ("ideia", "idêia", False),
    ("ideia", "édeia", False),
])
def test_is_single_e_acute(word, restored, expected):
    assert lattice_core._is_single_e_acute(word, restored) is expected


def test_normalize_spelling_restores_the_accent_in_a_capital_plural():
    # The stem of "IDEIAS" converts to "IDÉIA"; the final S is reattached.
    assert lattice_core.normalize_spelling("IDEIAS", "pt-BR") == "IDÉIAS"


def test_token_count_stays():
    assert len(phonemize("a ideia nova", "pt-BR").split()) == 3
