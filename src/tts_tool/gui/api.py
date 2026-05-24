from __future__ import annotations

import asyncio
import base64
import json
import tempfile
import threading
from datetime import datetime
from pathlib import Path

import webview
from webview import FileDialog

from tts_tool.config import SPEED_PRESETS
from tts_tool.dialog.merger import DialogMerger
from tts_tool.dialog.parser import DialogParser
from tts_tool.dialog.templates import DIALOG_TEMPLATES
from tts_tool.i18n import SUPPORTED_LOCALES, get_locale, set_locale
from tts_tool.subtitle import generate_srt
from tts_tool.text_parser import TextParser
from tts_tool.tts_engine import MP3_BITRATE, TTSEngine, GenerationCancelled
from tts_tool.voice_list import VoiceList

ALLOWED_LANGUAGES = {"en", "zh", "ja", "ko", "fr", "ru", "es"}

LANGUAGE_DISPLAY: dict[str, str] = {
    "en": "English",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "ru": "Русский",
    "es": "Español",
}


class Api:
    def __init__(self) -> None:
        self._engine = TTSEngine()
        self._voice_list = VoiceList()
        self._all_voices: list[dict] = []
        self._voices: list[dict] = []
        self._generated_audio: bytes | None = None
        self._boundaries: list | None = None
        self._cancel_event = threading.Event()
        self._cancel_loop: asyncio.AbstractEventLoop | None = None
        self._cancel_task: asyncio.Task | None = None
        self._window: webview.Window | None = None
        self._voices_loaded = threading.Event()
        self._current_provider = "edge"
        self._history: list[dict] = []
        self._history_counter = 0

    def set_window(self, window: webview.Window) -> None:
        self._window = window

    def set_provider(self, provider: str) -> None:
        if provider == self._current_provider:
            return
        self._current_provider = provider
        if provider == "sapi":
            try:
                from tts_tool.providers.sapi_provider import SapiTTSProvider

                self._engine = TTSEngine(provider=SapiTTSProvider())
                self._voice_list = VoiceList(provider=SapiTTSProvider())
            except Exception:
                self._current_provider = "edge"
                self._engine = TTSEngine()
                self._voice_list = VoiceList()
        else:
            self._engine = TTSEngine()
            self._voice_list = VoiceList()
        self._voices_loaded.clear()
        self._voices = []

    def get_locale(self) -> str:
        return get_locale()

    def set_locale(self, code: str) -> None:
        set_locale(code)

    def get_speed_presets(self) -> dict[str, int]:
        return SPEED_PRESETS

    def get_locales(self) -> list[dict]:
        return [{"code": loc.code, "name": loc.name} for loc in SUPPORTED_LOCALES]

    def get_ui_strings(self) -> dict:
        locale = get_locale()
        from tts_tool.i18n import _STRINGS_DB

        return _STRINGS_DB.get(locale, {})

    def init_voices(self) -> None:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self._voice_list.fetch())
        except Exception:
            pass
        finally:
            loop.close()
        self._all_voices = list(self._voice_list.voices)
        self._voices_loaded.set()

    def get_languages(self) -> list[dict]:
        self._voices_loaded.wait(timeout=10)
        prefixes: set[str] = set()
        for v in self._all_voices:
            parts = v["ShortName"].split("-")
            if len(parts) >= 2 and parts[0] in ALLOWED_LANGUAGES:
                prefixes.add(parts[0])
        result = []
        for p in sorted(prefixes):
            result.append({"code": p, "name": f"{p} - {LANGUAGE_DISPLAY.get(p, p.upper())}"})
        return result

    def get_accents(self, language: str = "") -> list[dict]:
        self._voices_loaded.wait(timeout=10)
        from collections import Counter

        accent_counts: Counter[str] = Counter()
        for v in self._all_voices:
            sn = v["ShortName"]
            parts = sn.split("-")
            if len(parts) < 2:
                continue
            accent = f"{parts[0]}-{parts[1]}"
            if language and not accent.startswith(language):
                continue
            accent_counts[accent] += 1
        groups = sorted(accent_counts.items(), key=lambda x: x[0], reverse=True)
        return [{"name": name, "count": count} for name, count in groups]

    def get_voices(self, accent: str = "") -> list[dict]:
        self._voices_loaded.wait(timeout=10)
        if accent:
            voices = [v for v in self._all_voices if v["ShortName"].startswith(f"{accent}-")]
        else:
            voices = list(self._all_voices)
        self._voices = voices
        result = []
        for v in voices:
            info = VoiceList.get_voice_display_info(v)
            result.append(info)
        return result

    def generate(
        self,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
        sentence_pause: float = 0.0,
        paragraph_pause: float = 0.0,
    ) -> str:
        segments = TextParser.get_segments(text, sentence_pause, paragraph_pause)
        self._cancel_event = threading.Event()
        cancel = self._cancel_event

        result_holder: dict = {}

        def worker() -> None:
            loop = asyncio.new_event_loop()
            self._cancel_loop = loop
            coro = self._engine.generate_full(
                segments, voice, rate, pitch, volume, cancel_token=cancel
            )
            task = loop.create_task(coro)
            self._cancel_task = task
            try:
                audio_data, boundaries = loop.run_until_complete(task)
                result_holder["audio"] = audio_data
                result_holder["boundaries"] = boundaries
            except (GenerationCancelled, asyncio.CancelledError):
                result_holder["error"] = "cancelled"
            except Exception as e:
                result_holder["error"] = str(e)
            finally:
                loop.close()
                self._cancel_loop = None
                self._cancel_task = None

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        t.join()

        if "error" in result_holder:
            return json.dumps({"error": result_holder["error"]})

        audio_data = result_holder["audio"]
        boundaries = result_holder["boundaries"]
        self._generated_audio = audio_data
        self._boundaries = boundaries

        self._temp_path = str(Path(tempfile.gettempdir()) / "tts_tool_temp.mp3")
        with open(self._temp_path, "wb") as f:
            f.write(audio_data)

        duration = self._compute_duration(self._temp_path)
        audio_b64 = base64.b64encode(audio_data).decode("ascii")

        self._history_counter += 1
        item = {
            "id": self._history_counter,
            "voice": voice,
            "rate": rate,
            "pitch": pitch,
            "volume": volume,
            "duration": duration,
            "audio_b64": audio_b64,
            "boundaries": boundaries,
            "text_preview": text[:60] + ("..." if len(text) > 60 else ""),
            "created_at": datetime.now().strftime("%H:%M:%S"),
        }
        self._history.append(item)

        return json.dumps({
            "success": True,
            "duration": duration,
            "audio_b64": audio_b64,
            "boundaries": boundaries,
            "history_id": self._history_counter,
        })

    def generate_preview(
        self, text: str, voice: str, rate: str, pitch: str, volume: str
    ) -> str:
        return self.generate(text, voice, rate, pitch, volume, 0.0, 0.0)

    def cancel_generation(self) -> None:
        self._cancel_event.set()
        if self._cancel_task is not None and self._cancel_loop is not None:
            self._cancel_loop.call_soon_threadsafe(self._cancel_task.cancel)

    def _compute_duration(self, file_path: str) -> float:
        try:
            import pygame
            sound = pygame.mixer.Sound(file_path)
            return sound.get_length()
        except Exception:
            try:
                file_size = Path(file_path).stat().st_size
                return file_size * 8 / MP3_BITRATE
            except Exception:
                return 0.0

    def save_mp3(self) -> str | None:
        if not self._generated_audio:
            return None
        result = self._window.create_file_dialog(
            FileDialog.SAVE,
            save_filename="output.mp3",
            file_types=("Audio Files (*.mp3)", "All Files (*.*)"),
        )
        if result and len(result) > 0:
            path = result[0]
            with open(path, "wb") as f:
                f.write(self._generated_audio)
            return path
        return None

    def save_srt(self) -> str | None:
        if not self._boundaries:
            return None
        result = self._window.create_file_dialog(
            FileDialog.SAVE,
            save_filename="output.srt",
            file_types=("Subtitle Files (*.srt)", "All Files (*.*)"),
        )
        if result and len(result) > 0:
            path = result[0]
            srt_content = generate_srt(self._boundaries)
            with open(path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            return path
        return None

    def get_history(self) -> list[dict]:
        result = []
        for h in self._history:
            item = {
                "id": h["id"],
                "type": h.get("type", "single"),
                "voice": h["voice"],
                "rate": h["rate"],
                "pitch": h["pitch"],
                "volume": h["volume"],
                "duration": h["duration"],
                "text_preview": h["text_preview"],
                "created_at": h["created_at"],
            }
            if h.get("type") == "dialog":
                item["turn_count"] = h.get("turn_count", 0)
                item["characters"] = h.get("characters", [])
            result.append(item)
        return result

    def play_history_item(self, history_id: int) -> str:
        for h in self._history:
            if h["id"] == history_id:
                self._generated_audio = base64.b64decode(h["audio_b64"])
                self._boundaries = h["boundaries"]
                return json.dumps({
                    "audio_b64": h["audio_b64"],
                    "duration": h["duration"],
                })
        return json.dumps({"error": "not_found"})

    def save_history_mp3(self, history_id: int) -> str | None:
        item = None
        for h in self._history:
            if h["id"] == history_id:
                item = h
                break
        if not item:
            return None
        audio_data = base64.b64decode(item["audio_b64"])
        result = self._window.create_file_dialog(
            FileDialog.SAVE,
            save_filename=f"tts_{history_id}.mp3",
            file_types=("Audio Files (*.mp3)", "All Files (*.*)"),
        )
        if result and len(result) > 0:
            path = result[0]
            with open(path, "wb") as f:
                f.write(audio_data)
            return path
        return None

    def save_history_srt(self, history_id: int) -> str | None:
        item = None
        for h in self._history:
            if h["id"] == history_id:
                item = h
                break
        if not item or not item["boundaries"]:
            return None
        result = self._window.create_file_dialog(
            FileDialog.SAVE,
            save_filename=f"tts_{history_id}.srt",
            file_types=("Subtitle Files (*.srt)", "All Files (*.*)"),
        )
        if result and len(result) > 0:
            path = result[0]
            srt_content = generate_srt(item["boundaries"])
            with open(path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            return path
        return None

    def delete_history_item(self, history_id: int) -> None:
        self._history = [h for h in self._history if h["id"] != history_id]

    def clear_history(self) -> None:
        self._history = []
        self._history_counter = 0

    def import_file(self) -> str | None:
        result = self._window.create_file_dialog(
            FileDialog.OPEN,
            file_types=("Text Files (*.txt)", "All Files (*.*)"),
        )
        if result and len(result) > 0:
            with open(result[0], "r", encoding="utf-8") as f:
                return f.read()
        return None

    def parse_dialog_text(self, text: str) -> str:
        script = DialogParser.parse(text)
        characters = [c.to_dict() for c in script.characters]
        turns = [
            {
                "speaker": t.speaker,
                "text": t.text,
                "paragraph_pause": t.paragraph_pause,
            }
            for t in script.turns
        ]
        return json.dumps({
            "success": True,
            "characters": characters,
            "turns": turns,
            "inter_turn_pause": script.inter_turn_pause,
            "paragraph_pause": script.paragraph_pause,
        })

    def get_dialog_templates(self) -> list[dict]:
        return DIALOG_TEMPLATES

    def generate_dialog(
        self,
        text: str,
        characters: list[dict],
        inter_pause_s: float = 0.8,
        paragraph_pause_s: float = 2.0,
    ) -> str:
        script = DialogParser.parse(text, inter_pause_s, paragraph_pause_s)

        if not script.turns:
            return json.dumps({"error": "no_turns"})

        for c in characters:
            if "name" not in c or "voice" not in c:
                return json.dumps({"error": "invalid_character_definition"})

        names = [c["name"] for c in characters]
        if len(names) != len(set(names)):
            return json.dumps({"error": "duplicate_character_name"})

        char_map: dict[str, dict] = {c["name"]: c for c in characters}

        for turn in script.turns:
            if turn.speaker not in char_map:
                return json.dumps({"error": f"unknown_speaker:{turn.speaker}"})

        turn_audios: list[bytes] = []
        turn_boundaries: list[list[dict]] = []
        turn_durations: list[float] = []
        turn_speakers: list[str] = []
        paragraph_after_indices: list[int] = []

        self._cancel_event = threading.Event()
        cancel = self._cancel_event
        result_holder: dict = {}

        def worker() -> None:
            loop = asyncio.new_event_loop()
            self._cancel_loop = loop
            try:
                for i, turn in enumerate(script.turns):
                    if cancel.is_set():
                        result_holder["error"] = "cancelled"
                        return

                    char = char_map[turn.speaker]
                    segments = [{"type": "text", "content": turn.text}]

                    coro = self._engine.generate_full(
                        segments,
                        char["voice"],
                        char.get("rate", "+0%"),
                        char.get("pitch", "+0Hz"),
                        char.get("volume", "+0%"),
                        cancel_token=cancel,
                    )
                    task = loop.create_task(coro)
                    self._cancel_task = task
                    audio_data, boundaries = loop.run_until_complete(task)
                    self._cancel_task = None

                    turn_audios.append(audio_data)
                    turn_boundaries.append(boundaries)
                    turn_speakers.append(turn.speaker)

                    duration = DialogMerger.compute_duration(audio_data, MP3_BITRATE)
                    turn_durations.append(duration)

                    if turn.paragraph_pause > 0 and i < len(script.turns) - 1:
                        paragraph_after_indices.append(i)

            except (GenerationCancelled, asyncio.CancelledError):
                result_holder["error"] = "cancelled"
            except Exception as e:
                result_holder["error"] = str(e)
            finally:
                loop.close()
                self._cancel_loop = None

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        t.join()

        if "error" in result_holder:
            return json.dumps({"error": result_holder["error"]})

        combined_audio = DialogMerger.concat_clips(
            turn_audios,
            inter_pause_s=inter_pause_s,
            paragraph_pause_s=paragraph_pause_s,
            paragraph_after_indices=paragraph_after_indices,
        )

        merged_boundaries = DialogMerger.merge_boundaries(
            turn_boundaries,
            durations=turn_durations,
            inter_pause_s=inter_pause_s,
            speakers=turn_speakers,
        )

        total_duration = DialogMerger.compute_duration(combined_audio, MP3_BITRATE)
        audio_b64 = base64.b64encode(combined_audio).decode("ascii")

        self._generated_audio = combined_audio
        self._boundaries = merged_boundaries

        self._history_counter += 1
        item = {
            "id": self._history_counter,
            "type": "dialog",
            "voice": characters[0]["voice"] if characters else "",
            "rate": characters[0].get("rate", "+0%") if characters else "+0%",
            "pitch": characters[0].get("pitch", "+0Hz") if characters else "+0Hz",
            "volume": characters[0].get("volume", "+0%") if characters else "+0%",
            "duration": total_duration,
            "audio_b64": audio_b64,
            "boundaries": merged_boundaries,
            "text_preview": text[:60] + ("..." if len(text) > 60 else ""),
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "turn_count": len(script.turns),
            "characters": [c["name"] for c in characters],
        }
        self._history.append(item)

        return json.dumps({
            "success": True,
            "duration": total_duration,
            "audio_b64": audio_b64,
            "boundaries": merged_boundaries,
            "turn_count": len(script.turns),
            "history_id": self._history_counter,
        })
