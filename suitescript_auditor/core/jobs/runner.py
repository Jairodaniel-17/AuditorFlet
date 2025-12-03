"""Background pipeline that analyses SuiteScript projects."""

from __future__ import annotations

import json
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List

from ..config.defaults import defaults
from ..docs.index_builder import build_index
from ..docs.writer import DocsWriter, FileDocsPayload
from ..io import discovery, hashing, workspace, zip_handler
from ..parsing import module_resolver, suitescript_header
from ..parsing.line_map import LineMap
from ..parsing.symbol_index import build_symbol_index
from ..rules import verifier
from ..rules.base import RuleContext
from ..rules.scoring import compute_score
from ..rules.suitescript import (
    clientscript_rules,
    data_integrity_rules,
    governance_rules,
    mapreduce_rules,
    security_rules,
    suitelet_rules,
    userevent_rules,
)
from ..rules.base import Hotspot, RuleEngine
from ..llm import dossier, router
from ..llm.orchestrator import LLMOrchestrator
from ..llm.experts.expert_clientscript import ClientScriptExpert
from ..llm.experts.expert_mapreduce import MapReduceExpert
from ..llm.experts.expert_security import SecurityExpert
from ..llm.experts.expert_suitelet import SuiteletExpert
from ..llm.experts.expert_userevent import UserEventExpert
from ..jobs.cost_tracker import CostTracker
from .models import FileArtifact, Job, JobResult, JobStage, JobStatus


