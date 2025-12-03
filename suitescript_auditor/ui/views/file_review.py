"""File Review view built with Tkinter."""

from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)
    ttk.Label(frame, text="File Review", font=("Segoe UI", 18, "bold")).pack(anchor="w")

    job = _latest_completed_job(context)
    if not job:
        ttk.Label(frame, text="Ejecuta un análisis para navegar los archivos.").pack(anchor="w", pady=20)
        return frame

    docs_path = Path(job.results.get("docs_path", ""))
    audit_dir = docs_path / "audit"
    if not audit_dir.exists():
        ttk.Label(frame, text="No se encontró la carpeta Docs/audit.").pack(anchor="w", pady=20)
        return frame

    listbox = tk.Listbox(frame, height=15)
    listbox.pack(side="left", fill="y")
    for audit_file in sorted(audit_dir.rglob("*.audit.json")):
        listbox.insert("end", str(audit_file.relative_to(audit_dir)))

    detail = tk.Text(frame)
    detail.pack(side="left", fill="both", expand=True, padx=10)

    def show_details(event=None):
        selection = listbox.curselection()
        if not selection:
            return
        relative_path = listbox.get(selection[0])
        file_path = audit_dir / relative_path
        data = json.loads(file_path.read_text(encoding="utf-8"))
        detail.configure(state="normal")
        detail.delete("1.0", "end")
        detail.insert("end", f"Archivo: {data['path']}\nScriptType: {data.get('scriptType')}\n")
        detail.insert("end", f"Score global: {data['score_1_10']['overall']:.1f}\n\nHotspots:\n")
        for hotspot in data.get("hotspots", []):
            detail.insert(
                "end",
                f"- {hotspot['severity']} :: {hotspot['title']} (Líneas {hotspot['location']['startLine']}-{hotspot['location']['endLine']})\n",
            )
        if not data.get("hotspots"):
            detail.insert("end", "Sin hotspots registrados.\n")
        detail.configure(state="disabled")

    listbox.bind("<<ListboxSelect>>", show_details)
    ttk.Label(frame, text="Selecciona un archivo para ver el resumen del audit.").pack(anchor="w", pady=10)
    return frame


def _latest_completed_job(context):
    jobs = [job for job in context.job_queue.list_jobs() if job.status.name == "COMPLETED"]
    return jobs[-1] if jobs else None
