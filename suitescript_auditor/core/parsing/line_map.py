"""Line map helpers to map offsets to line numbers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class LineRange:
    start: int
    end: int


class LineMap:
    def __init__(self, lines: List[str]) -> None:
        self._lines = lines
        self._offsets: List[int] = []
        offset = 0
        for line in lines:
            self._offsets.append(offset)
            offset += len(line)

    @classmethod
    def from_text(cls, text: str) -> "LineMap":
        lines = text.splitlines(keepends=True)
        if not lines:
            lines = [""]
        return cls(lines)

    def to_range(self, start_offset: int, end_offset: int) -> LineRange:
        start = self._offset_to_line(start_offset)
        adjusted_end = max(end_offset - 1, start_offset)
        end = self._offset_to_line(adjusted_end)
        return LineRange(start=start + 1, end=end + 1)

    def _offset_to_line(self, offset: int) -> int:
        for idx, start in enumerate(self._offsets):
            next_start = self._offsets[idx + 1] if idx + 1 < len(self._offsets) else None
            if next_start is None or offset < next_start:
                return idx
        return len(self._offsets) - 1

    def numbered_text(self, start_line: int, end_line: int) -> List[str]:
        text = []
        for idx in range(start_line - 1, min(end_line, len(self._lines))):
            prefix = f"{idx + 1:04}| "
            text.append(prefix + self._lines[idx].rstrip("\n"))
        return text

    @property
    def loc(self) -> int:
        return len(self._lines)
