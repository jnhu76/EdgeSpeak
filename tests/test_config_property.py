from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tts_tool.config import AppConfig, SPEED_PRESETS, VoiceInfo


class TestAppConfigProperty:
    @given(
        rate=st.sampled_from(["-50%", "-20%", "-10%", "+0%", "+10%", "+20%", "+50%", "+100%"]),
        pitch=st.sampled_from(["-50Hz", "-10Hz", "+0Hz", "+10Hz", "+50Hz"]),
        volume=st.sampled_from(["-50%", "-10%", "+0%", "+10%", "+50%"]),
    )
    @settings(max_examples=50)
    def test_to_dict_roundtrip(self, rate: str, pitch: str, volume: str) -> None:
        cfg = AppConfig(rate=rate, pitch=pitch, volume=volume)
        d = cfg.to_dict()
        cfg2 = AppConfig(**d)
        assert cfg2.rate == rate
        assert cfg2.pitch == pitch
        assert cfg2.volume == volume

    @given(label=st.sampled_from(list(SPEED_PRESETS.keys())))
    @settings(max_examples=10)
    def test_speed_preset_updates_rate(self, label: str) -> None:
        cfg = AppConfig()
        cfg.apply_speed_preset(label)
        expected = f"{SPEED_PRESETS[label]:+d}%"
        assert cfg.rate == expected

    @given(
        sentence_pause=st.floats(min_value=0.0, max_value=10.0, allow_nan=False),
        paragraph_pause=st.floats(min_value=0.0, max_value=30.0, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_pause_values_preserved(
        self, sentence_pause: float, paragraph_pause: float
    ) -> None:
        cfg = AppConfig(sentence_pause=sentence_pause, paragraph_pause=paragraph_pause)
        d = cfg.to_dict()
        assert abs(d["sentence_pause"] - sentence_pause) < 0.001
        assert abs(d["paragraph_pause"] - paragraph_pause) < 0.001


class TestVoiceInfoProperty:
    @given(
        name=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
        ),
        gender=st.sampled_from(["F", "M"]),
    )
    @settings(max_examples=50)
    def test_display_name_format(self, name: str, gender: str) -> None:
        v = VoiceInfo(
            short_name=f"en-US-{name}Neural",
            accent="en-US",
            gender=gender,
            name=name,
            categories=["General"],
        )
        assert v.display_name == f"{name} ({gender})"

    @given(
        categories=st.lists(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            ),
            min_size=0,
            max_size=5,
        ),
    )
    @settings(max_examples=50)
    def test_categories_str_joins(self, categories: list[str]) -> None:
        v = VoiceInfo(
            short_name="en-US-TestNeural",
            accent="en-US",
            gender="F",
            name="Test",
            categories=categories,
        )
        assert v.categories_str == ", ".join(categories)
