from __future__ import annotations

from tts_tool.dialog.presets import DEFAULT_CHARACTERS_ZH, DEFAULT_CHARACTERS_EN, get_default_characters
from tts_tool.dialog.templates import DIALOG_TEMPLATES, get_template


class TestPresetsZh:
    def test_has_male(self):
        names = [c["name"] for c in DEFAULT_CHARACTERS_ZH]
        assert "男" in names

    def test_has_female(self):
        names = [c["name"] for c in DEFAULT_CHARACTERS_ZH]
        assert "女" in names

    def test_has_narrator(self):
        names = [c["name"] for c in DEFAULT_CHARACTERS_ZH]
        assert "旁白" in names

    def test_each_has_voice(self):
        for c in DEFAULT_CHARACTERS_ZH:
            assert "voice" in c
            assert c["voice"].startswith("zh-")

    def test_get_default_characters_zh(self):
        chars = get_default_characters("zh")
        assert len(chars) >= 3


class TestPresetsEn:
    def test_has_male(self):
        names = [c["name"] for c in DEFAULT_CHARACTERS_EN]
        assert "Male" in names

    def test_has_female(self):
        names = [c["name"] for c in DEFAULT_CHARACTERS_EN]
        assert "Female" in names

    def test_get_default_characters_en(self):
        chars = get_default_characters("en")
        assert len(chars) >= 2

    def test_get_default_characters_unknown(self):
        chars = get_default_characters("ja")
        assert chars == []


class TestTemplates:
    def test_templates_exist(self):
        assert len(DIALOG_TEMPLATES) >= 4

    def test_template_has_required_fields(self):
        for t in DIALOG_TEMPLATES:
            assert "id" in t
            assert "name" in t
            assert "characters" in t
            assert "sample_text" in t

    def test_get_template_by_id(self):
        t = get_template("dialog_mf")
        assert t is not None
        assert t["id"] == "dialog_mf"

    def test_get_template_not_found(self):
        assert get_template("nonexistent") is None

    def test_dialog_mf_has_two_characters(self):
        t = get_template("dialog_mf")
        assert len(t["characters"]) == 2

    def test_interview_has_three_characters(self):
        t = get_template("interview")
        assert len(t["characters"]) >= 3
