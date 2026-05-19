from __future__ import annotations

import edge_tts

from tts_tool.tts_provider import TTSProvider


class EdgeTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "edge-tts"

    @property
    def supported_languages(self) -> list[str]:
        return ["en", "zh", "ja", "ko", "fr", "de", "es", "pt", "it", "ru", "ar", "hi"]

    async def generate_segment(
        self,
        text: str,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> tuple[bytes, list[dict]]:
        communicate = edge_tts.Communicate(
            text, voice, rate=rate, pitch=pitch, volume=volume
        )
        audio_chunks: list[bytes] = []
        boundaries: list[dict] = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                boundaries.append(chunk)
        return b"".join(audio_chunks), boundaries

    async def list_voices(self, language_prefix: str = "") -> list[dict]:
        all_voices = await edge_tts.list_voices()
        if language_prefix:
            return [
                v
                for v in all_voices
                if v["ShortName"].startswith(f"{language_prefix}-")
            ]
        return all_voices
