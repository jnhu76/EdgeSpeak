from __future__ import annotations

from tts_tool.dialog.merger import DialogMerger
from tts_tool.tts_engine import MP3_BITRATE, TTSEngine


def _make_silence(duration_s: float) -> bytes:
    return TTSEngine.generate_silence_ms(duration_s)


class TestDialogMergerConcat:
    def test_concat_two_clips(self):
        clip1 = b"\xff\xfb" + b"\x00" * 100
        clip2 = b"\xff\xfb" + b"\x01" * 100
        result = DialogMerger.concat_clips([clip1, clip2], inter_pause_s=0.0)
        assert result == clip1 + clip2

    def test_concat_with_pause(self):
        clip1 = b"\xff\xfb" + b"\x00" * 100
        clip2 = b"\xff\xfb" + b"\x01" * 100
        result = DialogMerger.concat_clips([clip1, clip2], inter_pause_s=0.5)
        silence = _make_silence(0.5)
        assert result == clip1 + silence + clip2

    def test_concat_single_clip(self):
        clip = b"\xff\xfb" + b"\x00" * 100
        result = DialogMerger.concat_clips([clip], inter_pause_s=0.5)
        assert result == clip

    def test_concat_empty_list(self):
        result = DialogMerger.concat_clips([], inter_pause_s=0.5)
        assert result == b""

    def test_concat_three_clips_with_pauses(self):
        clips = [b"\x01" * 50, b"\x02" * 50, b"\x03" * 50]
        result = DialogMerger.concat_clips(clips, inter_pause_s=0.3)
        silence = _make_silence(0.3)
        assert result == clips[0] + silence + clips[1] + silence + clips[2]


class TestDialogMergerParagraphPause:
    def test_concat_with_paragraph_pause(self):
        clip1 = b"\xff" * 50
        clip2 = b"\xfb" * 50
        result = DialogMerger.concat_clips(
            [clip1, clip2],
            inter_pause_s=0.0,
            paragraph_pause_s=2.0,
            paragraph_after_indices=[0],
        )
        silence = _make_silence(2.0)
        assert result == clip1 + silence + clip2


class TestDialogMergerMergeBoundaries:
    def test_merge_two_sets(self):
        b1 = [
            {"text": "你好", "offset": 0, "duration": 5000000},
            {"text": "世界", "offset": 5000000, "duration": 5000000},
        ]
        b2 = [
            {"text": "谢谢", "offset": 0, "duration": 3000000},
        ]
        duration1 = 1.0
        pause_duration = 0.5
        result = DialogMerger.merge_boundaries(
            [b1, b2],
            durations=[duration1],
            inter_pause_s=0.5,
        )
        assert len(result) == 3
        assert result[2]["offset"] > 0

    def test_merge_empty(self):
        result = DialogMerger.merge_boundaries([], durations=[], inter_pause_s=0.5)
        assert result == []

    def test_merge_offsets_cumulative(self):
        b1 = [{"text": "A", "offset": 0, "duration": 5000000}]
        b2 = [{"text": "B", "offset": 0, "duration": 3000000}]
        result = DialogMerger.merge_boundaries(
            [b1, b2],
            durations=[1.0],
            inter_pause_s=0.5,
        )
        expected_offset = 5000000 + 5000000
        assert result[1]["offset"] == expected_offset

    def test_merge_with_speaker_prefix(self):
        b1 = [{"text": "你好", "offset": 0, "duration": 5000000}]
        result = DialogMerger.merge_boundaries(
            [b1],
            durations=[],
            inter_pause_s=0.0,
            speakers=["男"],
        )
        assert result[0]["text"] == "[男] 你好"


class TestDialogMergerComputeDuration:
    def test_compute_from_bytes(self):
        silence = _make_silence(1.0)
        duration = DialogMerger.compute_duration(silence, bitrate=MP3_BITRATE)
        assert duration > 0.5

    def test_compute_empty(self):
        duration = DialogMerger.compute_duration(b"", bitrate=MP3_BITRATE)
        assert duration == 0.0
