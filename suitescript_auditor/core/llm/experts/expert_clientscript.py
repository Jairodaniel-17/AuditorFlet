"""Client script expert stub."""

from __future__ import annotations

from .base_expert import BaseExpert, ExpertResponse


class ClientScriptExpert(BaseExpert):
    expert_name = "expert_clientscript"

    def analyze(self, dossier):
        return ExpertResponse(hotspots=[], needs_context=False)
