"""Shared utilities for view builders."""

from __future__ import annotations

import flet as ft

from typing import Callable, Iterable

from ..shell import AppShell, NavItem

NAV_ITEMS = [
    NavItem("Processing Center", "/", "dashboard"),
    NavItem("New Analysis", "/analysis/new", "play_circle"),
    NavItem("Run Log", "/run-log", "list"),
    NavItem("Results", "/results", "assessment"),
    NavItem("File Review", "/file-review", "article"),
    NavItem("Docs Browser", "/docs", "folder"),
    NavItem("History", "/history", "history"),
    NavItem("Settings", "/settings", "settings"),
]


def make_view(
    route: str,
    breadcrumb: list[str],
    body: ft.Control,
    inspector: ft.Control | None = None,
    actions: Callable[[], Iterable[ft.Control]] | None = None,
) -> ft.View:
    shell = AppShell(
        page_title=breadcrumb[-1],
        breadcrumb=breadcrumb,
        nav_items=NAV_ITEMS,
        active_route=route,
        body=body,
        inspector=inspector,
        actions_builder=actions,
    )
    return ft.View(route, [shell])
