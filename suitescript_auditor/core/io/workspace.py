"""Temporary workspace management."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


class WorkspaceManager:
    def __init__(self) -> None:
        self._root = Path(tempfile.gettempdir()) / "suitescript_auditor"
        self._root.mkdir(parents=True, exist_ok=True)

    def create(self, job_id: str) -> Path:
        workspace = self._root / job_id
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace

    def cleanup(self, job_id: str) -> None:
        workspace = self._root / job_id
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
