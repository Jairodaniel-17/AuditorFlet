"""Combine expert outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .experts.base_expert import BaseExpert, ExpertResponse


@dataclass
class OrchestratorResult:
    hotspots: list[dict]
    needs_context: bool


class LLMOrchestrator:
    def __init__(self, experts: Dict[str, BaseExpert] | None = None) -> None:
        self.experts = experts or {}

    def register(self, expert: BaseExpert) -> None:
        self.experts[expert.expert_name] = expert

    def analyze(self, dossier: dict, expert_names: List[str]) -> OrchestratorResult:
        combined: list[dict] = []
        needs_context = False
        for name in expert_names:
            expert = self.experts.get(name)
            if not expert:
                continue
            response: ExpertResponse = expert.analyze(dossier)
            combined.extend(response.hotspots)
            needs_context = needs_context or response.needs_context
        return OrchestratorResult(hotspots=combined, needs_context=needs_context)
