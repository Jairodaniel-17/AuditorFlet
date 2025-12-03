"""Map/Reduce expert stub."""

from __future__ import annotations

from .base_expert import BaseExpert, ExpertResponse


class MapReduceExpert(BaseExpert):
    expert_name = "expert_mapreduce"

    def analyze(self, dossier):
        return ExpertResponse(hotspots=[], needs_context=False)
