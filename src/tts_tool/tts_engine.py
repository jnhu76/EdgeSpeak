from __future__ import annotations

import threading
from dataclasses import dataclass

from tts_tool.providers.edge_provider import EdgeTTSProvider
from tts_tool.tts_provider import TTSProvider


class GenerationCancelled(Exception):
    pass


@dataclass
class GenerationResult:
    success: bool
    audio_data: bytes | None = None
    duration_s: float | None = None
    error: str | None = None
    boundaries: list | None = None


TICKS_PER_MS = 10000
MP3_BITRATE = 48000
MP3_FRAME_SIZE = 144 * MP3_BITRATE // 24000
MP3_SILENCE_HEADER = bytes([0xFF, 0x53, 0xC4, 0x00])


class TTSEngine:
    def __init__(self, provider: TTSProvider | None = None) -> None:
        self._provider = provider or EdgeTTSProvider()

    @property
    def provider(self) -> TTSProvider:
        return self._provider

    @staticmethod
    def validate_param(value: str, param: str) -> str:
        return TTSProvider.validate_param(value, param)

    @staticmethod
    def generate_silence_ms(duration_s: float) -> bytes:
        bytes_per_sec = MP3_BITRATE // 8
        num_bytes = int(duration_s * bytes_per_sec)
        frame_size = MP3_FRAME_SIZE
        if frame_size <= 0:
            return b""
        silence_frame = MP3_SILENCE_HEADER + b"\x00" * (frame_size - len(MP3_SILENCE_HEADER))
        frames = max(num_bytes // frame_size, 1) if duration_s > 0 else 0
        return silence_frame * frames

    async def generate_full(
        self,
        segments: list[dict],
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
        cancel_token: threading.Event | None = None,
    ) -> tuple[bytes, list[dict]]:
        all_audio: list[bytes] = []
        all_boundaries: list[dict] = []
        offset_ticks = 0

        for seg in segments:
            if cancel_token is not None and cancel_token.is_set():
                raise GenerationCancelled()
            if seg["type"] == "pause":
                duration = seg.get("duration", 1.0)
                silence = TTSEngine.generate_silence_ms(duration)
                all_audio.append(silence)
                silence_ticks = int(duration * 1000 * TICKS_PER_MS)
                offset_ticks += silence_ticks
            elif seg["type"] == "text":
                content = seg.get("content", "")
                if not content.strip():
                    continue
                audio, boundaries = await self._provider.generate_segment(
                    content, voice, rate, pitch, volume
                )
                if cancel_token is not None and cancel_token.is_set():
                    raise GenerationCancelled()
                all_audio.append(audio)
                for b in boundaries:
                    adjusted = dict(b)
                    adjusted["offset"] = b["offset"] + offset_ticks
                    all_boundaries.append(adjusted)
                audio_ticks = len(audio) * 8 * TICKS_PER_MS * 1000 // MP3_BITRATE
                offset_ticks += audio_ticks

        return b"".join(all_audio), all_boundaries
