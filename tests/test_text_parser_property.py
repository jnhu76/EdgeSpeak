from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tts_tool.text_parser import TextParser


class TestTextParserPropertySplitParagraphs:
    @given(text=st.text(min_size=0, max_size=2000))
    @settings(max_examples=200)
    def test_rejoin_paragraphs_matches_original_stripped(self, text: str) -> None:
        paragraphs = TextParser.split_paragraphs(text)
        rejoined = "\n\n".join(paragraphs)
        assert (
            rejoined == text.strip()
            or rejoined == text.strip().replace("\n\n\n", "\n\n").strip()
        )

    @given(text=st.text(min_size=0, max_size=2000))
    @settings(max_examples=200)
    def test_no_empty_paragraphs(self, text: str) -> None:
        paragraphs = TextParser.split_paragraphs(text)
        for p in paragraphs:
            assert p.strip() != ""

    @given(text=st.text(min_size=0, max_size=500))
    @settings(max_examples=200)
    def test_paragraphs_are_substrings(self, text: str) -> None:
        paragraphs = TextParser.split_paragraphs(text)
        for p in paragraphs:
            assert p in text


class TestTextParserPropertySplitSentences:
    @given(
        text=st.text(
            min_size=1,
            max_size=1000,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Po", "Zs")),
        )
    )
    @settings(max_examples=200)
    def test_sentences_join_preserves_content(self, text: str) -> None:
        sentences = TextParser.split_sentences(text)
        if not sentences:
            return
        " ".join(sentences)
        for s in sentences:
            for word in s.split():
                if word.strip():
                    assert word in text

    @given(text=st.just(""))
    @settings(max_examples=5)
    def test_empty_string_returns_empty(self, text: str) -> None:
        result = TextParser.split_sentences(text)
        assert result == []

    @given(text=st.text(min_size=1, max_size=500))
    @settings(max_examples=200)
    def test_no_empty_sentences(self, text: str) -> None:
        sentences = TextParser.split_sentences(text)
        for s in sentences:
            assert s.strip() != ""


class TestTextParserPropertyPauseMarkers:
    @given(text=st.text(min_size=0, max_size=500))
    @settings(max_examples=200)
    def test_segments_cover_all_text(self, text: str) -> None:
        segments = TextParser.parse_pause_markers(text)
        reconstructed = "".join(
            s.get("content", "")
            if s["type"] == "text"
            else f"[pause:{s.get('duration', 0)}s]"
            for s in segments
        )
        assert (
            reconstructed == text
            or reconstructed.replace("[pause:", "").replace("s]", "") == text
        )

    @given(text=st.text(min_size=0, max_size=200))
    @settings(max_examples=100)
    def test_all_segments_have_type(self, text: str) -> None:
        segments = TextParser.parse_pause_markers(text)
        for seg in segments:
            assert "type" in seg
            assert seg["type"] in ("text", "pause")

    @given(
        duration=st.floats(
            min_value=0.1, max_value=30.0, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=100)
    def test_roundtrip_pause_duration(self, duration: float) -> None:
        text = f"Hello [pause:{duration}s] World"
        segments = TextParser.parse_pause_markers(text)
        pauses = [s for s in segments if s["type"] == "pause"]
        assert len(pauses) == 1
        assert abs(pauses[0]["duration"] - duration) < 0.01


class TestTextParserPropertyGetSegments:
    @given(
        text=st.text(
            min_size=1,
            max_size=300,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Po", "Zs")),
        ),
        sentence_pause=st.floats(min_value=0.0, max_value=5.0, allow_nan=False),
        paragraph_pause=st.floats(min_value=0.0, max_value=10.0, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_segments_always_has_at_least_one_item(
        self, text: str, sentence_pause: float, paragraph_pause: float
    ) -> None:
        segments = TextParser.get_segments(text, sentence_pause, paragraph_pause)
        assert len(segments) >= 1
        for seg in segments:
            assert seg["type"] in ("text", "pause")
