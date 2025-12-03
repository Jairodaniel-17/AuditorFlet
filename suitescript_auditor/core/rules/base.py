"""Rule infrastructure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..parsing.line_map import LineMap


@dataclass
class RuleContext:
    path: str
    text: str
    script_type: str | None
    api_version: str | None
    line_map: "LineMap"


@dataclass
class Hotspot:
    rule_id: str
    severity: str
    title: str
    description: str
    start_line: int
    end_line: int
    snippet: list[str]
    recommendations: list[str]
    symbol: str | None = None
    verified: bool = True
    score_1_10: float = 5.0


class Rule(Protocol):
    rule_id: str
    severity: str
    title: str

    def applies(self, context: RuleContext) -> bool:
        ...

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        ...


class RuleEngine:
    def __init__(self, rules: Iterable[Rule]) -> None:
        self.rules = list(rules)

    def run(self, context: RuleContext) -> List[Hotspot]:
        findings: List[Hotspot] = []
        for rule in self.rules:
            if not rule.applies(context):
                continue
            for finding in rule.evaluate(context):
                findings.append(finding)
        return findings
