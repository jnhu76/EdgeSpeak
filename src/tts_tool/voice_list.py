from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from tts_tool.tts_provider import TTSProvider


@dataclass
class AccentGroup:
    name: str
    count: int


class VoiceList:
    def __init__(self, provider: TTSProvider | None = None) -> None:
        from tts_tool.providers.edge_provider import EdgeTTSProvider

        self._provider = provider or EdgeTTSProvider()
        self.voices: list[dict] = []

    async def fetch(self, language_prefix: str = "") -> None:
        self.voices = await self._provider.list_voices(language_prefix)

    def get_accents(self) -> list[AccentGroup]:
        accent_counts: Counter[str] = Counter()
        for v in self.voices:
            short = v["ShortName"]
            parts = short.split("-")
            accent = f"{parts[0]}-{parts[1]}"
            accent_counts[accent] += 1
        groups = [
            AccentGroup(name=name, count=count) for name, count in accent_counts.items()
        ]
        return sorted(groups, key=lambda g: g.name, reverse=True)

    def get_language_prefixes(self) -> list[str]:
        prefixes: set[str] = set()
        for v in self.voices:
            short = v["ShortName"]
            parts = short.split("-")
            if len(parts) >= 2:
                prefixes.add(parts[0])
        return sorted(prefixes)

    def filter_by_accent(self, accent: str) -> list[dict]:
        return [v for v in self.voices if v["ShortName"].startswith(f"{accent}-")]

    def filter_by_language(self, prefix: str) -> list[dict]:
        if not prefix:
            return self.voices
        return [v for v in self.voices if v["ShortName"].startswith(f"{prefix}-")]

    @staticmethod
    def get_voice_display_info(voice: dict) -> dict:
        short_name = voice["ShortName"]
        gender = "F" if voice["Gender"] == "Female" else "M"
        name = (
            short_name.split("-")[-1].replace("Neural", "").replace("Multilingual", "")
        )
        categories = ", ".join(voice["VoiceTag"]["ContentCategories"])
        return {
            "short_name": short_name,
            "name": name,
            "gender": gender,
            "categories": categories,
        }
