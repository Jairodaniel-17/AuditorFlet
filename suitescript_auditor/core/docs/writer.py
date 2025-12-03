"""Docs writer orchestrating JSON/Markdown outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .markdown import render_template


@dataclass
class FileDocsPayload:
    rel_path: Path
    audit: Dict
    summary: Dict


class DocsWriter:
    def __init__(self, docs_root: Path) -> None:
        self.root = docs_root
        (self.root / "audit").mkdir(parents=True, exist_ok=True)
        (self.root / "summary").mkdir(parents=True, exist_ok=True)
        (self.root / "artifacts").mkdir(parents=True, exist_ok=True)

    def write(self, payload: FileDocsPayload) -> Dict[str, Path]:
        rel_dir = payload.rel_path.parent
        rel_name = payload.rel_path.name
        stem = rel_name.replace(".js", "")

        audit_json_path = self.root / "audit" / rel_dir / f"{rel_name}.audit.json"
        audit_md_path = self.root / "audit" / rel_dir / f"{rel_name}.audit.md"
        summary_json_path = self.root / "summary" / rel_dir / f"{rel_name}.summary.json"
        summary_md_path = self.root / "summary" / rel_dir / f"{rel_name}.summary.md"

        for path in [audit_json_path, audit_md_path, summary_json_path, summary_md_path]:
            path.parent.mkdir(parents=True, exist_ok=True)

        audit_json_path.write_text(json.dumps(payload.audit, indent=2), encoding="utf-8")
        summary_json_path.write_text(json.dumps(payload.summary, indent=2), encoding="utf-8")

        audit_md_path.write_text(
            render_template(
                "audit_file.md.j2",
                {
                    "path": str(payload.rel_path),
                    "score": payload.audit["score_1_10"],
                    "script_type": payload.audit["scriptType"],
                    "api_version": payload.audit["apiVersion"],
                    "hotspots": payload.audit["hotspots"],
                },
            ),
            encoding="utf-8",
        )

        summary_md_path.write_text(
            render_template(
                "summary_file.md.j2",
                {
                    "path": str(payload.rel_path),
                    "overview": payload.summary.get("overview", ""),
                    "entry_points": payload.summary.get("entry_points", []),
                    "functions": payload.summary.get("functions", []),
                },
            ),
            encoding="utf-8",
        )

        return {
            "audit_json": audit_json_path,
            "summary_json": summary_json_path,
            "audit_md": audit_md_path,
            "summary_md": summary_md_path,
        }
