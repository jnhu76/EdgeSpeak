import pytest
from tts_tool.tts_engine import TTSEngine, GenerationResult


class TestValidateParam:
    def test_valid_rate(self):
        assert TTSEngine.validate_param("+0%", "rate") == "+0%"
        assert TTSEngine.validate_param("-10%", "rate") == "-10%"
        assert TTSEngine.validate_param("+50%", "rate") == "+50%"

    def test_invalid_rate(self):
        with pytest.raises(ValueError):
            TTSEngine.validate_param("0%", "rate")
        with pytest.raises(ValueError):
            TTSEngine.validate_param("abc", "rate")

    def test_valid_pitch(self):
        assert TTSEngine.validate_param("+0Hz", "pitch") == "+0Hz"
        assert TTSEngine.validate_param("-5Hz", "pitch") == "-5Hz"

    def test_invalid_pitch(self):
        with pytest.raises(ValueError):
            TTSEngine.validate_param("+0%", "pitch")

    def test_valid_volume(self):
        assert TTSEngine.validate_param("+0%", "volume") == "+0%"

    def test_invalid_volume(self):
        with pytest.raises(ValueError):
            TTSEngine.validate_param("loud", "volume")

    def test_unknown_param(self):
        with pytest.raises(ValueError):
            TTSEngine.validate_param("+0%", "unknown")


class TestGenerationResult:
    def test_success_result(self):
        result = GenerationResult(success=True, audio_data=b"fake", duration_s=10.5)
        assert result.success
        assert result.duration_s == 10.5
        assert result.error is None

    def test_error_result(self):
        result = GenerationResult(success=False, error="Network error")
        assert not result.success
        assert result.error == "Network error"
        assert result.audio_data is None


class TestGenerateSilence:
    def test_silence_bytes_positive_duration(self):
        result = TTSEngine.generate_silence_ms(1.0)
        assert len(result) > 0
        assert isinstance(result, bytes)

    def test_silence_bytes_zero_duration(self):
        result = TTSEngine.generate_silence_ms(0.0)
        assert isinstance(result, bytes)

    def test_longer_silence_more_bytes(self):
        short = TTSEngine.generate_silence_ms(1.0)
        long = TTSEngine.generate_silence_ms(2.0)
        assert len(long) > len(short)
