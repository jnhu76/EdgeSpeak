from tts_tool.config import AppConfig, SPEED_PRESETS, VoiceInfo


class TestSpeedPresetCompleteness:
    def test_four_presets_exist(self):
        assert len(SPEED_PRESETS) == 4

    def test_preset_labels(self):
        assert set(SPEED_PRESETS.keys()) == {"0.5x", "1x", "1.5x", "2x"}

    def test_preset_values_are_monotonic(self):
        values = list(SPEED_PRESETS.values())
        for i in range(len(values) - 1):
            assert values[i] < values[i + 1], f"{values[i]} not < {values[i + 1]}"

    def test_100_is_zero(self):
        assert SPEED_PRESETS["1x"] == 0


class TestAppConfigStress:
    def test_apply_all_presets_sequentially(self):
        cfg = AppConfig()
        for label, value in SPEED_PRESETS.items():
            cfg.apply_speed_preset(label)
            assert cfg.rate == f"{value:+d}%"

    def test_apply_same_preset_repeatedly(self):
        cfg = AppConfig()
        for _ in range(100):
            cfg.apply_speed_preset("1.5x")
            assert cfg.rate == "+50%"

    def test_to_dict_after_many_mutations(self):
        cfg = AppConfig()
        for label in SPEED_PRESETS:
            cfg.apply_speed_preset(label)
        d = cfg.to_dict()
        assert d["rate"] == "+100%"

    def test_frozen_voice_info(self):
        v = VoiceInfo(
            short_name="en-US-AriaNeural",
            accent="en-US",
            gender="F",
            name="Aria",
        )
        for _ in range(100):
            assert v.display_name == "Aria (F)"
            assert v.categories_str == ""

    def test_voice_info_with_categories(self):
        v = VoiceInfo(
            short_name="en-US-AriaNeural",
            accent="en-US",
            gender="F",
            name="Aria",
            categories=["News", "Novel", "Conversation"],
        )
        assert "News" in v.categories_str
        assert "Novel" in v.categories_str
