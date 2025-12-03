"""LLM expert router."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExpertRoute:
    experts: list[str]


def route(script_type: str | None) -> ExpertRoute:
    if not script_type:
        return ExpertRoute(experts=["expert_security"])
    if "ClientScript" in script_type:
        return ExpertRoute(experts=["expert_clientscript", "expert_security"])
    if "UserEvent" in script_type:
        return ExpertRoute(experts=["expert_userevent", "expert_security"])
    if "Suitelet" in script_type:
        return ExpertRoute(experts=["expert_suitelet", "expert_security"])
    if "MapReduce" in script_type:
        return ExpertRoute(experts=["expert_mapreduce", "expert_security"])
    return ExpertRoute(experts=["expert_security"])
