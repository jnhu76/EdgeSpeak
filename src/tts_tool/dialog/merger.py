from __future__ import annotations

from tts_tool.tts_engine import TTSEngine


class DialogMerger:
    @staticmethod
    def concat_clips(
        clips: list[bytes],
        inter_pause_s: float = 0.0,
        paragraph_pause_s: float = 0.0,
        paragraph_after_indices: list[int] | None = None,
    ) -> bytes:
        if not clips:
            return b""

        paragraph_after = set(paragraph_after_indices) if paragraph_after_indices else set()
        parts: list[bytes] = []

        for i, clip in enumerate(clips):
            if i > 0:
                if (i - 1) in paragraph_after and paragraph_pause_s > 0:
                    parts.append(TTSEngine.generate_silence_ms(paragraph_pause_s))
                elif inter_pause_s > 0:
                    parts.append(TTSEngine.generate_silence_ms(inter_pause_s))
            parts.append(clip)

        return b"".join(parts)

    @staticmethod
    def merge_boundaries(
        boundary_sets: list[list[dict]],
        durations: list[float],
        inter_pause_s: float = 0.0,
        speakers: list[str] | None = None,
    ) -> list[dict]:
        if not boundary_sets:
            return []

        result: list[dict] = []
        cumulative_offset_ticks = 0

        for i, boundaries in enumerate(boundary_sets):
            for b in boundaries:
                entry = dict(b)
                entry["offset"] = b["offset"] + cumulative_offset_ticks
                if speakers and i < len(speakers):
                    entry["text"] = f"[{speakers[i]}] {b['text']}"
                result.append(entry)

            if i < len(boundary_sets) - 1 and boundaries:
                end_ticks = boundaries[-1]["offset"] + boundaries[-1].get("duration", 0)
                cumulative_offset_ticks += end_ticks
                pause_ticks = int(inter_pause_s * 1000 * 10000)
                cumulative_offset_ticks += pause_ticks

        return result

    @staticmethod
    def compute_duration(audio_bytes: bytes, bitrate: int) -> float:
        if not audio_bytes:
            return 0.0
        return len(audio_bytes) * 8 / bitrate
