"""Simple in-memory multi-job queue."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List

from .models import Job, JobSettings, JobSourceType, JobStatus
from .runner import JobRunner


class JobQueue:
    """Queues jobs and dispatches them to worker threads."""

    def __init__(self, runner: JobRunner | None = None) -> None:
        self._runner = runner or JobRunner()
        self._jobs: Dict[str, Job] = {}
        self._subscribers: List[Callable[[Job], None]] = []
        self._lock = threading.Lock()

    def submit_job(
        self,
        *,
        project_name: str,
        source: Path,
        source_type: JobSourceType,
        settings: JobSettings | None = None,
    ) -> Job:
        job_id = uuid.uuid4().hex[:8]
        job = Job(
            id=job_id,
            project_name=project_name,
            source=source,
            source_type=source_type,
            created_at=datetime.utcnow(),
            settings=settings or JobSettings(),
        )
        with self._lock:
            self._jobs[job_id] = job
        self._notify(job)
        thread = threading.Thread(target=self._run_job, args=(job,), daemon=True)
        thread.start()
        return job

    def list_jobs(self) -> List[Job]:
        with self._lock:
            return list(self._jobs.values())

    def subscribe(self, callback: Callable[[Job], None]) -> None:
        self._subscribers.append(callback)

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def _notify(self, job: Job) -> None:
        for callback in self._subscribers:
            callback(job)

    def _run_job(self, job: Job) -> None:
        try:
            self._runner.run(job, on_update=self._notify)
        except Exception as exc:  # pragma: no cover - guard rail
            job.status = JobStatus.FAILED
            job.error = str(exc)
            self._notify(job)
