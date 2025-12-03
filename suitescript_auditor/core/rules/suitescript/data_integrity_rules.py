"""Data integrity safeguards."""

from __future__ import annotations

import re
from typing import Iterable

from ..base import Hotspot, Rule, RuleContext


class IgnoreMandatoryRule:
    rule_id = "data_integrity.ignore_mandatory"
    severity = "HIGH"
    title = "ignoreMandatoryFields enabled"
    pattern = re.compile(r"ignoreMandatoryFields\s*:\s*true", re.IGNORECASE)

    def applies(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="ignoreMandatoryFields true without guard can corrupt data.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Add contextual guard or justification log entry.",
                    "Wrap updates in validation to ensure completeness.",
                ],
                score_1_10=3,
            )


class EmptyCatchRule:
    rule_id = "data_integrity.empty_catch"
    severity = "MED"
    title = "Empty catch block"
    pattern = re.compile(r"catch\s*\([^)]+\)\s*{\s*}", re.MULTILINE)

    def applies(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="Swallowing exceptions hides transactional errors.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "At least log the error using log.error.",
                    "Consider rethrow or compensating actions.",
                ],
                score_1_10=5,
            )


def get_rules() -> list[Rule]:
    return [IgnoreMandatoryRule(), EmptyCatchRule()]
