"""Index json/md builder."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .markdown import render_template


def build_index(
    docs_root: Path,
    *,
    project: Dict,
    summary_scores: Dict,
    counts: Dict,
    ranking_files: List[Dict],
    top_hotspots: List[Dict],
    llm_usage: Dict,
) -> Dict[str, Path]:
    index_json = {
        "project": project,
        "settings": project.get("settings"),
        "summary_scores": summary_scores,
        "counts": counts,
        "ranking_files": ranking_files,
        "top_hotspots": top_hotspots,
        "llm_usage": llm_usage,
    }
    json_path = docs_root / "index.json"
    json_path.write_text(json.dumps(index_json, indent=2), encoding="utf-8")

    md_path = docs_root / "index.md"
    md_path.write_text(
        render_template(
            "index.md.j2",
            {
                "project": {
                    "name": project.get("name"),
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "summary_scores": summary_scores,
                "counts": counts,
                "top_hotspots": top_hotspots,
            },
        ),
        encoding="utf-8",
    )
    return {"index_json": json_path, "index_md": md_path}
