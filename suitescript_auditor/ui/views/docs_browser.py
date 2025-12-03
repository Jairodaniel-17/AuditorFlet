"""Docs Browser view for Tkinter."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)
    ttk.Label(frame, text="Docs Browser", font=("Segoe UI", 18, "bold")).pack(anchor="w")

    job = _latest_completed_job(context)
    if not job:
        ttk.Label(frame, text="No hay documentación generada aún.").pack(anchor="w", pady=20)
        return frame

    docs_path = Path(job.results.get("docs_path", ""))
    summary_dir = docs_path / "summary"
    if not summary_dir.exists():
        ttk.Label(frame, text="No se encontró Docs/summary.").pack(anchor="w", pady=20)
        return frame

    body = ttk.Frame(frame)
    body.pack(fill="both", expand=True)

    listbox = tk.Listbox(body, width=40)
    listbox.pack(side="left", fill="y")
    files = sorted(summary_dir.rglob("*.summary.md"))
    for file in files:
        listbox.insert("end", str(file.relative_to(summary_dir)))

    text = tk.Text(body)
    text.pack(side="left", fill="both", expand=True, padx=10)

    def display_file(event=None):
        selection = listbox.curselection()
        if not selection:
            return
        selected = files[selection[0]]
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("end", selected.read_text(encoding="utf-8"))
        text.configure(state="disabled")

    listbox.bind("<<ListboxSelect>>", display_file)
    ttk.Label(frame, text="Explora Markdown generados. Usa File Review para detalles completos.").pack(anchor="w", pady=10)
    return frame


def _latest_completed_job(context):
    jobs = [job for job in context.job_queue.list_jobs() if job.status.name == "COMPLETED"]
    return jobs[-1] if jobs else None
