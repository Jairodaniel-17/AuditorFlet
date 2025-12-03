"""Dialog helpers."""

from __future__ import annotations

from dataclasses import dataclass

from flet import AlertDialog, Column, Row, Text, TextField

from ..theme.tokens import typography


@dataclass
class PublishGitForm:
    repository_path: str = ""
    remote_url: str = ""
    base_branch: str = "main"
    new_branch: str = ""
    commit_message: str = ""
    include_audit: bool = True
    include_summary: bool = True
    push_changes: bool = False
    create_pr: bool = False
    pr_title: str = ""
    pr_description: str = ""


def publish_dialog(form: PublishGitForm) -> AlertDialog:
    """Create a dialog stub for Publish to Git."""

    return AlertDialog(
        title=Text("Publish to Git", size=typography.large, weight="bold"),
        content=Column(
            controls=[
                TextField(label="Repository Path", value=form.repository_path, read_only=True),
                TextField(label="Remote URL", value=form.remote_url),
                Row(
                    controls=[
                        TextField(label="Base Branch", value=form.base_branch, expand=True),
                        TextField(label="New Branch", value=form.new_branch, expand=True),
                    ]
                ),
                TextField(label="Commit message", value=form.commit_message),
            ],
            tight=True,
        ),
    )
