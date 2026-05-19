from __future__ import annotations

from tts_tool.dialog.models import DialogCharacter, DialogScript, DialogTurn


class TestDialogCharacter:
    def test_create_defaults(self):
        c = DialogCharacter(name="男", voice="zh-CN-YunxiNeural")
        assert c.name == "男"
        assert c.voice == "zh-CN-YunxiNeural"
        assert c.rate == "+0%"
        assert c.pitch == "+0Hz"
        assert c.volume == "+0%"
        assert c.color == "#4f46e5"

    def test_create_custom_params(self):
        c = DialogCharacter(
            name="女",
            voice="zh-CN-XiaoxiaoNeural",
            rate="+10%",
            pitch="+5Hz",
            volume="-10%",
            color="#dc2626",
        )
        assert c.rate == "+10%"
        assert c.pitch == "+5Hz"
        assert c.volume == "-10%"
        assert c.color == "#dc2626"

    def test_to_dict(self):
        c = DialogCharacter(name="男", voice="zh-CN-YunxiNeural")
        d = c.to_dict()
        assert d["name"] == "男"
        assert d["voice"] == "zh-CN-YunxiNeural"
        assert "rate" in d
        assert "color" in d

    def test_from_dict(self):
        d = {"name": "女", "voice": "zh-CN-XiaoxiaoNeural", "rate": "+5%", "pitch": "+3Hz", "volume": "+0%", "color": "#dc2626"}
        c = DialogCharacter.from_dict(d)
        assert c.name == "女"
        assert c.rate == "+5%"
        assert c.color == "#dc2626"


class TestDialogTurn:
    def test_create_basic(self):
        t = DialogTurn(speaker="男", text="你好")
        assert t.speaker == "男"
        assert t.text == "你好"
        assert t.paragraph_pause == 0.0

    def test_create_with_pause(self):
        t = DialogTurn(speaker="女", text="谢谢", paragraph_pause=2.0)
        assert t.paragraph_pause == 2.0

    def test_text_not_empty(self):
        t = DialogTurn(speaker="男", text="")
        assert t.text == ""


class TestDialogScript:
    def test_create_empty(self):
        s = DialogScript()
        assert s.characters == []
        assert s.turns == []
        assert s.inter_turn_pause == 0.8
        assert s.paragraph_pause == 2.0

    def test_create_with_data(self):
        chars = [
            DialogCharacter(name="男", voice="zh-CN-YunxiNeural"),
            DialogCharacter(name="女", voice="zh-CN-XiaoxiaoNeural"),
        ]
        turns = [
            DialogTurn(speaker="男", text="你好"),
            DialogTurn(speaker="女", text="你好啊"),
        ]
        s = DialogScript(characters=chars, turns=turns, inter_turn_pause=1.0)
        assert len(s.characters) == 2
        assert len(s.turns) == 2
        assert s.inter_turn_pause == 1.0

    def test_get_character_by_name(self):
        chars = [
            DialogCharacter(name="男", voice="zh-CN-YunxiNeural"),
            DialogCharacter(name="女", voice="zh-CN-XiaoxiaoNeural"),
        ]
        s = DialogScript(characters=chars)
        found = s.get_character("女")
        assert found is not None
        assert found.voice == "zh-CN-XiaoxiaoNeural"

    def test_get_character_not_found(self):
        s = DialogScript()
        assert s.get_character("不存在") is None

    def test_add_character(self):
        s = DialogScript()
        c = DialogCharacter(name="旁白", voice="zh-CN-YunyangNeural")
        s.add_character(c)
        assert len(s.characters) == 1
        assert s.characters[0].name == "旁白"

    def test_add_turn(self):
        s = DialogScript()
        s.add_turn("男", "你好")
        assert len(s.turns) == 1
        assert s.turns[0].speaker == "男"
        assert s.turns[0].text == "你好"

    def test_add_turn_with_pause(self):
        s = DialogScript()
        s.add_turn("男", "你好", paragraph_pause=1.5)
        assert s.turns[0].paragraph_pause == 1.5

    def test_speaker_names(self):
        chars = [
            DialogCharacter(name="男", voice="a"),
            DialogCharacter(name="女", voice="b"),
        ]
        turns = [
            DialogTurn(speaker="男", text="hi"),
            DialogTurn(speaker="女", text="hello"),
            DialogTurn(speaker="男", text="bye"),
        ]
        s = DialogScript(characters=chars, turns=turns)
        names = s.speaker_names()
        assert "男" in names
        assert "女" in names

    def test_turn_count(self):
        s = DialogScript()
        s.add_turn("A", "1")
        s.add_turn("B", "2")
        s.add_turn("A", "3")
        assert s.turn_count() == 3
