import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from suitescript_auditor.app import AppContext, SuiteScriptAuditorApp
from suitescript_auditor.core.jobs.models import (
    Job,
    JobLogEntry,
    JobSettings,
    JobSourceType,
    JobStage,
    JobStatus,
)
from suitescript_auditor.ui.views import (
    docs_browser,
    file_review,
    history,
    new_analysis,
    processing_center,
    results,
    run_log,
    settings,
)


class DummyWidget:
    def __init__(self, *args, **kwargs):
        self.children = []
        self._values = []
        self.kwargs = kwargs
        self._items = {}

    def pack(self, **kwargs):
        return self

    def grid(self, **kwargs):
        return self

    def configure(self, **kwargs):
        return self

    config = configure

    def destroy(self):
        return None

    def insert(self, *args, **kwargs):
        self._values.append((args, kwargs))

    def delete(self, *args, **kwargs):
        return None

    def bind(self, *args, **kwargs):
        return None

    def set(self, *args, **kwargs):
        return None

    def columnconfigure(self, *args, **kwargs):
        return None

    def rowconfigure(self, *args, **kwargs):
        return None

    def __setitem__(self, key, value):
        self._items[key] = value

    def __getitem__(self, key):
        return self._items.get(key)


class DummyTreeview(DummyWidget):
    def heading(self, *args, **kwargs):
        return None

    def column(self, *args, **kwargs):
        return None

    def get_children(self):
        return []

    def yview(self, *args, **kwargs):
        return None


class DummyListbox(DummyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

    def insert(self, index, value):
        self.items.append(value)

    def curselection(self):
        return ()

    def get(self, index):
        return self.items[index]


class DummyVar:
    def __init__(self, value=None):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class DummyTk(DummyWidget):
    def withdraw(self):
        return None


class DummyStyle:
    def __init__(self, *args, **kwargs):
        pass

    def theme_use(self, name):
        return None


class DummyQueue:
    def __init__(self, jobs):
        self._jobs = jobs

    def list_jobs(self):
        return self._jobs


@pytest.fixture(autouse=True)
def mock_tk(monkeypatch):
    monkeypatch.setattr(tk, "Tk", DummyTk)
    monkeypatch.setattr(tk, "StringVar", DummyVar)
    monkeypatch.setattr(tk, "BooleanVar", DummyVar)
    monkeypatch.setattr(ttk, "Style", DummyStyle)
    widget_classes = [
        "Frame",
        "Label",
        "Button",
        "Entry",
        "Checkbutton",
        "LabelFrame",
        "Progressbar",
        "Scrollbar",
        "Scale",
        "Combobox",
        "Radiobutton",
    ]
    for name in widget_classes:
        monkeypatch.setattr(ttk, name, DummyWidget)
    monkeypatch.setattr(ttk, "Treeview", DummyTreeview)
    monkeypatch.setattr(tk, "Listbox", DummyListbox)
    monkeypatch.setattr(tk, "Text", DummyWidget)
    monkeypatch.setattr(ttk, "Notebook", DummyWidget, raising=False)


@pytest.fixture
def tk_root():
    return DummyTk()


@pytest.fixture
def context_with_job(tmp_path):
    docs = tmp_path / "Docs"
    (docs / "audit").mkdir(parents=True)
    (docs / "summary").mkdir()
    audit_payload = {
        "path": "script.js",
        "hash": "hash",
        "scriptType": "UserEventScript",
        "apiVersion": "2.x",
        "score_1_10": {"overall": 8},
        "hotspots": [],
        "netsuite_specific": [],
        "fix_plan": [],
    }
    (docs / "audit" / "script.js.audit.json").write_text(json.dumps(audit_payload), encoding="utf-8")
    (docs / "summary" / "script.js.summary.md").write_text("# Summary\n", encoding="utf-8")
    index_payload = {
        "project": {"name": "Demo", "source": "repo", "run_id": "job1", "timestamp": "now"},
        "settings": {},
        "summary_scores": {"overall": 8.5},
        "counts": {"files": 1, "critical_files": 0, "hotspots_high": 0},
        "ranking_files": [{"path": "script.js", "score_overall": 8.5, "hotspots_high": 0}],
        "top_hotspots": [],
        "llm_usage": {"tokens_in": 0, "tokens_out": 0, "cost_total": 0.0},
    }
    (docs / "index.json").write_text(json.dumps(index_payload), encoding="utf-8")

    job = Job(
        id="job1",
        project_name="Demo",
        source=tmp_path,
        source_type=JobSourceType.REPOSITORY,
        created_at=datetime.utcnow(),
        settings=JobSettings(),
    )
    job.status = JobStatus.COMPLETED
    job.stage = JobStage.COMPLETE
    job.results = {"docs_path": str(docs), "summary_score": 8.5}
    job.files_total = 1
    job.files_processed = 1
    job.progress = 1.0
    job.llm_cost = 1.23
    job.log = [JobLogEntry(timestamp=datetime.utcnow(), level="info", message="Started")]

    queue = DummyQueue([job])
    return AppContext(job_queue=queue)


def test_processing_center_view(tk_root, context_with_job):
    frame = processing_center.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_new_analysis_view(tk_root, context_with_job):
    frame = new_analysis.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_run_log_view(tk_root, context_with_job):
    frame = run_log.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_results_view(tk_root, context_with_job):
    frame = results.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_file_review_view(tk_root, context_with_job):
    frame = file_review.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_docs_browser_view(tk_root, context_with_job):
    frame = docs_browser.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_settings_view(tk_root, context_with_job):
    frame = settings.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_history_view(tk_root, context_with_job):
    frame = history.build(tk_root, context_with_job)
    assert isinstance(frame, ttk.Frame)


def test_app_navigation(context_with_job):
    app = SuiteScriptAuditorApp(context_with_job)
    app.show_view(new_analysis.build)
    assert isinstance(app.current_view, ttk.Frame)
    app.destroy()
