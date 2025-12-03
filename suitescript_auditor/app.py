"""Flet entrypoint for SuiteScript Auditor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

import flet as ft

from .core.jobs.queue import JobQueue


@dataclass
class AppContext:
    """Shared context accessible to all views."""

    job_queue: JobQueue


ViewFactory = Callable[[ft.Page, AppContext], ft.View]


def _build_views() -> Dict[str, ViewFactory]:
    from .ui.views.processing_center import build_processing_center
    from .ui.views.new_analysis import build_new_analysis
    from .ui.views.run_log import build_run_log
    from .ui.views.results import build_results
    from .ui.views.file_review import build_file_review
    from .ui.views.docs_browser import build_docs_browser
    from .ui.views.settings import build_settings
    from .ui.views.history import build_history

    return {
        "/": build_processing_center,
        "/analysis/new": build_new_analysis,
        "/run-log": build_run_log,
        "/results": build_results,
        "/file-review": build_file_review,
        "/docs": build_docs_browser,
        "/settings": build_settings,
        "/history": build_history,
    }


def main(page: ft.Page) -> None:
    """Flet standard entrypoint."""

    page.title = "SuiteScript Auditor"
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "stretch"
    page.window_min_height = 720
    page.window_min_width = 1280

    context = AppContext(job_queue=JobQueue())
    view_builders = _build_views()

    def handle_route(route: str) -> None:
        builder = view_builders.get(route, view_builders["/"])
        page.views.clear()
        page.views.append(builder(page, context))
        page.update()

    page.on_route_change = lambda e: handle_route(e.route)
    handle_route(page.route or "/")


def run() -> None:
    ft.app(target=main)
