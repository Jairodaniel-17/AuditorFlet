"""History view."""

from __future__ import annotations

import json
from pathlib import Path

import flet as ft

from .common import make_view


def build_history(page: ft.Page, context) -> ft.View:
    rows = []
    for job in context.job_queue.list_jobs():
        docs_path = Path(job.results["docs_path"]) if job.results else None
        overall = "-"
        if docs_path and (docs_path / "index.json").exists():
            data = json.loads((docs_path / "index.json").read_text(encoding="utf-8"))
            overall = f"{data.get('summary_scores', {}).get('overall', 0):.1f}"
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(job.project_name)),
                    ft.DataCell(ft.Text(job.created_at.isoformat())),
                    ft.DataCell(ft.Text(job.status.value)),
                    ft.DataCell(ft.Text(overall)),
                ]
            )
        )
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Project")),
            ft.DataColumn(ft.Text("Timestamp")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Overall Score")),
        ],
        rows=rows,
    )
    body = ft.Column(
        controls=[
            ft.Text("Run History", size=22, weight="bold"),
            table,
            ft.TextButton("Export history", on_click=lambda _: None),
        ],
        expand=True,
    )
    return make_view("/history", ["Processing Center", "History"], body)
