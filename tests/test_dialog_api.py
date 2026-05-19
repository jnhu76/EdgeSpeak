from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tts_tool.gui.api import Api
from tts_tool.tts_engine import MP3_BITRATE, TTSEngine


@pytest.fixture
def api() -> Api:
    a = Api()
    a._window = MagicMock()
    a._all_voices = [
        {"ShortName": "zh-CN-YunxiNeural", "Gender": "Male"},
        {"ShortName": "zh-CN-XiaoxiaoNeural", "Gender": "Female"},
    ]
    a._voices_loaded.set()
    return a


class TestParseDialogText:
    def test_parse_simple_dialog(self, api: Api) -> None:
        text = "[男] 你好\n[女] 你好"
        result = api.parse_dialog_text(text)
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert len(parsed["turns"]) == 2
        assert parsed["turns"][0]["speaker"] == "男"
        assert parsed["turns"][0]["text"] == "你好"

    def test_parse_with_character_block(self, api: Api) -> None:
        text = "---characters---\n男: zh-CN-YunxiNeural\n---end---\n[男] 测试"
        result = api.parse_dialog_text(text)
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert len(parsed["characters"]) == 1
        assert parsed["characters"][0]["name"] == "男"

    def test_parse_empty_text(self, api: Api) -> None:
        result = api.parse_dialog_text("")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert len(parsed["turns"]) == 0

    def test_parse_returns_inter_turn_pause(self, api: Api) -> None:
        result = api.parse_dialog_text("[男] 你好")
        parsed = json.loads(result)
        assert "inter_turn_pause" in parsed
        assert "paragraph_pause" in parsed


class TestGetDialogTemplates:
    def test_returns_list(self, api: Api) -> None:
        templates = api.get_dialog_templates()
        assert isinstance(templates, list)
        assert len(templates) >= 4

    def test_template_has_required_fields(self, api: Api) -> None:
        templates = api.get_dialog_templates()
        for t in templates:
            assert "id" in t
            assert "name" in t
            assert "characters" in t
            assert "sample_text" in t


class TestGenerateDialog:
    def _mock_generate_segment(self) -> AsyncMock:
        async def _generate(content, voice, rate, pitch, volume):
            fake_audio = b"\xff\xfb" + b"\x00" * 200
            fake_boundaries = [
                {"text": content[:5], "offset": 0, "duration": 5000000},
            ]
            return fake_audio, fake_boundaries

        return _generate

    def test_generate_two_turns(self, api: Api) -> None:
        text = "[男] 你好\n[女] 谢谢"
        characters = [
            {"name": "男", "voice": "zh-CN-YunxiNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
            {"name": "女", "voice": "zh-CN-XiaoxiaoNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
        ]

        with patch.object(api._engine, "generate_full", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = (
                b"\xff\xfb" + b"\x00" * 200,
                [{"text": "你好", "offset": 0, "duration": 5000000}],
            )
            mock_gen.return_value = (
                b"\xff\xfb" + b"\x01" * 200,
                [{"text": "谢谢", "offset": 0, "duration": 5000000}],
            )

            side_effects = [
                (
                    b"\xff\xfb" + b"\x00" * 200,
                    [{"text": "你好", "offset": 0, "duration": 5000000}],
                ),
                (
                    b"\xff\xfb" + b"\x01" * 200,
                    [{"text": "谢谢", "offset": 0, "duration": 5000000}],
                ),
            ]
            mock_gen.side_effect = side_effects

            result_str = api.generate_dialog(text, characters, inter_pause_s=0.5, paragraph_pause_s=2.0)
            result = json.loads(result_str)

        assert result["success"] is True
        assert "audio_b64" in result
        assert "duration" in result
        assert "boundaries" in result
        assert result["turn_count"] == 2

    def test_generate_single_turn(self, api: Api) -> None:
        text = "[男] 测试一下"
        characters = [
            {"name": "男", "voice": "zh-CN-YunxiNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
        ]

        with patch.object(api._engine, "generate_full", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = (
                b"\xff\xfb" + b"\x00" * 200,
                [{"text": "测试一下", "offset": 0, "duration": 5000000}],
            )

            result_str = api.generate_dialog(text, characters, inter_pause_s=0.8, paragraph_pause_s=2.0)
            result = json.loads(result_str)

        assert result["success"] is True
        assert result["turn_count"] == 1

    def test_generate_empty_text(self, api: Api) -> None:
        result_str = api.generate_dialog("", [], inter_pause_s=0.8, paragraph_pause_s=2.0)
        result = json.loads(result_str)
        assert "error" in result

    def test_generate_unknown_speaker(self, api: Api) -> None:
        text = "[男] 你好"
        characters = []

        result_str = api.generate_dialog(text, characters, inter_pause_s=0.8, paragraph_pause_s=2.0)
        result = json.loads(result_str)
        assert "error" in result

    def test_generate_adds_to_history(self, api: Api) -> None:
        text = "[男] 你好"
        characters = [
            {"name": "男", "voice": "zh-CN-YunxiNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
        ]

        with patch.object(api._engine, "generate_full", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = (
                b"\xff\xfb" + b"\x00" * 200,
                [{"text": "你好", "offset": 0, "duration": 5000000}],
            )

            api.generate_dialog(text, characters, inter_pause_s=0.8, paragraph_pause_s=2.0)

        assert len(api._history) == 1
        assert api._history[0]["type"] == "dialog"

    def test_generate_with_paragraph_pause(self, api: Api) -> None:
        text = "[男] 第一段\n\n[男] 第二段"
        characters = [
            {"name": "男", "voice": "zh-CN-YunxiNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
        ]

        with patch.object(api._engine, "generate_full", new_callable=AsyncMock) as mock_gen:
            side_effects = [
                (b"\xff\xfb" + b"\x00" * 200, [{"text": "第一段", "offset": 0, "duration": 5000000}]),
                (b"\xff\xfb" + b"\x01" * 200, [{"text": "第二段", "offset": 0, "duration": 5000000}]),
            ]
            mock_gen.side_effect = side_effects

            result_str = api.generate_dialog(text, characters, inter_pause_s=0.5, paragraph_pause_s=2.0)
            result = json.loads(result_str)

        assert result["success"] is True
        assert result["turn_count"] == 2
