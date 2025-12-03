"""Score aggregation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .base import Hotspot


@dataclass
class ScoreBreakdown:
    overall: float
    risk: float
    clean_code: float
    quality: float
    flexibility: float


def compute_score(hotspots: Iterable[Hotspot]) -> ScoreBreakdown:
    high = sum(1 for h in hotspots if h.severity == "HIGH")
    med = sum(1 for h in hotspots if h.severity == "MED")
    low = sum(1 for h in hotspots if h.severity == "LOW")
    penalty = high * 2 + med * 1.2 + low * 0.5
    base = 10.0
    overall = max(1.0, base - penalty)
    return ScoreBreakdown(
        overall=overall,
        risk=max(1.0, overall - high),
        clean_code=max(1.0, overall - med * 0.5),
        quality=max(1.0, overall - low * 0.3),
        flexibility=max(1.0, overall - low * 0.2),
    )
