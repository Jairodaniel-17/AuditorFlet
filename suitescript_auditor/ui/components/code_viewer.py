"""Code viewer with line numbers."""

from __future__ import annotations

from typing import Iterable

from flet import Column, Container, Control, Text

from ..theme.tokens import palette, spacing, typography


def render_snippet(lines: Iterable[tuple[int, str]], highlight: set[int] | None = None) -> Control:
    """Render numbered code lines with optional highlight ranges."""

    highlight = highlight or set()
    rendered = []
    for lineno, text in lines:
        color = palette.danger if lineno in highlight else palette.text_primary
        rendered.append(
            RowLine(
                lineno=lineno,
                text=text.rstrip("\n"),
                color=color,
            ).as_control()
        )
    return Container(
        bgcolor="#0D1117",
        border_radius=spacing.radius,
        padding=spacing.md,
        content=Column(rendered, spacing=spacing.xs, scroll="auto"),
    )


class RowLine:
    """Helper to layout a single line."""

    def __init__(self, lineno: int, text: str, color: str) -> None:
        self.lineno = lineno
        self.text = text
        self.color = color

    def as_control(self) -> Control:
        return Container(
            content=Text(
                f"{self.lineno:04} | {self.text}",
                font_family="Consolas",
                color=self.color,
                size=typography.small,
            )
        )
