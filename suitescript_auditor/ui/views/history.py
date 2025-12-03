"""History view for Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)
    ttk.Label(frame, text="History", font=("Segoe UI", 18, "bold")).pack(anchor="w")

    columns = ("project", "status", "overall", "timestamp")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col.title())
        tree.column(col, width=180)
    tree.pack(fill="both", expand=True, pady=10)

    for job in context.job_queue.list_jobs():
        overall = "-"
        if job.results.get("docs_path"):
            overall = job.results.get("summary_score", "-")
        tree.insert(
            "",
            tk.END,
            values=(job.project_name, job.status.value.title(), overall, job.created_at.strftime("%Y-%m-%d %H:%M")),
        )

    ttk.Label(
        frame,
        text="Lista de ejecuciones previas. Ejecuta un nuevo análisis para agregar más entradas.",
        foreground="#555555",
    ).pack(anchor="w")
    return frame
