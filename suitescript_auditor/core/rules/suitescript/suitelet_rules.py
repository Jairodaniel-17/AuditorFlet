"""Suitelet heuristics."""

from __future__ import annotations

import re
from typing import Iterable

from ..base import Hotspot, Rule, RuleContext


class MissingPaginationRule:
    rule_id = "suitelet.missing_pagination"
    severity = "MED"
    title = "Suitelet lacks pagination while iterating search results"
    pattern = re.compile(r"response\.write\([^)]*search\.create", re.IGNORECASE)

    def applies(self, context: RuleContext) -> bool:
        return not context.script_type or "Suitelet" in context.script_type

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="Writing search results without pagination may lock UI.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Implement paginated table using form.addSublist.",
                    "Limit search results or lazy load via GET params.",
                ],
                score_1_10=5,
            )


def get_rules() -> list[Rule]:
    return [MissingPaginationRule()]
