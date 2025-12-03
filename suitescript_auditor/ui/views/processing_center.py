"""Processing Center dashboard view."""

from __future__ import annotations

import flet as ft

from ...core.jobs.models import Job, JobStage, JobStatus
from ..components import cards
from ..shell import primary_action, secondary_icon
from .common import make_view


STATUS_ORDER = {
    JobStatus.RUNNING: 0,
    JobStatus.PENDING: 1,
    JobStatus.COMPLETED: 2,
    JobStatus.FAILED: 3,
    JobStatus.CANCELED: 4,
}


def build_processing_center(page: ft.Page, context) -> ft.View:
    jobs = sorted(context.job_queue.list_jobs(), key=lambda j: STATUS_ORDER.get(j.status, 99))

    total = len(jobs)
    running = sum(1 for j in jobs if j.status == JobStatus.RUNNING)
    completed = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
    failed = sum(1 for j in jobs if j.status == JobStatus.FAILED)
    llm_cost_today = sum(j.llm_cost for j in jobs)

    cards_row = cards.horizontal_metrics(
        [
            cards.metric_card("Total Jobs", str(total)),
            cards.metric_card("Running", str(running)),
            cards.metric_card("Completed", str(completed)),
            cards.metric_card("Failed", str(failed)),
            cards.metric_card("LLM Cost Today", f"${llm_cost_today:.2f}"),
        ]
    )

    job_table = _build_table(page, jobs)
    inspector = _build_inspector(jobs[0] if jobs else None)

    body = ft.Column(
        controls=[
            cards_row,
            ft.Container(height=16),
            ft.Text("Jobs Queue", size=18, weight="bold"),
            job_table,
        ],
        expand=True,
    )

    return make_view(
        "/",
        ["Processing Center"],
        body,
        inspector=inspector,
        actions=lambda: [
            primary_action("New Analysis", lambda _: page.go("/analysis/new")),
            secondary_icon("settings", "Settings", lambda _: page.go("/settings")),
            secondary_icon("help_outline", "Help", lambda _: page.go("/docs")),
        ],
    )


def _build_table(page: ft.Page, jobs: list[Job]) -> ft.Control:
    columns = [
        ft.DataColumn(ft.Text("Project Name")),
        ft.DataColumn(ft.Text("Source")),
        ft.DataColumn(ft.Text("Status")),
        ft.DataColumn(ft.Text("Progress")),
        ft.DataColumn(ft.Text("Stage")),
        ft.DataColumn(ft.Text("Current file")),
        ft.DataColumn(ft.Text("Files processed")),
        ft.DataColumn(ft.Text("Elapsed / ETA")),
        ft.DataColumn(ft.Text("LLM Cost")),
        ft.DataColumn(ft.Text("Actions")),
    ]
    rows = []
    for job in jobs:
        actions = []
        if job.status == JobStatus.RUNNING:
            actions.append(ft.TextButton("Open Run Log", on_click=lambda _, j=job: page.go("/run-log")))
            actions.append(ft.TextButton("Cancel", on_click=lambda _, j=job: None))
        if job.status == JobStatus.COMPLETED:
            actions.append(ft.TextButton("Open Results", on_click=lambda _, j=job: page.go("/results")))
            actions.append(ft.TextButton("Export Docs.zip", on_click=lambda _, j=job: None))
        if job.status == JobStatus.FAILED:
            actions.append(ft.TextButton("Retry", on_click=lambda _, j=job: page.go("/analysis/new")))
        row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(job.project_name)),
                ft.DataCell(ft.Text(job.source_type.value.upper())),
                ft.DataCell(ft.Text(job.status.value.title())),
                ft.DataCell(ft.Text(f"{job.progress*100:.0f}%")),
                ft.DataCell(ft.Text(job.stage.value if isinstance(job.stage, JobStage) else str(job.stage))),
                ft.DataCell(ft.Text(job.current_file or "-")),
                ft.DataCell(ft.Text(f"{job.files_processed}/{job.files_total}")),
                ft.DataCell(ft.Text("-")),
                ft.DataCell(ft.Text(f"${job.llm_cost:.2f}")),
                ft.DataCell(ft.Column(actions)),
            ]
        )
        rows.append(row)
    return ft.DataTable(columns=columns, rows=rows, expand=True, data_row_min_height=60)


def _build_inspector(job: Job | None) -> ft.Control:
    if not job:
        return ft.Container(width=340, padding=20, content=ft.Text("Select a job to inspect."))
    tokens_in = job.results.get("tokens_in", 0) if job.results else 0
    tokens_out = job.results.get("tokens_out", 0) if job.results else 0
    return ft.Container(
        width=340,
        padding=20,
        bgcolor="#FFFFFF",
        content=ft.Column(
            controls=[
                ft.Text("Job Inspector", weight="bold"),
                ft.Text(f"Project: {job.project_name}"),
                ft.Text(f"LLM model: {job.settings.quality_tier} / {job.settings.llm_mode_label}"),
                ft.Text(f"Tokens in/out: {tokens_in}/{tokens_out}"),
                ft.Text(f"LLM Cost (USD): ${job.llm_cost:.2f}"),
                ft.Divider(),
                ft.Switch(label="Limit cost per job", value=bool(job.settings.cost_limit)),
                ft.TextField(label="Maximum USD", value=str(job.settings.cost_limit or "")),
            ]
        ),
    )
