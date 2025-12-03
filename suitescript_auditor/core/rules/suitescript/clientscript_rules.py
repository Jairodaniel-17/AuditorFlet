"""Client script heuristics."""

from __future__ import annotations

import re
from typing import Iterable

from ..base import Hotspot, Rule, RuleContext


class HeavyLoopDomRule:
    rule_id = "clientscript.heavy_loop_dom"
    severity = "MED"
    title = "Client script loops touching DOM extensively"
    pattern = re.compile(r"for\s*\([^)]*\)\s*{[^}]*document\.", re.DOTALL)

    def applies(self, context: RuleContext) -> bool:
        return not context.script_type or "ClientScript" in context.script_type

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="DOM mutations inside loops degrade UI responsiveness.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Batch DOM updates or use document fragments.",
                    "Precompute values before touching the DOM inside loops.",
                ],
                score_1_10=5,
            )


def get_rules() -> list[Rule]:
    return [HeavyLoopDomRule()]
