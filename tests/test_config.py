from tts_tool.config import AppConfig, SPEED_PRESETS, VoiceInfo


class TestSpeedPresets:
    def test_four_presets_exist(self):
        assert len(SPEED_PRESETS) == 4

    def test_preset_labels(self):
        assert set(SPEED_PRESETS.keys()) == {"0.5x", "1x", "1.5x", "2x"}

    def test_preset_values(self):
        assert SPEED_PRESETS["0.5x"] == -50
        assert SPEED_PRESETS["1x"] == 0
        assert SPEED_PRESETS["1.5x"] == 50
        assert SPEED_PRESETS["2x"] == 100

    def test_preset_rates_monotonic(self):
        values = list(SPEED_PRESETS.values())
        for i in range(len(values) - 1):
            assert values[i] < values[i + 1]

    def test_100_percent_is_zero(self):
        assert SPEED_PRESETS["1x"] == 0


class TestVoiceInfo:
    def test_display_name(self):
        v = VoiceInfo(
            short_name="en-US-AriaNeural",
            accent="en-US",
            gender="F",
            name="Aria",
            categories=["News", "Novel"],
        )
        assert v.display_name == "Aria (F)"

    def test_display_name_male(self):
        v = VoiceInfo(
            short_name="en-US-GuyNeural",
            accent="en-US",
            gender="M",
            name="Guy",
            categories=["News"],
        )
        assert v.display_name == "Guy (M)"

    def test_categories_string(self):
        v = VoiceInfo(
            short_name="en-US-AriaNeural",
            accent="en-US",
            gender="F",
            name="Aria",
            categories=["News", "Novel"],
        )
        assert v.categories_str == "News, Novel"


class TestAppConfig:
    def test_default_config(self):
        cfg = AppConfig()
        assert cfg.voice == "en-US-AriaNeural"
        assert cfg.rate == "+0%"
        assert cfg.pitch == "+0Hz"
        assert cfg.volume == "+0%"
        assert cfg.sentence_pause == 1.0
        assert cfg.paragraph_pause == 3.0
        assert cfg.language_filter == "en"

    def test_speed_preset_100(self):
        cfg = AppConfig()
        cfg.apply_speed_preset("1x")
        assert cfg.rate == "+0%"

    def test_speed_preset_50(self):
        cfg = AppConfig()
        cfg.apply_speed_preset("0.5x")
        assert cfg.rate == "-50%"

    def test_speed_preset_200(self):
        cfg = AppConfig()
        cfg.apply_speed_preset("2x")
        assert cfg.rate == "+100%"

    def test_to_dict(self):
        cfg = AppConfig()
        d = cfg.to_dict()
        assert d["voice"] == "en-US-AriaNeural"
        assert d["rate"] == "+0%"
        assert d["sentence_pause"] == 1.0
        assert d["language_filter"] == "en"
