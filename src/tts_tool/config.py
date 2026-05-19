from dataclasses import asdict, dataclass, field


SPEED_PRESETS: dict[str, int] = {
    "0.5x": -50,
    "1x": 0,
    "1.5x": 50,
    "2x": 100,
}


@dataclass(frozen=True)
class VoiceInfo:
    short_name: str
    accent: str
    gender: str
    name: str
    categories: list[str] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.gender})"

    @property
    def categories_str(self) -> str:
        return ", ".join(self.categories)


@dataclass
class AppConfig:
    voice: str = "en-US-AriaNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"
    sentence_pause: float = 1.0
    paragraph_pause: float = 3.0
    language_filter: str = "en"

    def apply_speed_preset(self, label: str) -> None:
        if label in SPEED_PRESETS:
            rate = SPEED_PRESETS[label]
            self.rate = f"{rate:+d}%"

    def to_dict(self) -> dict:
        return asdict(self)
