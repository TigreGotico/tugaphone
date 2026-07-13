"""Tests for tugaphone.plugin public API."""
import pytest
from tugaphone.plugin import TugaphoneG2PPlugin, SilabificadorSyllabifier

_LANGS = ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]


class TestTugaphoneG2PPlugin:
    def test_language_codes(self):
        p = TugaphoneG2PPlugin()
        assert set(_LANGS).issubset(set(p.language_codes))

    def test_transcribe_returns_string(self):
        p = TugaphoneG2PPlugin(lang="pt-PT")
        result = p.transcribe("o gato dorme")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_transcribe_pt_pt(self):
        p = TugaphoneG2PPlugin(lang="pt-PT")
        result = p.transcribe("o gato dorme")
        assert "ˈ" in result  # has stress marker

    def test_transcribe_pt_br(self):
        p = TugaphoneG2PPlugin(lang="pt-BR")
        result = p.transcribe("o gato dorme")
        assert isinstance(result, str)

    def test_transcribe_word(self):
        p = TugaphoneG2PPlugin(lang="pt-PT")
        result = p.transcribe_word("gato")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_lazy_engine_not_loaded_on_init(self):
        p = TugaphoneG2PPlugin(lang="pt-PT")
        assert p._phonemizer is None

    def test_engine_loads_on_first_transcribe(self):
        p = TugaphoneG2PPlugin(lang="pt-PT")
        p.transcribe("gato")
        assert p._phonemizer is not None


class TestSilabificadorSyllabifier:
    def test_language_codes(self):
        s = SilabificadorSyllabifier()
        assert "pt-PT" in s.language_codes
        assert "pt-BR" in s.language_codes

    def test_syllabify_returns_list(self):
        s = SilabificadorSyllabifier()
        result = s.syllabify("fonologia")
        assert isinstance(result, list)
        assert len(result) > 1

    def test_syllabify_gato(self):
        s = SilabificadorSyllabifier()
        result = s.syllabify("gato")
        assert result == ["ga", "to"]

    def test_syllabify_with_lang(self):
        s = SilabificadorSyllabifier()
        result = s.syllabify("comboio", lang="pt-PT")
        assert isinstance(result, list)
        assert len(result) >= 1
