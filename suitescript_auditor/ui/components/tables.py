"""Helpers to create stylized tables."""

from __future__ import annotations

from typing import Iterable, Sequence

from flet import DataCell, DataColumn, DataRow, DataTable, Text

from ..theme.tokens import palette, typography


def build_table(columns: Sequence[str], rows: Iterable[Sequence[str]]) -> DataTable:
    """Return a neutral style ``DataTable``."""

    data_columns = [DataColumn(Text(c, color=palette.text_secondary)) for c in columns]
    data_rows = [
        DataRow(cells=[DataCell(Text(value, color=palette.text_primary)) for value in row])
        for row in rows
    ]
    return DataTable(columns=data_columns, rows=data_rows, heading_row_color=palette.base_bg)
