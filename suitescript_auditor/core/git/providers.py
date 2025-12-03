"""Git provider registry placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GitProvider:
    name: str
    remote_url: str


PROVIDERS = {
    "github": GitProvider(name="github", remote_url="https://github.com"),
    "gitlab": GitProvider(name="gitlab", remote_url="https://gitlab.com"),
}
