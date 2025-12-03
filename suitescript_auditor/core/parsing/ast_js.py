"""JavaScript AST helpers.

For now we expose lightweight detection routines built on regular
expressions while keeping the public API compatible with a future
Tree-sitter backed implementation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class FunctionSymbol:
    name: str
    kind: str
    start_line: int
    end_line: int
    signature: str
    exported: bool


FUNC_DECL_RE = re.compile(
    r"(?P<export>exports\.)?(function|const|let|var)\s+(?P<name>[a-zA-Z0-9_]+)\s*"
    r"(?P<signature>\([^)]*\))",
    re.MULTILINE,
)


def extract_functions(text: str) -> List[FunctionSymbol]:
    """Heuristic extraction of function declarations and arrow functions."""

    lines = text.splitlines()
    results: List[FunctionSymbol] = []
    for match in FUNC_DECL_RE.finditer(text):
        name = match.group("name")
        signature = match.group("signature")
        start_line = text[: match.start()].count("\n") + 1
        snippet_after = text[match.start() :].split("{", 1)
        block_body = snippet_after[1] if len(snippet_after) > 1 else ""
        line_count = block_body.split("}", 1)[0].count("\n")
        end_line = start_line + line_count
        exported = bool(match.group("export"))
        kind = "Arrow Function" if "=>" in lines[start_line - 1 : end_line + 1] else "Function Declaration"
        results.append(
            FunctionSymbol(
                name=name,
                kind=kind,
                start_line=start_line,
                end_line=end_line,
                signature=signature,
                exported=exported,
            )
        )
    return results
