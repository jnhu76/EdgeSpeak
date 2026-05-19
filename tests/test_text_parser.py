from tts_tool.text_parser import TextParser


class TestSplitParagraphs:
    def test_splits_on_double_newline(self):
        text = "First paragraph.\n\nSecond paragraph."
        result = TextParser.split_paragraphs(text)
        assert result == ["First paragraph.", "Second paragraph."]

    def test_removes_empty_paragraphs(self):
        text = "Para one.\n\n\n\nPara two."
        result = TextParser.split_paragraphs(text)
        assert result == ["Para one.", "Para two."]

    def test_single_paragraph(self):
        text = "Just one paragraph."
        result = TextParser.split_paragraphs(text)
        assert result == ["Just one paragraph."]


class TestSplitSentences:
    def test_splits_on_period(self):
        text = "Hello world. Goodbye world."
        result = TextParser.split_sentences(text)
        assert result == ["Hello world.", "Goodbye world."]

    def test_handles_question_and_exclamation(self):
        text = "Really? Yes! OK."
        result = TextParser.split_sentences(text)
        assert result == ["Really?", "Yes!", "OK."]

    def test_does_not_split_abbreviations(self):
        text = "Dr. Smith went to Washington."
        result = TextParser.split_sentences(text)
        assert result == ["Dr. Smith went to Washington."]

    def test_empty_string(self):
        result = TextParser.split_sentences("")
        assert result == []

    def test_chinese_period(self):
        text = "你好世界。再见世界。"
        result = TextParser.split_sentences(text)
        assert result == ["你好世界。", "再见世界。"]

    def test_chinese_exclamation(self):
        text = "太好了！真的吗？"
        result = TextParser.split_sentences(text)
        assert result == ["太好了！", "真的吗？"]

    def test_chinese_semicolon(self):
        text = "第一句；第二句。"
        result = TextParser.split_sentences(text)
        assert result == ["第一句；", "第二句。"]

    def test_mixed_chinese_english(self):
        text = "Hello world. 你好世界。Goodbye."
        result = TextParser.split_sentences(text)
        assert "Hello world." in result
        assert "你好世界。" in result


class TestParsePauseMarkers:
    def test_extracts_pause_marker(self):
        text = "Hello. [pause:2s] Goodbye."
        result = TextParser.parse_pause_markers(text)
        assert result == [
            {"type": "text", "content": "Hello. "},
            {"type": "pause", "duration": 2.0},
            {"type": "text", "content": " Goodbye."},
        ]

    def test_no_markers(self):
        text = "Just plain text."
        result = TextParser.parse_pause_markers(text)
        assert result == [{"type": "text", "content": "Just plain text."}]

    def test_multiple_markers(self):
        text = "A [pause:1.5s] B [pause:3s] C"
        result = TextParser.parse_pause_markers(text)
        assert len([r for r in result if r["type"] == "pause"]) == 2

    def test_invalid_marker_ignored(self):
        text = "Hello [pause:abc] world."
        result = TextParser.parse_pause_markers(text)
        assert result == [{"type": "text", "content": "Hello [pause:abc] world."}]


class TestInsertAutoPauses:
    def test_inserts_sentence_pauses(self):
        text = "Hello. Goodbye."
        result = TextParser.insert_auto_pauses(
            text, sentence_pause=1.0, paragraph_pause=0.0
        )
        assert "[pause:1.0s]" in result

    def test_inserts_paragraph_pauses(self):
        text = "Para one.\n\nPara two."
        result = TextParser.insert_auto_pauses(
            text, sentence_pause=0.0, paragraph_pause=3.0
        )
        assert "[pause:3.0s]" in result

    def test_no_double_pauses(self):
        text = "Hello [pause:2s]. Goodbye."
        result = TextParser.insert_auto_pauses(
            text, sentence_pause=1.0, paragraph_pause=0.0
        )
        assert result.count("[pause:2s]") == 1


class TestGetSegments:
    def test_returns_text_and_pause_segments(self):
        text = "Hello. [pause:2s] Goodbye."
        result = TextParser.get_segments(text)
        assert len(result) == 3
        assert result[0]["type"] == "text"
        assert result[1]["type"] == "pause"
        assert result[2]["type"] == "text"

    def test_with_auto_pauses(self):
        text = "Hello. Goodbye."
        result = TextParser.get_segments(text, sentence_pause=1.0, paragraph_pause=3.0)
        assert any(s["type"] == "pause" for s in result)
