from dataclasses import dataclass

from tts_tool.tts_engine import TICKS_PER_MS


@dataclass
class SrtEntry:
    index: int
    start_ms: int
    end_ms: int
    text: str

    @staticmethod
    def format_timestamp(ms: int) -> str:
        hours, remainder = divmod(ms, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, millis = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    def to_srt_block(self) -> str:
        start = self.format_timestamp(self.start_ms)
        end = self.format_timestamp(self.end_ms)
        return f"{self.index}\n{start} --> {end}\n{self.text}\n\n"


def generate_srt(boundaries: list[dict]) -> str:
    if not boundaries:
        return ""

    entries = []
    for i, b in enumerate(boundaries, start=1):
        start_ms = b["offset"] // TICKS_PER_MS
        end_ms = start_ms + b["duration"] // TICKS_PER_MS
        entries.append(
            SrtEntry(index=i, start_ms=start_ms, end_ms=end_ms, text=b["text"])
        )

    return "".join(e.to_srt_block() for e in entries)
