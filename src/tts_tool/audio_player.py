from __future__ import annotations

from pathlib import Path

import pygame


class AudioPlayer:
    def __init__(self) -> None:
        pygame.mixer.init()
        self._current_file: Path | None = None
        self._is_playing: bool = False
        self._is_paused: bool = False
        self._duration_s: float | None = None

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def current_file(self) -> Path | None:
        return self._current_file

    @staticmethod
    def format_time(seconds: float) -> str:
        total = int(seconds)
        mins, secs = divmod(total, 60)
        return f"{mins:02d}:{secs:02d}"

    def load(self, file_path: Path | None) -> None:
        if file_path is None:
            raise ValueError("file_path must not be None")
        self.stop()
        self._current_file = file_path
        pygame.mixer.music.load(str(file_path))
        self._duration_s = None

    def play(self) -> None:
        if self._current_file is None:
            return
        if self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False
            self._is_playing = True
            return
        pygame.mixer.music.play()
        self._is_playing = True
        self._is_paused = False

    def pause(self) -> None:
        if self._is_playing and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            self._is_playing = False

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self._is_playing = False
        self._is_paused = False

    def seek(self, position: float) -> None:
        if self._duration_s is None:
            raise ValueError("Duration unknown, cannot seek")
        if not 0.0 <= position <= 1.0:
            raise ValueError("position must be between 0.0 and 1.0")
        target_s = position * self._duration_s
        pygame.mixer.music.set_pos(target_s)

    def get_position(self) -> float:
        if not self._is_playing and not self._is_paused:
            return 0.0
        try:
            pos = pygame.mixer.music.get_pos()
            if pos < 0:
                self._is_playing = False
                self._is_paused = False
                return 0.0
            return pos / 1000.0
        except Exception:
            self._is_playing = False
            self._is_paused = False
            return 0.0

    def cleanup(self) -> None:
        self.stop()
        pygame.mixer.quit()
