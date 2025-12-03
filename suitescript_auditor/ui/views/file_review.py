"""File Review view."""

from __future__ import annotations

import json
from pathlib import Path

import flet as ft

from ..components import badges, code_viewer
from ..shell import primary_action
from .common import make_view


def build_file_review(page: ft.Page, context) -> ft.View:
    jobs = [job for job in context.job_queue.list_jobs() if job.results]
    if not jobs:
        return make_view("/file-review", ["Processing Center", "File Review"], ft.Text("No results yet."))

    job = jobs[-1]
    docs_path = Path(job.results["docs_path"])
    audit_files = sorted((docs_path / "audit").rglob("*.audit.json"))
    if not audit_files:
        return make_view("/file-review", ["Processing Center", "File Review"], ft.Text("No audit files available."))
    selected_audit = audit_files[0]
    audit_data = json.loads(selected_audit.read_text(encoding="utf-8"))
    summary_path = docs_path / "summary" / selected_audit.relative_to(docs_path / "audit")
    summary_path = summary_path.with_name(summary_path.name.replace(".audit", ""))
    summary_path = summary_path.with_suffix(".summary.json")
    summary_data = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}

    tabs = ft.Tabs(
        tabs=[
            ft.Tab(text="Audit", content=_audit_tab(audit_data)),
            ft.Tab(text="Snippets", content=_snippets_tab(audit_data)),
            ft.Tab(text="Summary", content=_summary_tab(summary_data)),
            ft.Tab(text="Dependencies", content=_deps_tab(summary_data)),
        ]
    )

    header = ft.Column(
        controls=[
            ft.Text(audit_data["path"], size=22, weight="bold"),
            ft.Text(f"{audit_data.get('scriptType')} • Score {audit_data['score_1_10']['overall']:.1f}"),
        ]
    )

    body = ft.Column(
        controls=[
            header,
            tabs,
        ],
        expand=True,
    )

    return make_view(
        "/file-review",
        ["Results", "File Review", audit_data["path"]],
        body,
        actions=lambda: [
            primary_action("Publish to Git", lambda _: page.go("/settings")),
            ft.OutlinedButton("Export file.audit.json", on_click=lambda _: page.launch_url(str(selected_audit))),
        ],
    )


def _audit_tab(audit: dict) -> ft.Control:
    hotspots = audit.get("hotspots", [])
    summary_card = ft.Container(
        bgcolor="#FFFFFF",
        padding=16,
        border_radius=8,
        content=ft.Column(
            controls=[
                ft.Text("File Summary", size=18, weight="bold"),
                ft.Text(f"NApiVersion: {audit.get('apiVersion')}"),
                ft.Text(f"NScriptType: {audit.get('scriptType')}"),
                ft.Text(f"Hotspots: {len(hotspots)}"),
            ]
        ),
    )
    hotspot_cards = []
    for hotspot in hotspots:
        hotspot_cards.append(
            ft.Container(
                bgcolor="#FFFFFF",
                padding=16,
                border_radius=8,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                badges.severity_badge(hotspot["severity"]),
                                badges.score_badge(hotspot["score_1_10"]),
                                ft.Text(hotspot["title"], weight="bold"),
                            ],
                            spacing=12,
                        ),
                        ft.Text(f"Lines {hotspot['location']['startLine']}-{hotspot['location']['endLine']}"),
                        ft.Text("\n".join(hotspot["evidence_excerpt"]), font_family="Consolas"),
                        ft.Text("Recommendations:", weight="bold"),
                        ft.Column([ft.Text(f"- {rec}") for rec in hotspot["recommendations"]]),
                    ]
                ),
            )
        )
    return ft.Column(controls=[summary_card, *hotspot_cards], spacing=16, scroll="auto")


def _snippets_tab(audit: dict) -> ft.Control:
    hotspots = audit.get("hotspots", [])
    code_blocks = []
    for hotspot in hotspots:
        lines = []
        for numbered in hotspot["evidence_excerpt"]:
            try:
                line_num, code = numbered.split("|", 1)
                lines.append((int(line_num), code))
            except ValueError:
                lines.append((0, numbered))
        code_blocks.append(
            ft.Container(
                padding=12,
                content=ft.Column(
                    controls=[
                        ft.Text(f"{hotspot['title']}"),
                        code_viewer.render_snippet(lines),
                        ft.Row(
                            controls=[
                                ft.TextButton("Copy snippet", on_click=lambda _: None),
                                ft.TextButton("Copy line range", on_click=lambda _, h=hotspot: None),
                            ]
                        ),
                    ]
                ),
            )
        )
    return ft.Column(code_blocks, scroll="auto")


def _summary_tab(summary: dict) -> ft.Control:
    entries = summary.get("entry_points", [])
    functions = summary.get("functions", [])
    return ft.Column(
        controls=[
            ft.Text("Entry Points", size=18, weight="bold"),
            *(ft.Text(f"- {entry['name']} ({entry['lines']}) — {entry['role']}") for entry in entries),
            ft.Text("Functions", size=18, weight="bold"),
            *(ft.Text(f"- {fn['name']} [{fn['kind']}] {fn['lines']}") for fn in functions),
            ft.Row(
                controls=[
                    ft.TextButton("Download .md", on_click=lambda _: None),
                    ft.TextButton("Download .summary.json", on_click=lambda _: None),
                ]
            ),
        ],
        scroll="auto",
    )


def _deps_tab(summary: dict) -> ft.Control:
    modules = summary.get("modules_used", [])
    call_graph = summary.get("call_graph_lite", [])
    return ft.Column(
        controls=[
            ft.Text("Imports", size=18, weight="bold"),
            *(ft.Text(f"- {module}") for module in modules),
            ft.Text("Call Graph", size=18, weight="bold"),
            *(ft.Text(f"{edge.get('from')} -> {edge.get('to')}") for edge in call_graph),
            ft.Text("Risky dependencies", size=18, weight="bold"),
            ft.Text("Automatically evaluated in deterministic layer."),
        ],
        scroll="auto",
    )
