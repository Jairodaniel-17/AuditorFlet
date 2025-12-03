from pathlib import Path

from suitescript_auditor.core.llm import dossier
from suitescript_auditor.core.parsing.line_map import LineMap
from suitescript_auditor.core.parsing.module_resolver import ModuleImport
from suitescript_auditor.core.parsing.symbol_index import FunctionEntry
from suitescript_auditor.core.rules.base import Hotspot


def test_dossier_builder_creates_snippets():
    path = Path("example.js")
    text = "function onRequest() { return true; }"
    line_map = LineMap.from_text(text)
    header = type("Header", (), {"api_version": "2.x", "script_type": "Suitelet", "module_scope": None})
    modules = [ModuleImport(specifier="N/record", alias="record")]
    symbols = [FunctionEntry(name="onRequest", kind="Function", lines=(1, 1), signature="()", exported=True)]
    hotspots = [
        Hotspot(
            rule_id="x",
            severity="HIGH",
            title="test",
            description="desc",
            start_line=1,
            end_line=1,
            snippet=["0001| code"],
            recommendations=["fix"],
        )
    ]
    data = dossier.build_dossier(
        path=path,
        text=text,
        line_map=line_map,
        header=header,
        modules=modules,
        symbols=symbols,
        hotspots=hotspots,
        project_name="proj",
        settings={"tier": "Economic"},
    )
    assert data["file_meta"]["path"] == "example.js"
    assert data["snippets"][0]["snippet_id"] == "S1"
