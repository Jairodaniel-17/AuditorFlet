from datetime import datetime
from types import SimpleNamespace

import pytest

from suitescript_auditor.core.jobs.models import Job, JobSettings, JobSourceType, JobStatus
from suitescript_auditor.core.jobs.queue import JobQueue


class DummyThread:
    def __init__(self, target, args, daemon):
        self._target = target
        self._args = args

    def start(self):
        self._target(*self._args)


def test_job_queue_submit_executes_runner(monkeypatch, tmp_path):
    calls = []

    def fake_run(job, on_update=None):
        job.status = JobStatus.COMPLETED
        calls.append(job.id)

    queue = JobQueue(runner=SimpleNamespace(run=fake_run))
    monkeypatch.setattr("suitescript_auditor.core.jobs.queue.threading.Thread", DummyThread)
    job = queue.submit_job(
        project_name="Proj",
        source=tmp_path,
        source_type=JobSourceType.REPOSITORY,
        settings=JobSettings(),
    )
    assert job.status == JobStatus.COMPLETED
    assert calls == [job.id]
    assert queue.list_jobs()
