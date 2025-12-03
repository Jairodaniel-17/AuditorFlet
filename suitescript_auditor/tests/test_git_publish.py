from pathlib import Path

from suitescript_auditor.core.git import publish


def test_run_git_invokes_subprocess(monkeypatch, tmp_path):
    calls = []

    class DummyCompleted:
        def __init__(self):
            self.returncode = 0
            self.stdout = "ok"
            self.stderr = ""

    def fake_run(cmd, cwd, capture_output, text, check):
        calls.append((cmd, cwd))
        return DummyCompleted()

    monkeypatch.setattr(publish, "subprocess", type("S", (), {"run": fake_run}))
    output = publish.run_git(["status"], tmp_path)
    assert "ok" in output
    assert calls[0][0][1] == "status"


def test_publish_docs_sequence(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    docs = repo / "Docs"
    docs.mkdir()
    include = [docs]
    recorded = []

    def fake_run_git(args, cwd):
        recorded.append((tuple(args), cwd))
        return ""

    monkeypatch.setattr(publish, "run_git", fake_run_git)
    info = publish.publish_docs(
        repo_path=repo,
        branch_name="docs/audit",
        base_branch="main",
        commit_message="docs update",
        include_paths=include,
        push=True,
    )
    assert info["branch"] == "docs/audit"
    assert any("push" in cmd for cmd, _ in recorded)
