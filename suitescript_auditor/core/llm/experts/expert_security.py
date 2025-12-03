"""Security expert stub."""

from __future__ import annotations

from .base_expert import BaseExpert, ExpertResponse


class SecurityExpert(BaseExpert):
    expert_name = "expert_security"

    def analyze(self, dossier):
        return ExpertResponse(hotspots=[], needs_context=False)
