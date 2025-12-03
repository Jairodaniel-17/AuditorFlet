"""Severity badges and score chips."""

from __future__ import annotations

from flet import Container, Text

from ..theme.tokens import palette, spacing, typography


SEVERITY_COLORS = {
    "HIGH": palette.danger,
    "MED": palette.warning,
    "LOW": palette.accent,
}


def severity_badge(level: str) -> Container:
    color = SEVERITY_COLORS.get(level, palette.text_secondary)
    return Container(
        bgcolor=color,
        padding=(spacing.xs, spacing.sm),
        border_radius=spacing.radius,
        content=Text(level, color="white", size=typography.small, weight="bold"),
    )


def score_badge(score: float) -> Container:
    if score <= 3:
        color = palette.danger
    elif score <= 6:
        color = palette.warning
    else:
        color = palette.success
    return Container(
        bgcolor=color,
        padding=(spacing.xs, spacing.sm),
        border_radius=spacing.radius,
        content=Text(f"{score:.1f}", color="white", size=typography.small, weight="bold"),
    )
