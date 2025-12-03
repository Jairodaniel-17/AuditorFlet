"""
Top-level package for the SuiteScript Auditor desktop application.

The package exposes the ``__version__`` constant along with helpers
that simplify bootstrapping the Flet UI from external launchers or
from ``python -m suitescript_auditor``.
"""

from __future__ import annotations

__all__ = ["__version__", "run_app"]

__version__ = "0.1.0"


def run_app() -> None:
    """Run the Flet application entrypoint."""
    from .app import main

    main()
