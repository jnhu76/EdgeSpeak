from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TTSResult:
    audio_data: bytes
    boundaries: list[dict]


class TTSProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def supported_languages(self) -> list[str]: ...

    @abstractmethod
    async def generate_segment(
        self,
        text: str,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> tuple[bytes, list[dict]]: ...

    @abstractmethod
    async def list_voices(self, language_prefix: str = "") -> list[dict]: ...

    @staticmethod
    def validate_param(value: str, param: str) -> str:
        patterns = {
            "rate": r"^[+-]\d+%$",
            "pitch": r"^[+-]\d+Hz$",
            "volume": r"^[+-]\d+%$",
        }
        if param not in patterns:
            raise ValueError(f"Unknown param: {param}")
        if not re.match(patterns[param], value):
            raise ValueError(f"Invalid {param}: {value}")
        return value
