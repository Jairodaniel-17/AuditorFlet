"""Deterministic file dossier builder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from ..parsing.line_map import LineMap
from ..parsing.module_resolver import ModuleImport
from ..parsing.symbol_index import FunctionEntry
from ..rules.base import Hotspot


@dataclass
class Snippet:
    snippet_id: str
    start_line: int
    end_line: int
    text_numbered: list[str]
    hotspot_refs: list[str]


def build_dossier(
    *,
    path: Path,
    text: str,
    line_map: LineMap,
    header: Any,
    modules: List[ModuleImport],
    symbols: List[FunctionEntry],
    hotspots: List[Hotspot],
    project_name: str,
    settings: Dict[str, Any],
) -> Dict[str, Any]:
    snippets = _build_snippets(hotspots, line_map)
    return {
        "file_meta": {"path": str(path), "loc": line_map.loc},
        "suitescript_meta": {
            "NApiVersion": header.api_version,
            "NScriptType": header.script_type,
            "ModuleScope": header.module_scope,
        },
        "modules": [{"specifier": m.specifier, "alias": m.alias} for m in modules],
        "symbols": [
            {
                "name": s.name,
                "kind": s.kind,
                "lines": {"start": s.lines[0], "end": s.lines[1]},
                "signature": s.signature,
                "exported": s.exported,
            }
            for s in symbols
        ],
        "hotspots_static": [
            {
                "rule_id": h.rule_id,
                "severity": h.severity,
                "start_line": h.start_line,
                "end_line": h.end_line,
                "title": h.title,
            }
            for h in hotspots
        ],
        "snippets": [
            {
                "snippet_id": s.snippet_id,
                "startLine": s.start_line,
                "endLine": s.end_line,
                "text_numbered": s.text_numbered,
                "hotspot_refs": s.hotspot_refs,
            }
            for s in snippets
        ],
        "project_context": {
            "name": project_name,
            "settings": settings,
        },
    }


def _build_snippets(hotspots: List[Hotspot], line_map: LineMap) -> List[Snippet]:
    snippets: List[Snippet] = []
    for idx, hotspot in enumerate(hotspots, start=1):
        snippets.append(
            Snippet(
                snippet_id=f"S{idx}",
                start_line=hotspot.start_line,
                end_line=hotspot.end_line,
                text_numbered=line_map.numbered_text(hotspot.start_line, hotspot.end_line),
                hotspot_refs=[hotspot.rule_id],
            )
        )
    return snippets
