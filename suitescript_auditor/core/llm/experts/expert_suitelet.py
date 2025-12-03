"""Suitelet expert stub."""

from __future__ import annotations

from .base_expert import BaseExpert, ExpertResponse


class SuiteletExpert(BaseExpert):
    expert_name = "expert_suitelet"

    def analyze(self, dossier):
        return ExpertResponse(hotspots=[], needs_context=False)
