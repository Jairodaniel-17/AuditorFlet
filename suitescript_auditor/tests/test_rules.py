from suitescript_auditor.core.rules.base import RuleContext
from suitescript_auditor.core.rules.suitescript.security_rules import SecretLiteralRule
from suitescript_auditor.core.parsing.line_map import LineMap


def test_secret_literal_detection():
    text = "const token = 'abcd1234ABCD5678';"
    context = RuleContext(
        path="foo.js",
        text=text,
        script_type=None,
        api_version=None,
        line_map=LineMap.from_text(text),
    )
    rule = SecretLiteralRule()
    findings = list(rule.evaluate(context))
    assert findings
    assert findings[0].severity == "HIGH"
