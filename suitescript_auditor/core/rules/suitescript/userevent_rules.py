"""User Event specific heuristics."""

from __future__ import annotations

import re
from typing import Iterable

from ..base import Hotspot, Rule, RuleContext


class AfterSubmitRewriteRule:
    rule_id = "userevent.after_submit_rewrite"
    severity = "HIGH"
    title = "afterSubmit rewriting transactions without idempotency"
    pattern = re.compile(r"afterSubmit[\s\S]*record\.(submitFields|save)", re.IGNORECASE)

    def applies(self, context: RuleContext) -> bool:
        if not context.script_type:
            return True
        return "UserEvent" in context.script_type

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        if "afterSubmit" not in context.text:
            return []
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="afterSubmit modifies records without idempotent guard (newRecord type?).",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Check executionContext to avoid recursive writes.",
                    "Introduce before/after flag or hash comparison.",
                ],
                score_1_10=3,
            )


def get_rules() -> list[Rule]:
    return [AfterSubmitRewriteRule()]
