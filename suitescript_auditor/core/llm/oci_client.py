"""OCI LangChain client wrapper (stub)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OCIConfig:
    region: str
    model: str
    auth_method: str = "config_file"


class OCIClient:
    """Very small stub used until live integration is configured."""

    def __init__(self, config: OCIConfig) -> None:
        self.config = config

    def run_completion(self, prompt: str) -> dict:
        """Return deterministic placeholder output."""

        return {"needs_context": True, "prompt": prompt[:120]}
