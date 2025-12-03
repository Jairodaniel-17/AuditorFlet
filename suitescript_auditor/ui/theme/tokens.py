"""Design tokens shared by all UI views."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    """Color palette following the corporate specification."""

    primary: str = "#C62828"  # corporate red
    primary_dark: str = "#8E0000"
    accent: str = "#1976D2"
    accent_light: str = "#63A4FF"
    success: str = "#2E7D32"
    warning: str = "#F9A825"
    danger: str = "#B71C1C"
    base_bg: str = "#F7F7F9"
    base_card: str = "#FFFFFF"
    base_border: str = "#E0E0E0"
    text_primary: str = "#1F1F1F"
    text_secondary: str = "#5C5C5C"


@dataclass(frozen=True)
class Typography:
    """Font sizes used throughout the layout."""

    font_family: str = "Segoe UI"
    base: int = 14
    small: int = 12
    medium: int = 16
    large: int = 20
    xlarge: int = 24


@dataclass(frozen=True)
class Spacing:
    """Spacing and radius constants."""

    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    radius: int = 8


palette = Palette()
typography = Typography()
spacing = Spacing()
