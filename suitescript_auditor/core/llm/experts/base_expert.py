"""Base class for MoE experts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ExpertResponse:
    hotspots: list[Dict[str, Any]]
    needs_context: bool = False


class BaseExpert:
    expert_name = "base"

    def analyze(self, dossier: Dict[str, Any]) -> ExpertResponse:
        return ExpertResponse(hotspots=[], needs_context=False)
