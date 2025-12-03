"""New Analysis setup view."""

from __future__ import annotations

from pathlib import Path

import flet as ft

from ...core.jobs.models import JobSettings, JobSourceType
from ..shell import primary_action
from .common import make_view


def build_new_analysis(page: ft.Page, context) -> ft.View:
    project_name = ft.TextField(label="Project name", expand=True)
    source_path = ft.TextField(label="Source path (.zip or folder)", expand=True)
    source_type = ft.Dropdown(
        label="Source Type",
        options=[ft.dropdown.Option("zip"), ft.dropdown.Option("repo")],
        value="zip",
    )

    audit_checkbox = ft.Checkbox(label="Generate /Docs/audit", value=True)
    summary_checkbox = ft.Checkbox(label="Generate /Docs/summary", value=True)
    include_md_checkbox = ft.Checkbox(label="Include .md", value=True)

    llm_mode = ft.Dropdown(
        label="LLM Mode",
        options=[ft.dropdown.Option("OFF"), ft.dropdown.Option("ON")],
        value="OFF",
    )
    quality_tier = ft.Dropdown(
        label="Quality Tier",
        options=[ft.dropdown.Option("Economic"), ft.dropdown.Option("Normal"), ft.dropdown.Option("Strict")],
        value="Economic",
    )
    moe_toggle = ft.Switch(label="MoE multiexpert", value=True)

    strict_mode = ft.Switch(label="Strict SuiteScript mode", value=True)
    safety_mode = ft.Switch(label="Prioritize transaction safety", value=True)
    exclude_minified = ft.Switch(label="Exclude minified", value=True)

    preview = ft.Container(
        bgcolor="#FFFFFF",
        padding=20,
        border_radius=8,
        content=ft.Column(
            controls=[
                ft.Text("Output Preview", weight="bold"),
                ft.Text("Docs/"),
                ft.Text("  ├─ audit/"),
                ft.Text("  ├─ summary/"),
                ft.Text("  ├─ index.json"),
                ft.Text("  └─ index.md"),
            ]
        ),
    )

    def start_analysis(_):
        if not source_path.value or not project_name.value:
            page.snack_bar = ft.SnackBar(ft.Text("Project name and source path are required."), open=True)
            page.update()
            return
        settings = JobSettings(
            generate_audit=audit_checkbox.value,
            generate_summary=summary_checkbox.value,
            include_markdown=include_md_checkbox.value,
            llm_mode=llm_mode.value == "ON",
            quality_tier=quality_tier.value,
            moe_multiexpert=moe_toggle.value,
            strict_suite_script=strict_mode.value,
            prioritize_transaction_safety=safety_mode.value,
            exclude_minified=exclude_minified.value,
            llm_mode_label=llm_mode.value,
        )
        context.job_queue.submit_job(
            project_name=project_name.value,
            source=Path(source_path.value),
            source_type=JobSourceType.ZIP if source_type.value == "zip" else JobSourceType.REPOSITORY,
            settings=settings,
        )
        page.go("/")

    source_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Source", size=18, weight="bold"),
                    source_type,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("Choose...", on_click=lambda _: None),
                            source_path,
                        ]
                    ),
                    project_name,
                ]
            ),
        )
    )

    output_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Output", size=18, weight="bold"),
                    audit_checkbox,
                    summary_checkbox,
                    include_md_checkbox,
                    ft.Text("LLM", size=18, weight="bold"),
                    llm_mode,
                    quality_tier,
                    moe_toggle,
                    ft.Text("SuiteScript Options", size=18, weight="bold"),
                    strict_mode,
                    safety_mode,
                    exclude_minified,
                ]
            ),
        )
    )

    body = ft.Row(
        controls=[
            ft.Column(
                controls=[source_card, output_card, primary_action("Start Analysis", start_analysis)],
                expand=2,
                spacing=20,
            ),
            preview,
        ],
        expand=True,
    )
    return make_view(
        "/analysis/new",
        ["Processing Center", "New Analysis"],
        body,
        actions=lambda: [primary_action("Back to Processing Center", lambda _: page.go("/"))],
    )
