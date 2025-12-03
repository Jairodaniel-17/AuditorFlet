"""Reusable cards for metrics and sections."""

from __future__ import annotations

from typing import Iterable

from flet import Column, Container, Control, Row, Text

from ..theme.tokens import palette, spacing, typography


def metric_card(title: str, value: str, subtitle: str | None = None) -> Control:
    """Display a bold metric with optional subtitle."""

    return Container(
        bgcolor=palette.base_card,
        border_radius=spacing.radius,
        padding=spacing.lg,
        border={"color": palette.base_border, "width": 1},
        content=Column(
            controls=[
                Text(title.upper(), size=typography.small, color=palette.text_secondary),
                Text(value, size=typography.xlarge, weight="bold", color=palette.text_primary),
                Text(subtitle or "", size=typography.small, color=palette.text_secondary),
            ],
            spacing=spacing.xs,
        ),
    )


def card_section(title: str, content: Iterable[Control]) -> Control:
    """Building block for sections with header and content."""

    return Container(
        bgcolor=palette.base_card,
        border_radius=spacing.radius,
        padding=spacing.lg,
        border={"color": palette.base_border, "width": 1},
        content=Column(
            controls=[
                Text(title, size=typography.large, weight="bold", color=palette.text_primary),
                Container(height=spacing.xs),
                Column(list(content), spacing=spacing.sm),
            ]
        ),
    )


def horizontal_metrics(items: Iterable[Control]) -> Control:
    return Row(list(items), alignment="spaceBetween")
