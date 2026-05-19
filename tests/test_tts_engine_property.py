from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tts_tool.tts_engine import TTSEngine


class TestValidateParamProperty:
    @given(value=st.text(min_size=1, max_size=20))
    @settings(max_examples=200)
    def test_valid_rate_only_accepts_pattern(self, value: str) -> None:
        import re

        expected_valid = bool(re.match(r"^[+-]\d+%$", value))
        try:
            TTSEngine.validate_param(value, "rate")
            assert expected_valid, f"Should have rejected: {value}"
        except ValueError:
            assert not expected_valid, f"Should have accepted: {value}"

    @given(value=st.text(min_size=1, max_size=20))
    @settings(max_examples=200)
    def test_valid_pitch_only_accepts_pattern(self, value: str) -> None:
        import re

        expected_valid = bool(re.match(r"^[+-]\d+Hz$", value))
        try:
            TTSEngine.validate_param(value, "pitch")
            assert expected_valid
        except ValueError:
            assert not expected_valid

    @given(value=st.text(min_size=1, max_size=20))
    @settings(max_examples=200)
    def test_valid_volume_only_accepts_pattern(self, value: str) -> None:
        import re

        expected_valid = bool(re.match(r"^[+-]\d+%$", value))
        try:
            TTSEngine.validate_param(value, "volume")
            assert expected_valid
        except ValueError:
            assert not expected_valid


class TestGenerateSilenceProperty:
    @given(
        duration=st.floats(
            min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=100)
    def test_silence_length_proportional_to_duration(self, duration: float) -> None:
        result = TTSEngine.generate_silence_ms(duration)
        assert len(result) > 0
        assert isinstance(result, bytes)

    @given(
        duration=st.floats(
            min_value=0.5, max_value=10.0, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=50)
    def test_double_duration_more_bytes(self, duration: float) -> None:
        short = TTSEngine.generate_silence_ms(duration)
        long = TTSEngine.generate_silence_ms(duration * 2)
        assert len(long) >= len(short)
