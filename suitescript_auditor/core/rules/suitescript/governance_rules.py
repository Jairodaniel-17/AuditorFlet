"""Governance rules detecting heavy operations in loops."""

from __future__ import annotations

import re
from typing import Iterable

from ..base import Hotspot, Rule, RuleContext


class SearchEachLoopRule:
    rule_id = "governance.search_each_loop"
    severity = "HIGH"
    title = "search.run().each inside loop"

    pattern = re.compile(r"(for|while)\s*\([^)]*\)\s*{[^}]*search\.run\(\)\.each", re.DOTALL)

    def applies(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="search.run().each inside tight loop may exhaust governance units.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Move the each() call outside the loop or paginate results.",
                    "Cache search results before iterating.",
                ],
                score_1_10=2,
            )


class RecordLoadInLoopRule:
    rule_id = "governance.record_load_loop"
    severity = "MED"
    title = "Repeated record.load/save inside loop"

    pattern = re.compile(r"(for|while)[^{]+{[^}]*record\.(load|save)", re.DOTALL)

    def applies(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="record.load/save in loops is prone to governance spikes.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Batch record updates and persist outside of iteration.",
                    "Review whether field changes require multiple saves.",
                ],
                score_1_10=4,
            )


def get_rules() -> list[Rule]:
    return [SearchEachLoopRule(), RecordLoadInLoopRule()]
