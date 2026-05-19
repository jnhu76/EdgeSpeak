from tts_tool.subtitle import SrtEntry, generate_srt


class TestSrtEntry:
    def test_format_timestamp_zero(self):
        assert SrtEntry.format_timestamp(0) == "00:00:00,000"

    def test_format_timestamp_1_5s(self):
        assert SrtEntry.format_timestamp(1500) == "00:00:01,500"

    def test_format_timestamp_1h(self):
        assert SrtEntry.format_timestamp(3600000) == "01:00:00,000"

    def test_to_srt_block(self):
        entry = SrtEntry(index=1, start_ms=0, end_ms=2000, text="Hello.")
        block = entry.to_srt_block()
        lines = block.strip().split("\n")
        assert lines[0] == "1"
        assert "00:00:00,000 --> 00:00:02,000" in lines[1]
        assert lines[2] == "Hello."


class TestGenerateSrt:
    def test_empty_boundaries(self):
        result = generate_srt([])
        assert result == ""

    def test_single_sentence(self):
        boundaries = [
            {
                "type": "SentenceBoundary",
                "offset": 0,
                "duration": 5000000,
                "text": "Hello.",
            },
        ]
        result = generate_srt(boundaries)
        assert "1\n" in result
        assert "Hello." in result

    def test_multiple_sentences(self):
        boundaries = [
            {
                "type": "SentenceBoundary",
                "offset": 0,
                "duration": 5000000,
                "text": "Hello.",
            },
            {
                "type": "SentenceBoundary",
                "offset": 5000000,
                "duration": 5000000,
                "text": "World.",
            },
        ]
        result = generate_srt(boundaries)
        assert "Hello." in result
        assert "World." in result
        assert "1\n" in result
        assert "2\n" in result

    def test_offset_adjustment(self):
        boundaries = [
            {
                "type": "SentenceBoundary",
                "offset": 10000000,
                "duration": 5000000,
                "text": "Late.",
            },
        ]
        result = generate_srt(boundaries)
        assert "00:00:01,000" in result
