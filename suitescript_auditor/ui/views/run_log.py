"""Run Log view for Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ...core.jobs.models import Job


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)
    ttk.Label(frame, text="Run Log", font=("Segoe UI", 18, "bold")).pack(anchor="w")

    jobs = context.job_queue.list_jobs()
    job = jobs[-1] if jobs else None
    if not job:
        ttk.Label(frame, text="No hay jobs en ejecución.").pack(anchor="w", pady=20)
        return frame

    ttk.Label(frame, text=f"Proyecto seleccionado: {job.project_name}").pack(anchor="w", pady=(10, 5))
    ttk.Label(frame, text=f"Estatus actual: {job.status.value.title()}").pack(anchor="w")

    progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
    progress["value"] = job.progress * 100
    progress.pack(fill="x", pady=10)

    stepper = ttk.Frame(frame)
    stepper.pack(fill="x", pady=10)
    for idx, stage in enumerate(job.stage.__class__):
        color = "#C62828" if stage == job.stage else "#BDBDBD"
        step = ttk.Frame(stepper, padding=5)
        step.pack(side="left")
        ttk.Label(step, text=f"{idx+1}. {stage.value}", foreground=color).pack()

    cards = ttk.Frame(frame)
    cards.pack(fill="x", pady=10)
    _info_card(cards, "Archivo actual", job.current_file or "-")
    _info_card(cards, "Procesados / Total", f"{job.files_processed}/{job.files_total}")
    _info_card(cards, "Hotspots", str(job.results.get("hotspots", 0) if job.results else 0))
    _info_card(cards, "Costo LLM (USD)", f"${job.llm_cost:.2f}")

    ttk.Label(frame, text="Logs", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15, 5))
    log_box = tk.Text(frame, height=12)
    log_box.pack(fill="both", expand=True)
    if job.log:
        for entry in job.log:
            log_box.insert("end", f"[{entry.timestamp:%H:%M:%S}] {entry.level.upper()} - {entry.message}\n")
    else:
        log_box.insert("end", "Sin eventos registrados todavía.")
    log_box.configure(state="disabled")
    return frame


def _info_card(parent: ttk.Frame, title: str, value: str) -> None:
    wrapper = ttk.Frame(parent, padding=10, borderwidth=1, relief="ridge")
    wrapper.pack(side="left", padx=5, fill="x", expand=True)
    ttk.Label(wrapper, text=title, font=("Segoe UI", 9, "bold")).pack()
    ttk.Label(wrapper, text=value, font=("Segoe UI", 12)).pack()
