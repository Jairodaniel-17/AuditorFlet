"""ZIP extraction helpers with zip-slip prevention."""

from __future__ import annotations

import zipfile
from pathlib import Path


def extract(zip_path: Path, target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            _extract_member(zf, member, target)
    return target


def _extract_member(zf: zipfile.ZipFile, member: zipfile.ZipInfo, target: Path) -> None:
    if member.is_dir():
        (target / member.filename).mkdir(parents=True, exist_ok=True)
        return
    resolved = (target / member.filename).resolve()
    if target.resolve() not in resolved.parents and resolved != target.resolve():
        raise ValueError("Zip entry escapes target directory")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(member) as source, open(resolved, "wb") as dest:
        dest.write(source.read())
