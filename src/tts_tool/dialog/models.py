from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DialogCharacter:
    name: str
    voice: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"
    color: str = "#4f46e5"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "voice": self.voice,
            "rate": self.rate,
            "pitch": self.pitch,
            "volume": self.volume,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, d: dict) -> DialogCharacter:
        return cls(
            name=d["name"],
            voice=d["voice"],
            rate=d.get("rate", "+0%"),
            pitch=d.get("pitch", "+0Hz"),
            volume=d.get("volume", "+0%"),
            color=d.get("color", "#4f46e5"),
        )


@dataclass
class DialogTurn:
    speaker: str
    text: str
    paragraph_pause: float = 0.0


@dataclass
class DialogScript:
    characters: list[DialogCharacter] = field(default_factory=list)
    turns: list[DialogTurn] = field(default_factory=list)
    inter_turn_pause: float = 0.8
    paragraph_pause: float = 2.0

    def get_character(self, name: str) -> DialogCharacter | None:
        for c in self.characters:
            if c.name == name:
                return c
        return None

    def add_character(self, character: DialogCharacter) -> None:
        self.characters.append(character)

    def add_turn(self, speaker: str, text: str, paragraph_pause: float = 0.0) -> None:
        self.turns.append(DialogTurn(speaker=speaker, text=text, paragraph_pause=paragraph_pause))

    def speaker_names(self) -> set[str]:
        return {t.speaker for t in self.turns}

    def turn_count(self) -> int:
        return len(self.turns)
