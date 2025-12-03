"""User Event expert stub."""

from __future__ import annotations

from .base_expert import BaseExpert, ExpertResponse


class UserEventExpert(BaseExpert):
    expert_name = "expert_userevent"

    def analyze(self, dossier):
        return ExpertResponse(hotspots=[], needs_context=False)
