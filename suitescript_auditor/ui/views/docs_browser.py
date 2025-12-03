"""Docs Browser view."""

from __future__ import annotations

from pathlib import Path

import flet as ft

from .common import make_view


def build_docs_browser(page: ft.Page, context) -> ft.View:
    jobs = [job for job in context.job_queue.list_jobs() if job.results]
    if not jobs:
        return make_view("/docs", ["Processing Center", "Docs Browser"], ft.Text("Generate docs to browse them."))
    docs_path = Path(jobs[-1].results["docs_path"])
    summary_dir = docs_path / "summary"
    files = sorted(summary_dir.rglob("*.md"))
    if not files:
        return make_view("/docs", ["Processing Center", "Docs Browser"], ft.Text("No summary markdown files"))

    selected = files[0]
    file_list = ft.ListView(
        controls=[
            ft.ListTile(title=ft.Text(str(path.relative_to(summary_dir))), on_click=lambda e, p=path: None)
            for path in files
        ],
        expand=True,
    )
    viewer = ft.Markdown(selected.read_text(encoding="utf-8"), expand=True, selectable=True)
    body = ft.Row(
        controls=[
            ft.Container(width=320, bgcolor="#FFFFFF", padding=12, content=file_list),
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Dropdown(
                                label="Folder",
                                options=[ft.dropdown.Option("summary"), ft.dropdown.Option("audit")],
                                value="summary",
                            ),
                            ft.TextField(label="Search function", hint_text="Type to search...", expand=True),
                        ]
                    ),
                    viewer,
                ],
                expand=True,
            ),
        ],
        expand=True,
    )
    return make_view("/docs", ["Processing Center", "Docs Browser"], body)
