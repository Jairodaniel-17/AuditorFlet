"""Keyring wrappers."""

from __future__ import annotations

import keyring

SERVICE = "SuiteScriptAuditor"


def save_secret(name: str, value: str) -> None:
    keyring.set_password(SERVICE, name, value)


def load_secret(name: str) -> str | None:
    return keyring.get_password(SERVICE, name)
