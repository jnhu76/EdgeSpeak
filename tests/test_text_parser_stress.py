from tts_tool.text_parser import TextParser


class TestTextParserStress:
    def test_long_text_10000_chars(self):
        text = "Hello world. " * 1000
        sentences = TextParser.split_sentences(text)
        assert len(sentences) > 0
        assert all(isinstance(s, str) for s in sentences)

    def test_deeply_nested_pause_markers(self):
        text = "Start " + "[pause:1.0s] segment " * 50
        segments = TextParser.parse_pause_markers(text)
        assert len(segments) > 50

    def test_mixed_chinese_english_large(self):
        text = "".join(f"这是第{i}句。This is sentence {i}. " for i in range(100))
        sentences = TextParser.split_sentences(text)
        assert len(sentences) >= 200

    def test_only_abbreviations(self):
        text = "Dr. Mr. Mrs. Ms. Prof. Sr. Jr. St. vs. etc."
        sentences = TextParser.split_sentences(text)
        assert len(sentences) == 1

    def test_only_chinese_punctuation(self):
        text = "第一句。第二句！第三句？第四句；最后一段。"
        sentences = TextParser.split_sentences(text)
        assert len(sentences) == 5

    def test_empty_paragraphs_many(self):
        text = "\n\n\n\n" + "Content" + "\n\n\n\n"
        paragraphs = TextParser.split_paragraphs(text)
        assert len(paragraphs) == 1

    def test_get_segments_with_both_pauses(self):
        text = "First sentence. Second sentence.\n\nNew paragraph."
        segments = TextParser.get_segments(text, sentence_pause=0.5, paragraph_pause=2.0)
        pause_segments = [s for s in segments if s["type"] == "pause"]
        text_segments = [s for s in segments if s["type"] == "text"]
        assert len(pause_segments) > 0
        assert len(text_segments) > 0

    def test_get_segments_no_pauses(self):
        text = "First. Second. Third."
        segments = TextParser.get_segments(text, 0.0, 0.0)
        assert len(segments) == 1
        assert segments[0]["type"] == "text"

    def test_insert_auto_pauses_no_double(self):
        text = "First.\n\nSecond."
        result = TextParser.insert_auto_pauses(text, sentence_pause=0.5, paragraph_pause=2.0)
        assert "[pause:0.5s][pause:2.0s]" not in result
        assert "[pause:2.0s][pause:0.5s]" not in result

    def test_unicode_text(self):
        text = "こんにちは世界。さようなら！"
        sentences = TextParser.split_sentences(text)
        assert len(sentences) >= 2

    def test_very_long_single_sentence(self):
        text = "A" * 100000 + "."
        sentences = TextParser.split_sentences(text)
        assert len(sentences) == 1
        assert len(sentences[0]) >= 100000

    def test_pause_marker_various_formats(self):
        text = "A[pause:0.1s]B[pause:1s]C[pause:10.5s]D"
        segments = TextParser.parse_pause_markers(text)
        pause_durations = [s["duration"] for s in segments if s["type"] == "pause"]
        assert 0.1 in pause_durations
        assert 1.0 in pause_durations
        assert 10.5 in pause_durations

    def test_rapid_parse_1000_times(self):
        text = "Hello world. How are you? I am fine. 这是一个测试。"
        for _ in range(1000):
            TextParser.get_segments(text, 0.5, 1.5)
