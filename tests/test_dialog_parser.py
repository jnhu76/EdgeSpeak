from __future__ import annotations

import pytest

from tts_tool.dialog.models import DialogCharacter
from tts_tool.dialog.parser import DialogParser


class TestDialogParserBasic:
    def test_single_turn(self):
        result = DialogParser.parse("[男] 你好")
        assert len(result.turns) == 1
        assert result.turns[0].speaker == "男"
        assert result.turns[0].text == "你好"

    def test_multiple_turns(self):
        text = "[男] 你好\n[女] 你好啊\n[男] 吃了吗？"
        result = DialogParser.parse(text)
        assert len(result.turns) == 3
        assert result.turns[0].speaker == "男"
        assert result.turns[1].speaker == "女"
        assert result.turns[2].speaker == "男"

    def test_inherit_previous_speaker(self):
        text = "[男] 你好\n最近怎么样？"
        result = DialogParser.parse(text)
        assert len(result.turns) == 2
        assert result.turns[0].speaker == "男"
        assert result.turns[1].speaker == "男"

    def test_empty_lines_create_pause(self):
        text = "[男] 你好\n\n[女] 你好啊"
        result = DialogParser.parse(text)
        assert len(result.turns) == 2
        assert result.turns[1].paragraph_pause > 0

    def test_pause_marker(self):
        text = "[男] 你好[pause:1.5s]世界"
        result = DialogParser.parse(text)
        assert len(result.turns) == 1
        assert "[pause:1.5s]" in result.turns[0].text


class TestDialogParserCharacterBlock:
    def test_parse_character_block(self):
        text = "---characters---\n男: zh-CN-YunxiNeural, rate=+0%, pitch=+0Hz\n女: zh-CN-XiaoxiaoNeural, rate=+0%, pitch=+5Hz\n---end---\n[男] 你好\n[女] 你好"
        result = DialogParser.parse(text)
        assert len(result.characters) == 2
        assert result.characters[0].name == "男"
        assert result.characters[0].voice == "zh-CN-YunxiNeural"
        assert result.characters[1].pitch == "+5Hz"

    def test_no_character_block(self):
        text = "[男] 你好"
        result = DialogParser.parse(text)
        assert len(result.characters) == 0

    def test_character_block_with_volume(self):
        text = "---characters---\nA: voice1, volume=+20%\n---end---\n[A] hi"
        result = DialogParser.parse(text)
        assert result.characters[0].volume == "+20%"


class TestDialogParserEdgeCases:
    def test_empty_input(self):
        result = DialogParser.parse("")
        assert len(result.turns) == 0

    def test_whitespace_only(self):
        result = DialogParser.parse("   \n   \n")
        assert len(result.turns) == 0

    def test_no_speaker_tag_first_line(self):
        result = DialogParser.parse("你好世界")
        assert len(result.turns) == 1
        assert result.turns[0].speaker == ""
        assert result.turns[0].text == "你好世界"

    def test_multiple_empty_lines(self):
        text = "[男] 第一句\n\n\n\n[女] 第二句"
        result = DialogParser.parse(text)
        assert len(result.turns) == 2
        assert result.turns[1].paragraph_pause > 0

    def test_tag_with_spaces(self):
        result = DialogParser.parse("[ 旁白 ] 他说。")
        assert len(result.turns) == 1
        assert result.turns[0].speaker == "旁白"

    def test_tag_at_line_start_only(self):
        result = DialogParser.parse("这是[男]嵌套的标签")
        assert len(result.turns) == 1
        assert result.turns[0].text == "这是[男]嵌套的标签"
        assert result.turns[0].speaker == ""

    def test_custom_inter_turn_pause(self):
        text = "[男] 你好\n[女] 嗯嗯"
        result = DialogParser.parse(text, inter_turn_pause=1.5)
        assert result.inter_turn_pause == 1.5

    def test_custom_paragraph_pause(self):
        text = "[男] 你好\n\n[女] 嗯"
        result = DialogParser.parse(text, paragraph_pause=3.0)
        assert result.paragraph_pause == 3.0

    def test_speaker_tag_with_brackets_in_text(self):
        result = DialogParser.parse("[男] 数组[1,2,3]是这样的")
        assert result.turns[0].text == "数组[1,2,3]是这样的"
        assert result.turns[0].speaker == "男"
