from unittest.mock import AsyncMock, patch

import pytest

from tts_tool.voice_list import VoiceList


class TestVoiceList:
    @pytest.mark.asyncio
    async def test_fetch_english_voices_only(self):
        mock_voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["News"],
                    "VoicePersonalities": ["Confident"],
                },
            },
            {
                "ShortName": "en-GB-SoniaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": ["Friendly"],
                },
            },
            {
                "ShortName": "zh-CN-XiaoxiaoNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
            {
                "ShortName": "fr-FR-DeniseNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
        ]
        with patch(
            "tts_tool.providers.edge_provider.edge_tts.list_voices",
            new_callable=AsyncMock,
            return_value=mock_voices,
        ):
            vl = VoiceList()
            await vl.fetch("en")
            assert len(vl.voices) == 2
            assert all(v["ShortName"].startswith("en-") for v in vl.voices)

    @pytest.mark.asyncio
    async def test_fetch_all_voices(self):
        mock_voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["News"],
                    "VoicePersonalities": [],
                },
            },
            {
                "ShortName": "zh-CN-XiaoxiaoNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
        ]
        with patch(
            "tts_tool.providers.edge_provider.edge_tts.list_voices",
            new_callable=AsyncMock,
            return_value=mock_voices,
        ):
            vl = VoiceList()
            await vl.fetch()
            assert len(vl.voices) == 2

    @pytest.mark.asyncio
    async def test_fetch_empty(self):
        with patch(
            "tts_tool.providers.edge_provider.edge_tts.list_voices",
            new_callable=AsyncMock,
            return_value=[],
        ):
            vl = VoiceList()
            await vl.fetch()
            assert vl.voices == []

    def test_get_accents(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
            {
                "ShortName": "en-US-GuyNeural",
                "Gender": "Male",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
            {
                "ShortName": "en-GB-SoniaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
        ]
        accents = vl.get_accents()
        assert len(accents) == 2
        us = [a for a in accents if a.name == "en-US"][0]
        assert us.count == 2
        gb = [a for a in accents if a.name == "en-GB"][0]
        assert gb.count == 1

    def test_get_accents_sorted(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-GB-SoniaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
        ]
        accents = vl.get_accents()
        assert accents[0].name == "en-US"

    def test_filter_by_accent(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
            {
                "ShortName": "en-US-GuyNeural",
                "Gender": "Male",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
            {
                "ShortName": "en-GB-SoniaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
        ]
        result = vl.filter_by_accent("en-US")
        assert len(result) == 2
        assert all(v["ShortName"].startswith("en-US") for v in result)

    def test_filter_by_accent_no_match(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
        ]
        result = vl.filter_by_accent("en-AU")
        assert result == []

    def test_filter_by_language(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
            {
                "ShortName": "zh-CN-XiaoxiaoNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
        ]
        result = vl.filter_by_language("zh")
        assert len(result) == 1
        assert result[0]["ShortName"] == "zh-CN-XiaoxiaoNeural"

    def test_filter_by_language_empty_returns_all(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
            {
                "ShortName": "zh-CN-XiaoxiaoNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
        ]
        result = vl.filter_by_language("")
        assert len(result) == 2

    def test_get_language_prefixes(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {"ContentCategories": ["News"], "VoicePersonalities": []},
            },
            {
                "ShortName": "zh-CN-XiaoxiaoNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
            {
                "ShortName": "en-GB-SoniaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["General"],
                    "VoicePersonalities": [],
                },
            },
        ]
        prefixes = vl.get_language_prefixes()
        assert prefixes == ["en", "zh"]

    def test_get_voice_display_info(self):
        vl = VoiceList()
        vl.voices = [
            {
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "VoiceTag": {
                    "ContentCategories": ["News", "Novel"],
                    "VoicePersonalities": ["Confident"],
                },
            },
        ]
        info = vl.get_voice_display_info(vl.voices[0])
        assert info["name"] == "Aria"
        assert info["gender"] == "F"
        assert info["categories"] == "News, Novel"
        assert info["short_name"] == "en-US-AriaNeural"