class JobRunner:
    """Executes a job pipeline in a worker thread."""

    def __init__(self) -> None:
        self.workspace = workspace.WorkspaceManager()
        self.rule_engine = RuleEngine(
            governance_rules.get_rules()
            + data_integrity_rules.get_rules()
            + security_rules.get_rules()
            + userevent_rules.get_rules()
            + suitelet_rules.get_rules()
            + clientscript_rules.get_rules()
            + mapreduce_rules.get_rules()
        )
        self.orchestrator = LLMOrchestrator(
            {
                "expert_clientscript": ClientScriptExpert(),
                "expert_userevent": UserEventExpert(),
                "expert_suitelet": SuiteletExpert(),
                "expert_mapreduce": MapReduceExpert(),
                "expert_security": SecurityExpert(),
            }
        )

    def run(self, job: Job, on_update: Callable[[Job], None] | None = None) -> JobResult:
        job.status = JobStatus.RUNNING
        job.stage = JobStage.PREPARING
        self._notify(job, on_update)

        workdir = self.workspace.create(job.id)
        source_root = self._prepare_source(job, workdir)

        job.stage = JobStage.DISCOVERING
        self._notify(job, on_update)
        files = discovery.discover(source_root)
        job.files_total = len(files)

        docs_dir = source_root / defaults.docs_dir_name
        writer = DocsWriter(docs_dir)
        artifacts: List[FileArtifact] = []
        cost_tracker = CostTracker()

        job.stage = JobStage.PARSING
        self._notify(job, on_update)
        ranking_files: List[Dict] = []
        global_hotspots: List[Dict] = []

        for idx, source_file in enumerate(files, start=1):
            job.current_file = str(source_file.rel_path)
            job.files_processed = idx
            job.progress = idx / max(1, job.files_total)
            self._notify(job, on_update)

            text = source_file.path.read_text(encoding="utf-8", errors="ignore")
            line_map = LineMap.from_text(text)
            header = suitescript_header.parse_header(text)
            modules = module_resolver.find_modules(text)
            symbols = build_symbol_index(text)
            context = RuleContext(
                path=str(source_file.rel_path),
                text=text,
                script_type=header.script_type,
                api_version=header.api_version,
                line_map=line_map,
            )
            hotspots = verifier.verify_ranges(self.rule_engine.run(context))

            if job.settings.llm_mode:
                expert_route = router.route(header.script_type)
                dossier_payload = dossier.build_dossier(
                    path=source_file.rel_path,
                    text=text,
                    line_map=line_map,
                    header=header,
                    modules=modules,
                    symbols=symbols,
                    hotspots=hotspots,
                    project_name=job.project_name,
                    settings=job.settings.__dict__,
                )
                llm_result = self.orchestrator.analyze(dossier_payload, expert_route.experts)
                cost_tracker.add_usage(tokens_in=200, tokens_out=50)
            else:
                llm_result = None

            file_score = compute_score(hotspots)
            audit = self._build_audit_payload(
                job=job,
                source_file=source_file,
                header=header,
                line_map=line_map,
                hotspots=hotspots,
                score=file_score,
            )
            summary = self._build_summary_payload(
                job=job,
                source_file=source_file,
                header=header,
                symbols=symbols,
                modules=modules,
            )
            paths = writer.write(
                FileDocsPayload(rel_path=source_file.rel_path, audit=audit, summary=summary)
            )
            artifacts.append(
                FileArtifact(
                    path=source_file.path,
                    audit_json=audit,
                    summary_json=summary,
                    audit_markdown=paths["audit_md"].read_text(encoding="utf-8"),
                    summary_markdown=paths["summary_md"].read_text(encoding="utf-8"),
                )
            )
            ranking_files.append(
                {
                    "path": str(source_file.rel_path),
                    "score_overall": file_score.overall,
                    "hotspots_high": len([h for h in hotspots if h.severity == "HIGH"]),
                    "scriptType": header.script_type,
                }
            )
            for hotspot in hotspots:
                global_hotspots.append(
                    {
                        "severity": hotspot.severity,
                        "title": hotspot.title,
                        "file": str(source_file.rel_path),
                        "line_range": f"{hotspot.start_line}-{hotspot.end_line}",
                    }
                )

        job.stage = JobStage.WRITING
        self._notify(job, on_update)

        top_hotspots = sorted(
            global_hotspots, key=lambda h: {"HIGH": 0, "MED": 1, "LOW": 2}.get(h["severity"], 3)
        )[:10]

        counts = {
            "files": len(ranking_files),
            "critical_files": sum(1 for r in ranking_files if r["score_overall"] <= 3),
            "hotspots_high": sum(1 for h in global_hotspots if h["severity"] == "HIGH"),
            "hotspots_med": sum(1 for h in global_hotspots if h["severity"] == "MED"),
            "hotspots_low": sum(1 for h in global_hotspots if h["severity"] == "LOW"),
        }
        summary_scores = {
            "overall": sum(r["score_overall"] for r in ranking_files) / max(1, len(ranking_files)),
        }
        project_payload = {
            "name": job.project_name,
            "source": str(job.source),
            "run_id": job.id,
            "timestamp": datetime.utcnow().isoformat(),
            "settings": job.settings.__dict__,
        }
        build_index(
            docs_root=docs_dir,
            project=project_payload,
            summary_scores=summary_scores,
            counts=counts,
            ranking_files=ranking_files,
            top_hotspots=top_hotspots,
            llm_usage={
                "tokens_in": cost_tracker.tokens_input,
                "tokens_out": cost_tracker.tokens_output,
                "cost_total": cost_tracker.usd_cost,
            },
        )

        job.stage = JobStage.PACKAGING
        self._notify(job, on_update)
        archive_path = shutil.make_archive(str(docs_dir / "artifacts/Docs"), "zip", docs_dir)
        job.results = {"docs_path": str(docs_dir), "archive": archive_path}
        job.stage = JobStage.COMPLETE
        job.status = JobStatus.COMPLETED
        job.llm_cost = cost_tracker.usd_cost
        job.progress = 1.0
        self._notify(job, on_update)

        return JobResult(
            job=job,
            artifacts=artifacts,
            docs_path=docs_dir,
            index_json=json.loads((docs_dir / "index.json").read_text(encoding="utf-8")),
        )

    def _prepare_source(self, job: Job, workdir: Path) -> Path:
        if job.source_type.value == "zip":
            return zip_handler.extract(job.source, workdir)
        return job.source

    def _build_audit_payload(self, job: Job, source_file, header, line_map, hotspots, score):
        file_hash = hashing.sha256_file(source_file.path)
        formatted_hotspots = []
        for idx, h in enumerate(hotspots, start=1):
            formatted_hotspots.append(
                {
                    "severity": h.severity,
                    "score_1_10": h.score_1_10,
                    "title": h.title,
                    "location": {
                        "startLine": h.start_line,
                        "endLine": h.end_line,
                        "symbol": h.symbol,
                    },
                    "snippet_id": f"S{idx}",
                    "evidence_excerpt": h.snippet[:40],
                    "recommendations": h.recommendations,
                    "verified": h.verified,
                }
            )
        return {
            "path": str(source_file.rel_path),
            "hash": file_hash,
            "scriptType": header.script_type,
            "apiVersion": header.api_version,
            "score_1_10": score.__dict__,
            "hotspots": formatted_hotspots,
            "netsuite_specific": [],
            "fix_plan": [h.title for h in hotspots[:7]],
        }

    def _build_summary_payload(self, job, source_file, header, symbols, modules):
        file_hash = hashing.sha256_file(source_file.path)
        entry_points = [
            {
                "name": fn.name,
                "signature": fn.signature,
                "lines": f"{fn.lines[0]}-{fn.lines[1]}",
                "role": "Entry" if fn.exported else "Internal",
            }
            for fn in symbols
            if fn.name in {"onRequest", "beforeSubmit", "afterSubmit", "execute"}
        ]
        functions = [
            {
                "name": fn.name,
                "kind": fn.kind,
                "signature": fn.signature,
                "lines": f"{fn.lines[0]}-{fn.lines[1]}",
                "role": "Exported" if fn.exported else "Internal",
            }
            for fn in symbols
        ]
        return {
            "path": str(source_file.rel_path),
            "hash": file_hash,
            "scriptType": header.script_type,
            "apiVersion": header.api_version,
            "overview": f"{source_file.rel_path} contains {len(symbols)} functions and {len(modules)} modules.",
            "entry_points": entry_points,
            "functions": functions,
            "modules_used": [m.specifier for m in modules],
            "call_graph_lite": [],
        }

    def _notify(self, job: Job, callback: Callable[[Job], None] | None) -> None:
        if callback:
            callback(job)
