"""Run Log view."""

from __future__ import annotations

import flet as ft

from ...core.jobs.models import Job, JobStage, JobStatus
from ..shell import primary_action
from .common import make_view


def build_run_log(page: ft.Page, context) -> ft.View:
    jobs = context.job_queue.list_jobs()
    selected = next((j for j in jobs if j.status == JobStatus.RUNNING), jobs[-1] if jobs else None)

    if not selected:
        body = ft.Text("No job selected. Start a new analysis to view logs.")
        return make_view("/run-log", ["Processing Center", "Run Log"], body)

    progress = ft.ProgressBar(value=selected.progress, width=400)

    stepper = ft.Column(
        controls=[_step_item(stage, stage == selected.stage) for stage in JobStage],
        spacing=8,
    )

    log_console = ft.ListView(
        controls=[
            ft.Text(f"[{entry.timestamp.isoformat()}] {entry.level.upper()} - {entry.message}")
            for entry in selected.log
        ]
        or [ft.Text("No logs yet.")],
        height=300,
    )

    cards_row = ft.Row(
        controls=[
            _info_card("Current file", selected.current_file or "-"),
            _info_card("Hotspots detected", str(selected.results.get("hotspots", 0) if selected.results else 0)),
            _info_card("Files processed / total", f"{selected.files_processed}/{selected.files_total}"),
            _info_card("LLM Cost so far", f"${selected.llm_cost:.2f}"),
        ],
        spacing=16,
    )

    actions = ft.Row(
        controls=[
            ft.ElevatedButton("Cancel Job", on_click=lambda _: None, bgcolor="#C62828", color="white"),
            ft.OutlinedButton("Back to Processing Center", on_click=lambda _: page.go("/")),
            ft.ElevatedButton(
                "Open Results",
                disabled=selected.status != JobStatus.COMPLETED,
                on_click=lambda _: page.go("/results"),
            ),
        ],
        spacing=16,
    )

    body = ft.Column(
        controls=[
            ft.Text(f"{selected.project_name} — {selected.status.value.title()}", size=22, weight="bold"),
            progress,
            stepper,
            cards_row,
            ft.Text("Logs", size=18, weight="bold"),
            log_console,
            actions,
        ],
        expand=True,
    )
    return make_view(
        "/run-log",
        ["Processing Center", "Run Log"],
        body,
        actions=lambda: [primary_action("Back", lambda _: page.go("/"))],
    )


def _step_item(stage: JobStage, active: bool) -> ft.Control:
    color = "#C62828" if active else "#BDBDBD"
    return ft.Row(
        controls=[
            ft.Icon("check_circle" if active else "radio_button_unchecked", color=color),
            ft.Text(stage.value),
        ]
    )


def _info_card(title: str, value: str) -> ft.Control:
    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=8,
        padding=16,
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text(title, size=12, color="#5C5C5C"),
                ft.Text(value, size=18, weight="bold"),
            ]
        ),
    )
