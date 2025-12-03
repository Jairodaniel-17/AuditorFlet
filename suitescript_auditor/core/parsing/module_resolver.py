"""Resolve AMD style define dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


DEFINE_RE = re.compile(r"define\(\s*\[(?P<deps>[^\]]+)\]\s*,\s*function\s*\((?P<params>[^)]+)\)", re.MULTILINE)


@dataclass
class ModuleImport:
    specifier: str
    alias: str


def find_modules(text: str) -> List[ModuleImport]:
    match = DEFINE_RE.search(text)
    if not match:
        return []
    deps_raw = match.group("deps").split(",")
    params_raw = match.group("params").split(",")
    modules = []
    for dep, param in zip(deps_raw, params_raw):
        spec = dep.strip().strip("'\"")
        alias = param.strip()
        modules.append(ModuleImport(specifier=spec, alias=alias))
    return modules
