from __future__ import annotations

import asyncio
import re
import tempfile
from pathlib import Path

from tts_tool.tts_provider import TTSProvider


class SapiTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "sapi"

    @property
    def supported_languages(self) -> list[str]:
        return ["en", "zh", "ja", "ko", "fr", "ru", "es", "de", "pt", "it"]

    async def generate_segment(
        self,
        text: str,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> tuple[bytes, list[dict]]:
        import pythoncom

        pythoncom.CoInitialize()
        try:
            return await asyncio.to_thread(
                self._sync_generate, text, voice, rate, pitch, volume
            )
        finally:
            pythoncom.CoUninitialize()

    def _sync_generate(
        self,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
    ) -> tuple[bytes, list[dict]]:
        import winspeech

        sapi_rate = self._parse_rate(rate)
        sapi_volume = self._parse_volume(volume)

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()

        speaker = winspeech.SpeechSynthesizer()
        voices = speaker.get_voices()
        for v in voices:
            if voice.lower() in v.Id.lower() or voice.lower() in v.Name.lower():
                speaker.voice = v
                break

        speaker.rate = sapi_rate
        speaker.volume = sapi_volume
        speaker.speak_to_wave(tmp_path, text)

        wav_data = Path(tmp_path).read_bytes()
        Path(tmp_path).unlink(missing_ok=True)

        mp3_data = self._wav_to_mp3_bytes(wav_data)
        boundaries = [{"offset": 0, "duration": 0, "text": text}]

        return mp3_data, boundaries

    async def list_voices(self, language_prefix: str = "") -> list[dict]:
        return await asyncio.to_thread(self._sync_list_voices, language_prefix)

    def _sync_list_voices(self, language_prefix: str = "") -> list[dict]:
        import pythoncom

        pythoncom.CoInitialize()
        try:
            import winspeech

            speaker = winspeech.SpeechSynthesizer()
            voices = []
            for v in speaker.get_voices():
                lang_code = self._extract_lang(v.Id)
                if language_prefix and not lang_code.startswith(language_prefix):
                    continue
                short_name = v.Id.split("\\")[-1] if "\\" in v.Id else v.Name
                voices.append({
                    "ShortName": short_name,
                    "Gender": "Female" if "female" in v.Gender.lower() else "Male",
                    "VoiceTag": {"ContentCategories": []},
                })
            return voices
        finally:
            pythoncom.CoUninitialize()

    @staticmethod
    def _extract_lang(voice_id: str) -> str:
        match = re.search(r"(\w{2}-\w{2})", voice_id)
        return match.group(1) if match else ""

    @staticmethod
    def _parse_rate(rate: str) -> int:
        m = re.match(r"([+-]?\d+)%", rate)
        return int(m.group(1)) // 10 if m else 0

    @staticmethod
    def _parse_volume(volume: str) -> int:
        m = re.match(r"([+-]?\d+)%", volume)
        if not m:
            return 100
        val = 100 + int(m.group(1))
        return max(0, min(100, val))

    @staticmethod
    def _wav_to_mp3_bytes(wav_data: bytes) -> bytes:
        try:
            import subprocess

            result = subprocess.run(
                ["ffmpeg", "-y", "-f", "wav", "-i", "pipe:0", "-f", "mp3", "pipe:1"],
                input=wav_data,
                capture_output=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except Exception:
            pass
        return wav_data
