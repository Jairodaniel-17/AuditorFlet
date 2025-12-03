"""Reusable application shell with header, sidebar and breadcrumb."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from flet import (
    Column,
    Container,
    Control,
    ElevatedButton,
    Icon,
    IconButton,
    ListTile,
    Row,
    Text,
    padding,
)
from flet import colors

from .theme.tokens import palette, spacing, typography
from .theme import oracle_like_style as style


@dataclass(frozen=True)
class NavItem:
    label: str
    route: str
    icon: str


class AppShell(Container):
    """Shell layout reused by each view."""

    def __init__(
        self,
        *,
        page_title: str,
        breadcrumb: Iterable[str],
        nav_items: list[NavItem],
        active_route: str,
        actions_builder: Callable[[], Iterable[Control]] | None = None,
        inspector: Control | None = None,
        body: Control,
    ) -> None:
        super().__init__()

        self.padding = 0
        self.expand = True
        self.content = Row(
            controls=[
                self._build_sidebar(nav_items, active_route),
                Column(
                    controls=[
                        self._build_header(page_title, actions_builder),
                        self._build_breadcrumb(breadcrumb),
                        Row(
                            controls=[
                                Container(
                                    content=body,
                                    expand=True,
                                    padding=spacing.lg,
                                    bgcolor=palette.base_bg,
                                ),
                                inspector or Container(width=0),
                            ],
                            expand=True,
                        ),
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_header(
        self, title: str, actions_builder: Callable[[], Iterable[Control]] | None
    ) -> Control:
        return Container(
            bgcolor=palette.base_card,
            padding=padding.all(spacing.lg),
            border=padding.only(bottom=1),
            border_color=palette.base_border,
            content=Row(
                controls=[
                    Row(
                        controls=[
                            Icon("cases", color=palette.primary),
                            Text(
                                "SuiteScript Auditor",
                                size=typography.xlarge,
                                weight="bold",
                                color=palette.text_primary,
                            ),
                            Text(f"/ {title}", color=palette.text_secondary),
                        ],
                    ),
                    Row(
                        controls=list(actions_builder() if actions_builder else []),
                        alignment="end",
                        expand=True,
                    ),
                ],
                alignment="spaceBetween",
            ),
        )

    def _build_sidebar(self, nav_items: list[NavItem], active_route: str) -> Control:
        entries = []
        for item in nav_items:
            entries.append(
                Container(
                    bgcolor=palette.primary if item.route == active_route else None,
                    border_radius=spacing.radius,
                    padding=spacing.sm,
                    margin=padding.symmetric(vertical=2, horizontal=4),
                    content=ListTile(
                        leading=Icon(item.icon, color=self._sidebar_text_color(item, active_route)),
                        title=Text(item.label, color=self._sidebar_text_color(item, active_route)),
                        data=item.route,
                    ),
                )
            )
        return Container(
            width=220,
            bgcolor=palette.base_card,
            padding=padding.all(spacing.md),
            content=Column(entries, expand=True, scroll="auto"),
        )

    def _sidebar_text_color(self, item: NavItem, active_route: str) -> str:
        return colors.WHITE if item.route == active_route else palette.text_primary

    def _build_breadcrumb(self, breadcrumb: Iterable[str]) -> Control:
        crumb_text = " / ".join(breadcrumb)
        return Container(
            bgcolor=palette.base_bg,
            padding=padding.symmetric(horizontal=spacing.lg, vertical=spacing.sm),
            content=Text(crumb_text, color=palette.text_secondary),
        )


def primary_action(text: str, on_click: Callable) -> ElevatedButton:
    """Create a standard primary action button."""

    btn = ElevatedButton(text, on_click=on_click)
    btn.style = style.primary_button_style()
    return btn


def secondary_icon(icon: str, tooltip: str, on_click: Callable) -> IconButton:
    """Secondary icon button used on the header."""

    return IconButton(icon, tooltip=tooltip, on_click=on_click, icon_color=palette.accent)
