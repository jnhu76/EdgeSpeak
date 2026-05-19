from pathlib import Path
from unittest.mock import patch

import pytest

from tts_tool.audio_player import AudioPlayer


class TestAudioPlayerInit:
    @patch("tts_tool.audio_player.pygame")
    def test_default_state(self, mock_pygame):
        player = AudioPlayer()
        assert not player.is_playing
        assert not player.is_paused
        assert player.current_file is None

    def test_format_time_zero(self):
        assert AudioPlayer.format_time(0) == "00:00"

    def test_format_time_seconds(self):
        assert AudioPlayer.format_time(65) == "01:05"

    def test_format_time_hours(self):
        assert AudioPlayer.format_time(3661) == "61:01"


class TestAudioPlayerLoad:
    @patch("tts_tool.audio_player.pygame")
    def test_load_file_success(self, mock_pygame):
        mock_pygame.mixer.music.get_busy.return_value = False
        player = AudioPlayer()
        player.load(Path("/fake/test.mp3"))
        assert player.current_file == Path("/fake/test.mp3")

    @patch("tts_tool.audio_player.pygame")
    def test_load_none_path(self, mock_pygame):
        player = AudioPlayer()
        with pytest.raises(ValueError):
            player.load(None)


class TestAudioPlayerPlayback:
    @patch("tts_tool.audio_player.pygame")
    def test_play(self, mock_pygame):
        mock_pygame.mixer.music.get_busy.return_value = False
        player = AudioPlayer()
        player.load(Path("/fake/test.mp3"))
        player.play()
        mock_pygame.mixer.music.play.assert_called()

    @patch("tts_tool.audio_player.pygame")
    def test_pause(self, mock_pygame):
        mock_pygame.mixer.music.get_busy.return_value = True
        player = AudioPlayer()
        player.load(Path("/fake/test.mp3"))
        player.play()
        mock_pygame.mixer.music.get_busy.return_value = True
        player.pause()
        mock_pygame.mixer.music.pause.assert_called()

    @patch("tts_tool.audio_player.pygame")
    def test_stop(self, mock_pygame):
        mock_pygame.mixer.music.get_busy.return_value = True
        player = AudioPlayer()
        player.load(Path("/fake/test.mp3"))
        player.play()
        player.stop()
        mock_pygame.mixer.music.stop.assert_called()
        assert not player.is_playing


class TestAudioPlayerSeek:
    @patch("tts_tool.audio_player.pygame")
    def test_seek_to_position(self, mock_pygame):
        player = AudioPlayer()
        player._duration_s = 60.0
        player.seek(0.5)
        mock_pygame.mixer.music.set_pos.assert_called_with(30.0)

    @patch("tts_tool.audio_player.pygame")
    def test_seek_without_duration(self, mock_pygame):
        player = AudioPlayer()
        player._duration_s = None
        with pytest.raises(ValueError):
            player.seek(0.5)
