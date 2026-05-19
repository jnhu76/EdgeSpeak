from tts_tool.voice_list import VoiceList
from tts_tool.tts_provider import TTSProvider


class _MockProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "mock"

    @property
    def supported_languages(self) -> list[str]:
        return ["en", "zh", "ja"]

    async def generate_segment(self, text: str, voice: str, rate: str = "+0%", pitch: str = "+0Hz", volume: str = "+0%") -> tuple[bytes, list[dict]]:
        return b"", []

    async def list_voices(self, language_prefix: str = "") -> list[dict]:
        voices = [
            {"ShortName": "en-US-AriaNeural", "Gender": "Female", "VoiceTag": {"ContentCategories": ["News"]}},
            {"ShortName": "en-US-GuyNeural", "Gender": "Male", "VoiceTag": {"ContentCategories": ["News"]}},
            {"ShortName": "en-GB-SoniaNeural", "Gender": "Female", "VoiceTag": {"ContentCategories": ["Conversation"]}},
            {"ShortName": "zh-CN-XiaoxiaoNeural", "Gender": "Female", "VoiceTag": {"ContentCategories": ["Novel"]}},
            {"ShortName": "zh-CN-YunxiNeural", "Gender": "Male", "VoiceTag": {"ContentCategories": ["Novel"]}},
            {"ShortName": "ja-JP-NanamiNeural", "Gender": "Female", "VoiceTag": {"ContentCategories": ["News"]}},
        ]
        if language_prefix:
            return [v for v in voices if v["ShortName"].startswith(f"{language_prefix}-")]
        return voices


class TestVoiceListStress:
    def test_filter_empty_returns_all(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        result = vl.filter_by_language("")
        assert len(result) == 6

    def test_filter_by_language_en(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch("en"))
        result = vl.filter_by_language("en")
        assert len(result) == 3

    def test_filter_by_accent_en_us(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        result = vl.filter_by_accent("en-US")
        assert len(result) == 2

    def test_filter_by_accent_no_match(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        result = vl.filter_by_accent("fr-FR")
        assert result == []

    def test_get_language_prefixes(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        prefixes = vl.get_language_prefixes()
        assert prefixes == ["en", "ja", "zh"]

    def test_get_accents_sorted(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        accents = vl.get_accents()
        names = [a.name for a in accents]
        assert names == sorted(names, reverse=True)

    def test_display_info(self):
        voice = {"ShortName": "en-US-AriaNeural", "Gender": "Female", "VoiceTag": {"ContentCategories": ["News", "Novel"]}}
        info = VoiceList.get_voice_display_info(voice)
        assert info["name"] == "Aria"
        assert info["gender"] == "F"
        assert "News" in info["categories"]

    def test_display_info_male(self):
        voice = {"ShortName": "en-US-GuyNeural", "Gender": "Male", "VoiceTag": {"ContentCategories": ["News"]}}
        info = VoiceList.get_voice_display_info(voice)
        assert info["gender"] == "M"

    def test_refetch_replaces_voices(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        assert len(vl.voices) == 6
        asyncio.get_event_loop().run_until_complete(vl.fetch("zh"))
        assert len(vl.voices) == 2

    def test_rapid_filter_switching(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        for _ in range(200):
            vl.filter_by_accent("en-US")
            vl.filter_by_accent("zh-CN")
            vl.filter_by_language("en")
            vl.filter_by_language("")


class TestVoiceListProperty:
    def test_accent_counts_sum_to_total(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        total = sum(a.count for a in vl.get_accents())
        assert total == len(vl.voices)

    def test_filter_by_accent_subset_of_all(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        accents = vl.get_accents()
        for accent in accents:
            filtered = vl.filter_by_accent(accent.name)
            assert len(filtered) == accent.count
            for v in filtered:
                assert v["ShortName"].startswith(accent.name)

    def test_language_prefix_covers_all_voices(self):
        vl = VoiceList(provider=_MockProvider())
        import asyncio
        asyncio.get_event_loop().run_until_complete(vl.fetch())
        prefixes = vl.get_language_prefixes()
        for v in vl.voices:
            prefix = v["ShortName"].split("-")[0]
            assert prefix in prefixes
