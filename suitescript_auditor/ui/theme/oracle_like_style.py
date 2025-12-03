"""Shared helpers to make controls match the corporate style."""

from __future__ import annotations

from flet import ButtonStyle, colors

from .tokens import palette, spacing, typography


def primary_button_style() -> ButtonStyle:
    """Return a filled red button style."""

    return ButtonStyle(
        color=colors.WHITE,
        bgcolor=palette.primary,
        padding=(spacing.sm, spacing.lg),
        text_style={"size": typography.base, "weight": "w600"},
        shape={"borderRadius": spacing.radius},
    )


def ghost_button_style() -> ButtonStyle:
    """Return an outlined neutral button style."""

    return ButtonStyle(
        color=palette.text_primary,
        bgcolor=palette.base_card,
        side={"color": palette.base_border, "width": 1},
        padding=(spacing.sm, spacing.lg),
        shape={"borderRadius": spacing.radius},
    )
