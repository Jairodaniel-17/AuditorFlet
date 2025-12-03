"""Results dashboard view implemented with Tkinter."""

from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)
    ttk.Label(frame, text="Results", font=("Segoe UI", 18, "bold")).pack(anchor="w")

    job = _latest_completed_job(context)
    if not job:
        ttk.Label(frame, text="Ejecuta un análisis para ver resultados.").pack(anchor="w", pady=20)
        return frame

    docs_path = Path(job.results.get("docs_path", ""))
    index_path = docs_path / "index.json"
    summary = {}
    if index_path.exists():
        summary = json.loads(index_path.read_text(encoding="utf-8"))

    counts = summary.get("counts", {})
    overall = summary.get("summary_scores", {}).get("overall", 0)
    ttk.Label(frame, text=f"Overall Score: {overall:.1f}").pack(anchor="w")
    ttk.Label(frame, text=f"Files analyzed: {counts.get('files', 0)}").pack(anchor="w")
    ttk.Label(frame, text=f"High severity hotspots: {counts.get('hotspots_high', 0)}").pack(anchor="w")

    ttk.Label(frame, text="Ranking de archivos", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15, 5))
    columns = ("path", "score", "hotspots")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col.title())
        tree.column(col, width=220 if col == "path" else 120)
    tree.pack(fill="both", expand=True)

    for record in summary.get("ranking_files", [])[:10]:
        tree.insert("", tk.END, values=(record["path"], f"{record['score_overall']:.1f}", record["hotspots_high"]))

    ttk.Label(frame, text="Top 10 Hotspots", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15, 5))
    hotspot_list = tk.Text(frame, height=8)
    hotspot_list.pack(fill="both", expand=True)
    if summary.get("top_hotspots"):
        for hotspot in summary["top_hotspots"]:
            hotspot_list.insert(
                "end",
                f"- {hotspot.get('severity')} :: {hotspot.get('file')} :: {hotspot.get('title')} ({hotspot.get('line_range')})\n",
            )
    else:
        hotspot_list.insert("end", "No hay hotspots registrados.")
    hotspot_list.configure(state="disabled")
    return frame


def _latest_completed_job(context):
    jobs = [job for job in context.job_queue.list_jobs() if job.status.name == "COMPLETED"]
    return jobs[-1] if jobs else None
