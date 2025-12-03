"""Git publication helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def publish_docs(
    *,
    repo_path: Path,
    branch_name: str,
    base_branch: str,
    commit_message: str,
    include_paths: list[Path],
    push: bool = False,
) -> Dict[str, str]:
    run_git(["checkout", base_branch], cwd=repo_path)
    run_git(["checkout", "-B", branch_name], cwd=repo_path)
    for path in include_paths:
        run_git(["add", str(path)], cwd=repo_path)
    run_git(["commit", "-m", commit_message], cwd=repo_path)
    if push:
        run_git(["push", "-u", "origin", branch_name], cwd=repo_path)
    return {"branch": branch_name, "commit": commit_message}
