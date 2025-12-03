"""Processing Center view implemented with Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ...core.jobs.models import JobStatus


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)

    header = ttk.Label(frame, text="Processing Center", font=("Segoe UI", 18, "bold"))
    header.pack(anchor="w")

    stats_frame = ttk.Frame(frame)
    stats_frame.pack(fill="x", pady=10)

    total_jobs = len(context.job_queue.list_jobs())
    running = len([j for j in context.job_queue.list_jobs() if j.status == JobStatus.RUNNING])
    completed = len([j for j in context.job_queue.list_jobs() if j.status == JobStatus.COMPLETED])
    failed = len([j for j in context.job_queue.list_jobs() if j.status == JobStatus.FAILED])

    for label, value in [
        ("Total Jobs", total_jobs),
        ("Running", running),
        ("Completed", completed),
        ("Failed", failed),
    ]:
        _metric(stats_frame, label, value)

    table_frame = ttk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    columns = ("project", "status", "progress", "stage", "files", "cost")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col.title())
        tree.column(col, width=150 if col != "project" else 220)
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def refresh():
        for row in tree.get_children():
            tree.delete(row)
        for job in context.job_queue.list_jobs():
            tree.insert(
                "",
                tk.END,
                values=(
                    job.project_name,
                    job.status.value.title(),
                    f"{job.progress*100:.0f}%",
                    job.stage.value if hasattr(job.stage, "value") else str(job.stage),
                    f"{job.files_processed}/{job.files_total}",
                    f"${job.llm_cost:.2f}",
                ),
            )

    refresh()

    ttk.Button(frame, text="Actualizar", command=refresh).pack(anchor="e", pady=10)
    ttk.Label(
        frame,
        text="Selecciona 'Nueva Análisis' para crear un job o refresca para ver progreso.",
        foreground="#555555",
    ).pack(anchor="w")
    return frame


def _metric(parent: ttk.Frame, label: str, value: int) -> None:
    container = ttk.Frame(parent, padding=10)
    container.pack(side="left", padx=10)
    ttk.Label(container, text=label, font=("Segoe UI", 10, "bold")).pack()
    ttk.Label(container, text=value, font=("Segoe UI", 16)).pack()
