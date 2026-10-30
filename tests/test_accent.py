"""Accent-forcing: respelling, overlays, round-trip, CLI and plugin exposure."""
import json
import subprocess
import sys

import pytest

from tugaphone import (AccentOverlay, Transform, force_accent, list_dialects,
                       respell, respell_word)
from tugaphone.accent import DEFAULT_RESPELL_RULES, _levenshtein
from tugaphone.lattice_core import phonemize


# ---------------------------------------------------------------------------
# mode="ipa" is the lattice
# ---------------------------------------------------------------------------
def test_ipa_mode_is_lattice_transcription():
    assert force_accent("o vinho", "pt-BR", mode="ipa") == phonemize("o vinho", "pt-BR")


def test_bad_mode_raises():
    with pytest.raises(ValueError):
        force_accent("x", "pt-BR", mode="nonsense")


# ---------------------------------------------------------------------------
# respelling: concrete, well-known phenomena
# ---------------------------------------------------------------------------
def test_betacism_respells_v_to_b_for_northern():
    # Porto realises ⟨v⟩ as [b]; a pt-PT voice must be fed ⟨b⟩.
    assert respell_word("vinho", "pt-PT-x-porto", "pt-PT") == "binho"


def test_betacism_case_preserved():
    assert respell_word("Vinho", "pt-PT-x-porto", "pt-PT") == "Binho"


def test_brazilian_palatalisation_and_l_vocalisation():
    out = respell("a tia no Brasil", "pt-BR", "pt-PT")
    assert "tchia" in out          # [t]→[tʃ] before [i]
    assert "Brasiu" in out         # coda [ɫ]→[w]


def test_unrespellable_word_left_unchanged():
    # base already says it → identical spelling, never mangled.
    assert respell_word("gato", "pt-PT-x-lisbon", "pt-PT") == "gato"


def test_punctuation_and_spacing_preserved():
    out = respell("o vinho, sim!", "pt-PT-x-porto", "pt-PT")
    assert out == "o binho, sim!"


# ---------------------------------------------------------------------------
# the round-trip guarantee: respelling never makes the base voice worse
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("lect", ["pt-PT-x-porto", "pt-BR", "pt-AO",
                                  "pt-PT-x-braga"])
def test_respell_never_increases_distance_to_target(lect):
    sentence = "o vinho verde e a tia dele no Brasil"
    base = "pt-PT"
    target_ipa = phonemize(sentence, lect)
    d_orig = _levenshtein(phonemize(sentence, base), target_ipa)
    d_resp = _levenshtein(
        phonemize(respell(sentence, lect, base), base), target_ipa)
    assert d_resp <= d_orig


def test_respell_strictly_helps_a_betacism_lect():
    sentence = "o vinho da vinha"
    base = "pt-PT"
    lect = "pt-PT-x-porto"
    target_ipa = phonemize(sentence, lect)
    d_orig = _levenshtein(phonemize(sentence, base), target_ipa)
    d_resp = _levenshtein(
        phonemize(respell(sentence, lect, base), base), target_ipa)
    assert d_resp < d_orig


# ---------------------------------------------------------------------------
# user-space overlay: application order + JSON round-trip
# ---------------------------------------------------------------------------
def test_overlay_applies_ipa_stage_only_in_ipa_mode():
    overlay = AccentOverlay(transforms=[
        Transform(kind="regex", pattern="ʀ", replacement="ɾ", stage="ipa"),
        Transform(kind="regex", pattern="XXX", replacement="!", stage="text"),
    ])
    out = force_accent("o carro", "pt-PT", mode="ipa", overlay=overlay)
    assert "ʀ" not in out           # ipa-stage transform fired
    assert "ɾ" in out


def test_overlay_text_stage_in_respell_mode():
    overlay = AccentOverlay(transforms=[
        Transform(kind="word", pattern="binho", replacement="BINHO",
                  stage="text"),
    ])
    out = force_accent("o vinho", "pt-PT-x-porto", mode="respell",
                       overlay=overlay)
    assert "BINHO" in out


def test_overlay_transforms_apply_in_order():
    overlay = AccentOverlay(transforms=[
        Transform(kind="regex", pattern="a", replacement="b", stage="ipa"),
        Transform(kind="regex", pattern="b", replacement="c", stage="ipa"),
    ])
    assert overlay.apply("a", "ipa") == "c"


def test_overlay_json_round_trip():
    overlay = AccentOverlay(
        name="voice-1",
        transforms=[
            Transform(kind="regex", pattern="ʀ", replacement="h", stage="ipa"),
            Transform(kind="word", pattern="lh", replacement="j", stage="text",
                      ignore_case=False),
        ],
    )
    restored = AccentOverlay.from_json(overlay.to_json())
    assert restored.to_dict() == overlay.to_dict()
    assert json.loads(overlay.to_json())["name"] == "voice-1"


# ---------------------------------------------------------------------------
# rule table sanity
# ---------------------------------------------------------------------------
def test_rules_have_unique_names():
    names = [r.name for r in DEFAULT_RESPELL_RULES]
    assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# plugin exposure
# ---------------------------------------------------------------------------
def test_plugin_force_accent_defaults_base_to_plugin_lang():
    from tugaphone.plugin import TugaphoneG2PPlugin

    plugin = TugaphoneG2PPlugin(lang="pt-PT")
    assert plugin.force_accent("o vinho", "pt-PT-x-porto", mode="respell") \
        == respell("o vinho", "pt-PT-x-porto", "pt-PT")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "tugaphone", *args],
        capture_output=True, text=True,
    )


def test_cli_force_accent_respell():
    r = _cli("force-accent", "o vinho", "--lect", "pt-PT-x-porto",
             "--mode", "respell")
    assert r.returncode == 0, r.stderr
    assert "binho" in r.stdout


def test_cli_phonemize():
    r = _cli("phonemize", "o gato", "--lect", "pt-BR")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()


def test_cli_list_has_all_dialects():
    r = _cli("list")
    assert r.returncode == 0, r.stderr
    assert len(r.stdout.strip().splitlines()) == len(list_dialects())


def test_cli_force_accent_with_overlay(tmp_path):
    overlay = AccentOverlay(transforms=[
        Transform(kind="word", pattern="binho", replacement="BINHO",
                  stage="text")])
    p = tmp_path / "ov.json"
    p.write_text(overlay.to_json(), encoding="utf-8")
    r = _cli("force-accent", "o vinho", "--lect", "pt-PT-x-porto",
             "--mode", "respell", "--overlay", str(p))
    assert r.returncode == 0, r.stderr
    assert "BINHO" in r.stdout
