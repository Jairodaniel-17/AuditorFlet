from pathlib import Path

from suitescript_auditor.core.docs.writer import DocsWriter, FileDocsPayload


def test_docs_writer_creates_files(tmp_path):
    writer = DocsWriter(tmp_path / "Docs")
    payload = FileDocsPayload(
        rel_path=Path("script.js"),
        audit={
            "path": "script.js",
            "hash": "abc",
            "scriptType": "Suitelet",
            "apiVersion": "2.x",
            "score_1_10": {"overall": 8},
            "hotspots": [],
            "netsuite_specific": [],
            "fix_plan": [],
        },
        summary={
            "path": "script.js",
            "hash": "abc",
            "scriptType": "Suitelet",
            "apiVersion": "2.x",
            "overview": "test",
            "entry_points": [],
            "functions": [],
            "modules_used": [],
            "call_graph_lite": [],
        },
    )
    paths = writer.write(payload)
    assert paths["audit_json"].exists()
    assert paths["summary_md"].exists()
