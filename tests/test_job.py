from __future__ import annotations

from tts_tool.job import Job, JobStore


class TestJob:
    def test_create_job(self):
        j = Job(id=1, text="hello", voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        assert j.id == 1
        assert j.text == "hello"
        assert j.status == "pending"
        assert j.audio_b64 is None

    def test_job_to_dict(self):
        j = Job(id=1, text="hello", voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        d = j.to_dict()
        assert d["id"] == 1
        assert d["voice"] == "Aria"
        assert d["status"] == "pending"
        assert "audio_b64" not in d

    def test_job_to_dict_with_audio(self):
        j = Job(id=1, text="hello", voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        j.mark_done(audio_b64="abc", duration=5.0, boundaries=[])
        d = j.to_dict()
        assert d["duration"] == 5.0

    def test_job_mark_done(self):
        j = Job(id=1, text="hello", voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        j.mark_done(audio_b64="abc", duration=5.0, boundaries=[{"offset": 0}])
        assert j.status == "done"
        assert j.audio_b64 == "abc"
        assert j.duration == 5.0

    def test_job_mark_error(self):
        j = Job(id=1, text="hello", voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        j.mark_error("network fail")
        assert j.status == "error"
        assert j.error == "network fail"

    def test_job_text_preview_short(self):
        j = Job(id=1, text="hi", voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        assert j.text_preview == "hi"

    def test_job_text_preview_long(self):
        j = Job(id=1, text="a" * 100, voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        assert len(j.text_preview) == 63
        assert j.text_preview.endswith("...")


class TestJobStore:
    def test_create_store(self):
        store = JobStore()
        assert store.list_jobs() == []

    def test_add_job(self):
        store = JobStore()
        j = store.add_job(text="hello", voice="Aria", rate="+0%", pitch="+0Hz", volume="+0%")
        assert j.id == 1
        assert j.text == "hello"
        assert len(store.list_jobs()) == 1

    def test_add_multiple_jobs_increments_id(self):
        store = JobStore()
        j1 = store.add_job(text="a", voice="A", rate="+0%", pitch="+0Hz", volume="+0%")
        j2 = store.add_job(text="b", voice="B", rate="+0%", pitch="+0Hz", volume="+0%")
        assert j1.id == 1
        assert j2.id == 2
        assert len(store.list_jobs()) == 2

    def test_get_job(self):
        store = JobStore()
        store.add_job(text="a", voice="A", rate="+0%", pitch="+0Hz", volume="+0%")
        j2 = store.add_job(text="b", voice="B", rate="+0%", pitch="+0Hz", volume="+0%")
        found = store.get_job(j2.id)
        assert found is not None
        assert found.text == "b"

    def test_get_job_not_found(self):
        store = JobStore()
        assert store.get_job(999) is None

    def test_delete_job(self):
        store = JobStore()
        j1 = store.add_job(text="a", voice="A", rate="+0%", pitch="+0Hz", volume="+0%")
        store.add_job(text="b", voice="B", rate="+0%", pitch="+0Hz", volume="+0%")
        store.delete_job(j1.id)
        assert len(store.list_jobs()) == 1
        assert store.get_job(j1.id) is None

    def test_clear_jobs(self):
        store = JobStore()
        store.add_job(text="a", voice="A", rate="+0%", pitch="+0Hz", volume="+0%")
        store.add_job(text="b", voice="B", rate="+0%", pitch="+0Hz", volume="+0%")
        store.clear()
        assert store.list_jobs() == []
        j = store.add_job(text="c", voice="C", rate="+0%", pitch="+0Hz", volume="+0%")
        assert j.id == 1

    def test_list_jobs_returns_summary(self):
        store = JobStore()
        j = store.add_job(text="hello world", voice="Aria", rate="+50%", pitch="+0Hz", volume="+0%")
        j.mark_done(audio_b64="abc", duration=12.5, boundaries=[])
        jobs = store.list_jobs()
        assert len(jobs) == 1
        assert jobs[0]["voice"] == "Aria"
        assert jobs[0]["duration"] == 12.5
        assert jobs[0]["status"] == "done"
        assert "audio_b64" not in jobs[0]

    def test_list_jobs_newest_first(self):
        store = JobStore()
        store.add_job(text="first", voice="A", rate="+0%", pitch="+0Hz", volume="+0%")
        store.add_job(text="second", voice="B", rate="+0%", pitch="+0Hz", volume="+0%")
        jobs = store.list_jobs()
        assert jobs[0]["text_preview"] == "second"
        assert jobs[1]["text_preview"] == "first"
