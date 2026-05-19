from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tts_tool.subtitle import SrtEntry, generate_srt


class TestSrtEntryProperty:
    @given(ms=st.integers(min_value=0, max_value=86_400_000))
    @settings(max_examples=200)
    def test_format_timestamp_always_valid(self, ms: int) -> None:
        ts = SrtEntry.format_timestamp(ms)
        assert len(ts) == 12
        assert ts[2] == ":"
        assert ts[5] == ":"
        assert ts[8] == ","
        h, m, s, frac = int(ts[0:2]), int(ts[3:5]), int(ts[6:8]), int(ts[9:12])
        total_ms = h * 3600000 + m * 60000 + s * 1000 + frac
        assert total_ms == ms

    @given(
        start=st.integers(min_value=0, max_value=3_600_000),
        duration=st.integers(min_value=1, max_value=60_000),
    )
    @settings(max_examples=100)
    def test_end_always_after_start(self, start: int, duration: int) -> None:
        entry = SrtEntry(index=1, start_ms=start, end_ms=start + duration, text="Test.")
        entry.to_srt_block()
        assert start + duration >= start


class TestGenerateSrtProperty:
    @given(
        offsets=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=60_000_000),
                st.integers(min_value=100_000, max_value=10_000_000),
                st.text(
                    min_size=1,
                    max_size=100,
                    alphabet=st.characters(
                        whitelist_categories=("Lu", "Ll", "Po", "Zs")
                    ),
                ),
            ),
            min_size=1,
            max_size=20,
        )
    )
    @settings(max_examples=100)
    def test_output_always_has_index_for_each_entry(
        self, offsets: list[tuple[int, int, str]]
    ) -> None:
        boundaries = [
            {"type": "SentenceBoundary", "offset": o, "duration": d, "text": t}
            for o, d, t in offsets
        ]
        result = generate_srt(boundaries)
        for i in range(1, len(offsets) + 1):
            assert f"{i}\n" in result

    @given(
        offsets=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=60_000_000),
                st.integers(min_value=100_000, max_value=10_000_000),
                st.text(
                    min_size=1,
                    max_size=50,
                    alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
                ),
            ),
            min_size=1,
            max_size=10,
        )
    )
    @settings(max_examples=50)
    def test_each_text_appears_in_output(
        self, offsets: list[tuple[int, int, str]]
    ) -> None:
        boundaries = [
            {"type": "SentenceBoundary", "offset": o, "duration": d, "text": t}
            for o, d, t in offsets
        ]
        result = generate_srt(boundaries)
        for _, _, t in offsets:
            assert t in result
