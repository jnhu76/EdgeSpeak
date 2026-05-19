from __future__ import annotations

from datetime import datetime, timezone


TEXT_PREVIEW_MAX = 60


class Job:
    def __init__(
        self,
        id: int,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
        sentence_pause: float = 0.0,
        paragraph_pause: float = 0.0,
    ) -> None:
        self.id = id
        self.text = text
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self.sentence_pause = sentence_pause
        self.paragraph_pause = paragraph_pause
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.audio_b64: str | None = None
        self.duration: float = 0.0
        self.boundaries: list | None = None
        self.status: str = "pending"
        self.error: str | None = None

    def mark_done(self, audio_b64: str, duration: float, boundaries: list) -> None:
        self.status = "done"
        self.audio_b64 = audio_b64
        self.duration = duration
        self.boundaries = boundaries

    def mark_error(self, error: str) -> None:
        self.status = "error"
        self.error = error

    @property
    def text_preview(self) -> str:
        if len(self.text) <= TEXT_PREVIEW_MAX:
            return self.text
        return self.text[:TEXT_PREVIEW_MAX] + "..."

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "voice": self.voice,
            "rate": self.rate,
            "pitch": self.pitch,
            "volume": self.volume,
            "duration": self.duration,
            "status": self.status,
            "text_preview": self.text_preview,
            "created_at": self.created_at,
        }


class JobStore:
    def __init__(self) -> None:
        self._jobs: list[Job] = []
        self._next_id: int = 1

    def add_job(
        self,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
        sentence_pause: float = 0.0,
        paragraph_pause: float = 0.0,
    ) -> Job:
        job = Job(
            id=self._next_id,
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
            sentence_pause=sentence_pause,
            paragraph_pause=paragraph_pause,
        )
        self._jobs.append(job)
        self._next_id += 1
        return job

    def get_job(self, job_id: int) -> Job | None:
        for j in self._jobs:
            if j.id == job_id:
                return j
        return None

    def delete_job(self, job_id: int) -> None:
        self._jobs = [j for j in self._jobs if j.id != job_id]

    def clear(self) -> None:
        self._jobs = []
        self._next_id = 1

    def list_jobs(self) -> list[dict]:
        return [j.to_dict() for j in reversed(self._jobs)]
