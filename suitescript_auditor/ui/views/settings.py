"""Settings view."""

from __future__ import annotations

import flet as ft

from ...core.config.defaults import defaults
from ..shell import primary_action
from .common import make_view


def build_settings(page: ft.Page, context) -> ft.View:
    oci_section = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("OCI", size=18, weight="bold"),
                    ft.TextField(label="Region/Endpoint", value=defaults.region),
                    ft.TextField(label="Model name", value=defaults.llm_model),
                    ft.Dropdown(
                        label="Auth method",
                        options=[ft.dropdown.Option("config file"), ft.dropdown.Option("instance principal")],
                        value=defaults.auth_method,
                    ),
                    primary_action("Test connection", lambda _: None),
                ]
            ),
        )
    )

    limits_section = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("LLM limits", size=18, weight="bold"),
                    ft.TextField(label="Max cost per job (USD)", value=str(defaults.max_cost_per_job)),
                    ft.TextField(label="Max tokens per file", value="2000"),
                    ft.Dropdown(
                        label="Tier presets",
                        options=[
                            ft.dropdown.Option("Economic"),
                            ft.dropdown.Option("Normal"),
                            ft.dropdown.Option("Strict"),
                        ],
                        value="Economic",
                    ),
                ]
            ),
        )
    )

    git_section = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Git", size=18, weight="bold"),
                    ft.TextField(label="Provider", value="GitHub"),
                    ft.TextField(label="Default remote", value="origin"),
                    ft.TextField(label="Token storage", value="Stored in keyring"),
                    primary_action("Test push permissions", lambda _: None),
                ]
            ),
        )
    )

    ui_section = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("UI", size=18, weight="bold"),
                    ft.Dropdown(label="Theme", options=[ft.dropdown.Option("Light")], value="Light"),
                    ft.Dropdown(label="Primary color", options=[ft.dropdown.Option("Red")], value="Red"),
                    ft.Dropdown(label="Accent color", options=[ft.dropdown.Option("Blue")], value="Blue"),
                    ft.Slider(label="Font size", min=12, max=18, divisions=6, value=14),
                ]
            ),
        )
    )

    body = ft.Column(
        controls=[
            oci_section,
            limits_section,
            git_section,
            ui_section,
        ],
        scroll="auto",
    )
    return make_view(
        "/settings",
        ["Processing Center", "Settings"],
        body,
        actions=lambda: [primary_action("Back", lambda _: page.go("/"))],
    )
