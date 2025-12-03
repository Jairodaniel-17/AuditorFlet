# SuiteScript Auditor

SuiteScript Auditor is a desktop application (Tkinter) that analyzes NetSuite SuiteScript projects, generates `/Docs` with audit + summary artefacts, and surfaces risks through a corporate UI.

## Features

- Multi-job Processing Center with status tracking, cost metrics, and inspector.
- New Analysis workflow for ZIP or local repositories including SuiteScript/LLM options.
- Deterministic parsing layer (regex + heuristics) feeding governance/data-integrity/security rules.
- Docs writer that mirrors project structure (`Docs/audit`, `Docs/summary`, `index.json`/`index.md` + `Docs.zip` artifact).
- File Review experience with Audit/Snippets/Summary/Dependencies tabs.
- LLM MoE scaffolding for OCI integration and Git publish helper.

## Development

```bash
uv sync  # or pip install -e .
uv run python -m suitescript_auditor.app
```

Run tests:

```bash
uv run pytest
```
