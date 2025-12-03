"""Job and queue related models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional


class JobSourceType(str, Enum):
    ZIP = "zip"
    REPOSITORY = "repo"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class JobStage(str, Enum):
    PREPARING = "Preparing workspace"
    DISCOVERING = "Discovering files"
    PARSING = "Parsing"
    RULES = "Static checks"
    LLM = "LLM Analysis"
    WRITING = "Generating Docs"
    PACKAGING = "Packaging results"
    COMPLETE = "Complete"


@dataclass
class JobSettings:
    generate_audit: bool = True
    generate_summary: bool = True
    include_markdown: bool = True
    llm_mode: bool = False
    quality_tier: str = "Economic"
    strict_suite_script: bool = True
    prioritize_transaction_safety: bool = True
    exclude_minified: bool = True
    moe_multiexpert: bool = True
    cost_limit: float | None = None
    llm_mode_label: str = "OFF"
    max_tokens_per_file: int = 2000


@dataclass
class Job:
    id: str
    project_name: str
    source: Path
    source_type: JobSourceType
    created_at: datetime
    settings: JobSettings
    status: JobStatus = JobStatus.PENDING
    stage: JobStage = JobStage.PREPARING
    progress: float = 0.0
    files_total: int = 0
    files_processed: int = 0
    llm_cost: float = 0.0
    current_file: str | None = None
    error: str | None = None
    results: Dict[str, Any] = field(default_factory=dict)
    log: List["JobLogEntry"] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_name": self.project_name,
            "source": str(self.source),
            "source_type": self.source_type.value,
            "status": self.status.value,
            "stage": self.stage.value,
            "progress": self.progress,
            "files_total": self.files_total,
            "files_processed": self.files_processed,
            "llm_cost": self.llm_cost,
            "current_file": self.current_file,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class JobLogEntry:
    timestamp: datetime
    level: str
    message: str


@dataclass
class FileArtifact:
    path: Path
    audit_json: Optional[Dict[str, Any]] = None
    summary_json: Optional[Dict[str, Any]] = None
    audit_markdown: Optional[str] = None
    summary_markdown: Optional[str] = None


@dataclass
class JobResult:
    job: Job
    artifacts: List[FileArtifact]
    docs_path: Path
    index_json: Dict[str, Any]
