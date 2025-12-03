"""Symbol index builder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .ast_js import FunctionSymbol, extract_functions


@dataclass
class FunctionEntry:
    name: str
    kind: str
    lines: tuple[int, int]
    signature: str
    exported: bool


def build_symbol_index(text: str) -> List[FunctionEntry]:
    functions: List[FunctionEntry] = []
    for symbol in extract_functions(text):
        functions.append(
            FunctionEntry(
                name=symbol.name,
                kind=symbol.kind,
                lines=(symbol.start_line, symbol.end_line),
                signature=symbol.signature,
                exported=symbol.exported,
            )
        )
    return functions
