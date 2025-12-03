"""Track LLM tokens and approximate USD cost."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CostTracker:
    tokens_input: int = 0
    tokens_output: int = 0
    usd_cost: float = 0.0
    usd_per_1k: float = 0.003  # default public preview value

    def add_usage(self, tokens_in: int, tokens_out: int) -> None:
        self.tokens_input += tokens_in
        self.tokens_output += tokens_out
        self.usd_cost += ((tokens_in + tokens_out) / 1000.0) * self.usd_per_1k

    @property
    def total_tokens(self) -> int:
        return self.tokens_input + self.tokens_output
