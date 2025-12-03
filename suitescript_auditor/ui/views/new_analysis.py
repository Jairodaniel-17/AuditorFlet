"""New Analysis setup view for Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from ...core.jobs.models import JobSettings, JobSourceType


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)
    ttk.Label(frame, text="New Analysis", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")

    project_var = tk.StringVar()
    path_var = tk.StringVar(value=str(Path.cwd()))
    source_var = tk.StringVar(value=JobSourceType.REPOSITORY.value)

    ttk.Label(frame, text="Project Name").grid(row=1, column=0, sticky="w", pady=(12, 0))
    ttk.Entry(frame, textvariable=project_var, width=50).grid(row=2, column=0, sticky="w")

    ttk.Label(frame, text="Source Path (ZIP or folder)").grid(row=3, column=0, sticky="w", pady=(12, 0))
    path_row = ttk.Frame(frame)
    path_row.grid(row=4, column=0, sticky="we")
    ttk.Entry(path_row, textvariable=path_var, width=50).pack(side="left", fill="x", expand=True)
    ttk.Button(path_row, text="Browse", command=lambda: _choose_path(source_var, path_var)).pack(side="left", padx=5)

    ttk.Label(frame, text="Source Type").grid(row=5, column=0, sticky="w", pady=(12, 0))
    type_row = ttk.Frame(frame)
    type_row.grid(row=6, column=0, sticky="w")
    ttk.Radiobutton(
        type_row, text="Local Repository", value=JobSourceType.REPOSITORY.value, variable=source_var
    ).pack(side="left")
    ttk.Radiobutton(type_row, text="ZIP", value=JobSourceType.ZIP.value, variable=source_var).pack(side="left", padx=10)

    options_frame = ttk.LabelFrame(frame, text="Output Options", padding=10)
    options_frame.grid(row=7, column=0, sticky="we", pady=15)
    audit_var = tk.BooleanVar(value=True)
    summary_var = tk.BooleanVar(value=True)
    md_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(options_frame, text="Generate /Docs/audit", variable=audit_var).pack(anchor="w")
    ttk.Checkbutton(options_frame, text="Generate /Docs/summary", variable=summary_var).pack(anchor="w")
    ttk.Checkbutton(options_frame, text="Include Markdown", variable=md_var).pack(anchor="w")

    llm_frame = ttk.LabelFrame(frame, text="LLM", padding=10)
    llm_frame.grid(row=8, column=0, sticky="we")
    llm_mode = tk.BooleanVar(value=False)
    quality_var = tk.StringVar(value="Economic")
    ttk.Checkbutton(llm_frame, text="Enable OCI LLM Mode", variable=llm_mode).pack(anchor="w")
    ttk.Label(llm_frame, text="Quality Tier").pack(anchor="w")
    ttk.Combobox(llm_frame, values=["Economic", "Normal", "Strict"], textvariable=quality_var, state="readonly").pack(
        anchor="w", fill="x"
    )

    def start_job():
        if not project_var.get().strip():
            messagebox.showwarning("New Analysis", "Project name is required.")
            return
        path = Path(path_var.get()).expanduser()
        if not path.exists():
            messagebox.showwarning("New Analysis", "Source path does not exist.")
            return
        settings = JobSettings(
            generate_audit=audit_var.get(),
            generate_summary=summary_var.get(),
            include_markdown=md_var.get(),
            llm_mode=llm_mode.get(),
            quality_tier=quality_var.get(),
        )
        context.job_queue.submit_job(
            project_name=project_var.get().strip(),
            source=path,
            source_type=JobSourceType(source_var.get()),
            settings=settings,
        )
        messagebox.showinfo("New Analysis", "Job queued successfully. Revise el Processing Center.")

    ttk.Button(frame, text="Start Analysis", command=start_job).grid(row=9, column=0, sticky="e", pady=20)
    frame.columnconfigure(0, weight=1)
    return frame


def _choose_path(source_var: tk.StringVar, path_var: tk.StringVar) -> None:
    if source_var.get() == JobSourceType.ZIP.value:
        filename = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if filename:
            path_var.set(filename)
    else:
        directory = filedialog.askdirectory()
        if directory:
            path_var.set(directory)
