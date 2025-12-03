"""Security rules."""

from __future__ import annotations

import re
from typing import Iterable

from ..base import Hotspot, Rule, RuleContext


class HttpsAllowlistRule:
    rule_id = "security.https_allowlist"
    severity = "HIGH"
    title = "HTTPS request without allowlist"
    pattern = re.compile(r"https\.request\([^)]*['\"]http", re.IGNORECASE)

    def applies(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="External call lacks explicit allowlist mention.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Inject target URL only from configuration or allowlist.",
                    "Document the remote endpoint in Settings > Git section.",
                ],
                score_1_10=2,
            )


class SecretLiteralRule:
    rule_id = "security.secret_literal"
    severity = "HIGH"
    title = "Possible secret literal"
    pattern = re.compile(r"(token|secret|password)\s*[:=]\s*['\"][A-Za-z0-9+/=]{8,}", re.IGNORECASE)

    def applies(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            redacted = [line.replace(match.group(0), "***REDACTED***") for line in context.line_map.numbered_text(lr.start, lr.end)]
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="Potential secret embedded directly in source.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=redacted,
                recommendations=[
                    "Move credentials to keyring-backed storage.",
                    "Replace literals with configuration references.",
                ],
                score_1_10=1,
            )


class EvalUsageRule:
    rule_id = "security.eval_usage"
    severity = "HIGH"
    title = "Use of eval/new Function"
    pattern = re.compile(r"\b(eval|new\s+Function)\b")

    def applies(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> Iterable[Hotspot]:
        for match in self.pattern.finditer(context.text):
            lr = context.line_map.to_range(match.start(), match.end())
            yield Hotspot(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                description="Dynamic code execution is risky in SuiteScript.",
                start_line=lr.start,
                end_line=lr.end,
                snippet=context.line_map.numbered_text(lr.start, lr.end),
                recommendations=[
                    "Remove eval usage and rely on explicit module references.",
                    "Validate inputs before executing dynamic expressions.",
                ],
                score_1_10=2,
            )


def get_rules() -> list[Rule]:
    return [HttpsAllowlistRule(), SecretLiteralRule(), EvalUsageRule()]
