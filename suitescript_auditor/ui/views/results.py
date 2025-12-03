"""Results dashboard view."""

from __future__ import annotations

import json
from pathlib import Path

import flet as ft

from ..components import cards, tables
from ..shell import primary_action
from .common import make_view


def build_results(page: ft.Page, context) -> ft.View:
    jobs = [job for job in context.job_queue.list_jobs() if job.results]
    if not jobs:
        return make_view("/results", ["Processing Center", "Results"], ft.Text("Run an analysis to view results."))

    job = jobs[-1]
    docs_path = Path(job.results["docs_path"])
    index_path = docs_path / "index.json"
    index_data = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}

    summary_scores = index_data.get("summary_scores", {"overall": 0})
    counts = index_data.get("counts", {"files": 0, "critical_files": 0, "hotspots_high": 0})
    top_hotspots = index_data.get("top_hotspots", [])
    ranking_files = index_data.get("ranking_files", [])

    cards_row = cards.horizontal_metrics(
        [
            cards.metric_card("Overall Score", f"{summary_scores.get('overall', 0):.1f}"),
            cards.metric_card("Critical files", str(counts.get("critical_files", 0))),
            cards.metric_card("High severity hotspots", str(counts.get("hotspots_high", 0))),
            cards.metric_card("Total files analyzed", str(counts.get("files", 0))),
        ]
    )

    hotspots_table = tables.build_table(
        ["Severity", "File", "Line range", "Issue", "Score impact"],
        [
            (h["severity"], h["file"], h.get("line_range", "-"), h["title"], h.get("score", "-"))
            for h in top_hotspots
        ],
    )

    file_list = ranking_files
    selected_file = file_list[0] if file_list else None
    file_summary = _read_file_summary(docs_path, selected_file["path"]) if selected_file else {}
    summary_panel = _build_file_summary(file_summary)

    file_panel = ft.Row(
        controls=[
            _build_file_tree(file_list),
            summary_panel,
        ],
        expand=True,
    )

    actions = ft.Row(
        controls=[
            primary_action("Export Docs.zip", lambda _: None),
            ft.OutlinedButton("Export index.json", on_click=lambda _: None),
            ft.OutlinedButton("Open Docs folder", on_click=lambda _: page.launch_url(str(docs_path))),
            ft.ElevatedButton("Publish to Git", on_click=lambda _: page.go("/settings")),
        ],
        spacing=12,
    )

    body = ft.Column(
        controls=[
            cards_row,
            ft.Text("Top 10 Hotspots", size=18, weight="bold"),
            hotspots_table,
            ft.Divider(),
            ft.Text("Files", size=18, weight="bold"),
            file_panel,
            actions,
        ],
        expand=True,
    )

    return make_view("/results", ["Processing Center", "Results"], body)


def _build_file_tree(files: list[dict]) -> ft.Control:
    entries = []
    for item in files:
        entries.append(
            ft.ListTile(
                title=ft.Text(item["path"]),
                subtitle=ft.Text(f"Score {item['score_overall']:.1f}"),
                dense=True,
            )
        )
    return ft.Container(width=320, bgcolor="#FFFFFF", padding=12, content=ft.Column(entries, scroll="auto"))


def _build_file_summary(summary: dict) -> ft.Control:
    if not summary:
        return ft.Container(expand=True, padding=16, bgcolor="#FFFFFF", content=ft.Text("Select a file."))
    entry_points = summary.get("entry_points", [])
    functions = summary.get("functions", [])
    return ft.Container(
        expand=True,
        padding=16,
        bgcolor="#FFFFFF",
        content=ft.Column(
            controls=[
                ft.Text(summary.get("path", ""), size=20, weight="bold"),
                ft.Text(f"ScriptType: {summary.get('scriptType')}"),
                ft.Text(summary.get("overview", "")),
                ft.Text("Entry Points", weight="bold"),
                *(ft.Text(f"- {entry['name']} ({entry['lines']})") for entry in entry_points),
                ft.Text("Top Functions", weight="bold"),
                *(ft.Text(f"- {fn['name']} {fn['lines']}") for fn in functions[:3]),
                ft.Row(
                    controls=[
                        ft.TextButton("Open File Review", on_click=lambda _: None),
                        ft.TextButton("Open Docs (Summary)", on_click=lambda _: None),
                    ]
                ),
            ],
            scroll="auto",
        ),
    )


def _read_file_summary(docs_path: Path, rel_path: str) -> dict:
    summary_path = docs_path / "summary" / rel_path
    summary_path = summary_path.with_name(summary_path.name + ".summary.json")
    if summary_path.exists():
        return json.loads(summary_path.read_text(encoding="utf-8"))
    return {}
