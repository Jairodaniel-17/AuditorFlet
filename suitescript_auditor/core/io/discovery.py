"""File discovery utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class SourceFile:
    path: Path
    rel_path: Path
    size: int


def discover(root: Path, patterns: Iterable[str] | None = None) -> List[SourceFile]:
    patterns = list(patterns or ["*.js"])
    results: List[SourceFile] = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if not _match(filename, patterns):
                continue
            path = Path(dirpath) / filename
            rel = path.relative_to(root)
            results.append(SourceFile(path=path, rel_path=rel, size=path.stat().st_size))
    return results


def _match(filename: str, patterns: Iterable[str]) -> bool:
    from fnmatch import fnmatch

    return any(fnmatch(filename, pattern) for pattern in patterns)
