"""Map/Reduce heuristics."""

from __future__ import annotations

import re
from typing import Iterable

from ..base import Hotspot, Rule, RuleContext


class MissingRetryRule:
    rule_id = "mapreduce.missing_retry"
    severity = "HIGH"
    title = "Map/Reduce summarize lacks retry guard"
    pattern = re.compile(r"summarize\s*:\s*function\s*\([^)]*\)\s*{[^}]*log\.", re.DOTALL)

    def applies(self, context: RuleContext) -> bool:
        return not context.script_type or "MapReduce" in context.script_type

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        if "summarize" not in context.text:
            return []
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="Summarize stage logs errors but does not reschedule or retry.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Use summarize.output.iterator() to reschedule failed keys.",
                    "Set summary.resume and call mapContext.isRestarted for dedupe.",
                ],
                score_1_10=4,
            )


def get_rules() -> list[Rule]:
    return [MissingRetryRule()]
