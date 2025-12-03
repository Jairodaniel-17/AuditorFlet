"""Markdown helpers for Docs generation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(enabled_extensions=("md.j2",)),
)


def render_template(name: str, context: Dict) -> str:
    template = env.get_template(name)
    return template.render(**context)
