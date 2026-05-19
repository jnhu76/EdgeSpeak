import asyncio
import threading

import pytest

from tts_tool.tts_engine import TTSEngine, GenerationCancelled
from tts_tool.tts_provider import TTSProvider


class _SlowMockProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "slow-mock"

    @property
    def supported_languages(self) -> list[str]:
        return ["en"]

    async def generate_segment(self, text: str, voice: str, rate: str = "+0%", pitch: str = "+0Hz", volume: str = "+0%") -> tuple[bytes, list[dict]]:
        await asyncio.sleep(0.1)
        return b"\xff\xfb\x90\x00" * 100, [{"text": text, "offset": 0, "duration": 100000}]

    async def list_voices(self, language_prefix: str = "") -> list[dict]:
        return []


class _InstantMockProvider(TTSProvider):
    call_count: int = 0

    @property
    def name(self) -> str:
        return "instant-mock"

    @property
    def supported_languages(self) -> list[str]:
        return ["en"]

    async def generate_segment(self, text: str, voice: str, rate: str = "+0%", pitch: str = "+0Hz", volume: str = "+0%") -> tuple[bytes, list[dict]]:
        _InstantMockProvider.call_count += 1
        return b"\xff\xfb\x90\x00" * 100, [{"text": text, "offset": 0, "duration": 100000}]

    async def list_voices(self, language_prefix: str = "") -> list[dict]:
        return []


class TestCancelToken:
    def test_cancel_before_generate_raises(self):
        engine = TTSEngine(provider=_InstantMockProvider())
        cancel = threading.Event()
        cancel.set()
        segments = [{"type": "text", "content": "Hello"}]
        with pytest.raises(GenerationCancelled):
            asyncio.get_event_loop().run_until_complete(
                engine.generate_full(segments, "voice", cancel_token=cancel)
            )

    def test_no_cancel_completes_normally(self):
        _InstantMockProvider.call_count = 0
        engine = TTSEngine(provider=_InstantMockProvider())
        cancel = threading.Event()
        segments = [{"type": "text", "content": "Hello world."}]
        audio, boundaries = asyncio.get_event_loop().run_until_complete(
            engine.generate_full(segments, "voice", cancel_token=cancel)
        )
        assert len(audio) > 0
        assert len(boundaries) > 0
        assert _InstantMockProvider.call_count == 1

    def test_cancel_during_multi_segment_stops_early(self):
        _InstantMockProvider.call_count = 0
        engine = TTSEngine(provider=_SlowMockProvider())
        cancel = threading.Event()

        segments = [
            {"type": "text", "content": "First segment"},
            {"type": "text", "content": "Second segment"},
            {"type": "text", "content": "Third segment"},
        ]

        async def run():
            task = asyncio.ensure_future(
                engine.generate_full(segments, "voice", cancel_token=cancel)
            )
            await asyncio.sleep(0.15)
            cancel.set()
            with pytest.raises(GenerationCancelled):
                await task

        asyncio.get_event_loop().run_until_complete(run())

    def test_cancel_token_none_completes_normally(self):
        _InstantMockProvider.call_count = 0
        engine = TTSEngine(provider=_InstantMockProvider())
        segments = [{"type": "text", "content": "Hello"}]
        audio, boundaries = asyncio.get_event_loop().run_until_complete(
            engine.generate_full(segments, "voice")
        )
        assert len(audio) > 0

    def test_cancel_after_pause_segment(self):
        engine = TTSEngine(provider=_SlowMockProvider())
        cancel = threading.Event()

        segments = [
            {"type": "text", "content": "Before pause"},
            {"type": "pause", "duration": 1.0},
            {"type": "text", "content": "After pause"},
        ]

        async def run():
            task = asyncio.ensure_future(
                engine.generate_full(segments, "voice", cancel_token=cancel)
            )
            await asyncio.sleep(0.15)
            cancel.set()
            with pytest.raises(GenerationCancelled):
                await task

        asyncio.get_event_loop().run_until_complete(run())

    def test_cancel_between_segments(self):
        engine = TTSEngine(provider=_SlowMockProvider())
        cancel = threading.Event()

        segments = [
            {"type": "text", "content": "A"},
            {"type": "text", "content": "B"},
        ]

        async def run():
            task = asyncio.ensure_future(
                engine.generate_full(segments, "voice", cancel_token=cancel)
            )
            await asyncio.sleep(0.15)
            cancel.set()
            with pytest.raises(GenerationCancelled):
                await task

        asyncio.get_event_loop().run_until_complete(run())

    def test_cancel_preserves_none_token_default(self):
        engine = TTSEngine(provider=_InstantMockProvider())
        segments = [{"type": "text", "content": "test"}]
        audio, _ = asyncio.get_event_loop().run_until_complete(
            engine.generate_full(segments, "voice", cancel_token=None)
        )
        assert len(audio) > 0

    def test_multiple_generations_different_tokens(self):
        _InstantMockProvider.call_count = 0
        engine = TTSEngine(provider=_InstantMockProvider())
        segments = [{"type": "text", "content": "test"}]

        cancel1 = threading.Event()
        audio1, _ = asyncio.get_event_loop().run_until_complete(
            engine.generate_full(segments, "voice", cancel_token=cancel1)
        )
        assert len(audio1) > 0

        cancel2 = threading.Event()
        audio2, _ = asyncio.get_event_loop().run_until_complete(
            engine.generate_full(segments, "voice", cancel_token=cancel2)
        )
        assert len(audio2) > 0
