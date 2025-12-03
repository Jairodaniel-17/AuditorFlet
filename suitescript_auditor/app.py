"""Tkinter entrypoint for SuiteScript Auditor."""

from __future__ import annotations

import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk
from typing import Callable

if __package__ in {None, ""}:  # Support running as script: python suitescript_auditor/app.py
    ROOT = Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from suitescript_auditor.core.jobs.queue import JobQueue  # type: ignore
else:
    from .core.jobs.queue import JobQueue

from .ui.views import (
    docs_browser,
    file_review,
    history,
    new_analysis,
    processing_center,
    results,
    run_log,
    settings,
)


ViewBuilder = Callable[[tk.Widget, "AppContext"], ttk.Frame]


@dataclass
class AppContext:
    job_queue: JobQueue


class SuiteScriptAuditorApp(tk.Tk):
    """Main Tkinter window with sidebar navigation."""

    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self.title("SuiteScript Auditor (Tkinter)")
        self.geometry("1280x800")
        self.minsize(1024, 720)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.nav_items: list[tuple[str, ViewBuilder]] = [
            ("Processing Center", processing_center.build),
            ("New Analysis", new_analysis.build),
            ("Run Log", run_log.build),
            ("Results", results.build),
            ("File Review", file_review.build),
            ("Docs Browser", docs_browser.build),
            ("Settings", settings.build),
            ("History", history.build),
        ]

        self._setup_layout()
        self.current_view: ttk.Frame | None = None
        self.show_view(self.nav_items[0][1])

    def _setup_layout(self) -> None:
        container = ttk.Frame(self, padding=0)
        container.pack(fill="both", expand=True)

        sidebar = ttk.Frame(container, width=220, padding=10)
        sidebar.pack(side="left", fill="y")
        ttk.Label(sidebar, text="SuiteScript Auditor", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

        for label, builder in self.nav_items:
            ttk.Button(sidebar, text=label, command=lambda b=builder: self.show_view(b)).pack(
                fill="x", pady=2, anchor="w"
            )

        self.content = ttk.Frame(container, padding=10)
        self.content.pack(side="left", fill="both", expand=True)

    def show_view(self, builder: ViewBuilder) -> None:
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = builder(self.content, self.context)
        self.current_view.pack(fill="both", expand=True)


def main() -> None:
    context = AppContext(job_queue=JobQueue())
    app = SuiteScriptAuditorApp(context)
    app.mainloop()


def run() -> None:  # Kept for compatibility with previous entrypoint
    main()
