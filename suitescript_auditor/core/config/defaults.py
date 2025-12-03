"""Default configuration values."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Defaults:
    llm_model: str = "openai.gpt-oss-120b"
    region: str = "us-ashburn-1"
    auth_method: str = "config_file"
    quality_tier: str = "Economic"
    max_cost_per_job: float = 5.0
    docs_dir_name: str = "Docs"


defaults = Defaults()
