"""Parse SuiteScript metadata annotations."""

from __future__ import annotations

import re
from dataclasses import dataclass


HEADER_RE = re.compile(r"@NApiVersion\s+(?P<version>[0-9.]+)")
TYPE_RE = re.compile(r"@NScriptType\s+(?P<type>[A-Za-z]+)")
MODULE_SCOPE_RE = re.compile(r"@ModuleScope\s+(?P<scope>[A-Za-z]+)")


@dataclass
class SuiteScriptHeader:
    api_version: str | None = None
    script_type: str | None = None
    module_scope: str | None = None


def parse_header(text: str) -> SuiteScriptHeader:
    version = _extract(HEADER_RE, text)
    script_type = _extract(TYPE_RE, text)
    scope = _extract(MODULE_SCOPE_RE, text)
    return SuiteScriptHeader(api_version=version, script_type=script_type, module_scope=scope)


def _extract(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1) if match else None
