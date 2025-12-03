"""Evidence verification utilities."""

from __future__ import annotations

from typing import Iterable

from .base import Hotspot


def verify_ranges(hotspots: Iterable[Hotspot]) -> list[Hotspot]:
    verified: list[Hotspot] = []
    for hotspot in hotspots:
        if not hotspot.snippet:
            hotspot.verified = False
        else:
            hotspot.verified = True
        verified.append(hotspot)
    return verified
