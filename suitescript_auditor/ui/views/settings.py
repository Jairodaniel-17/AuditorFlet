"""Settings view implemented with Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from ...core.config.defaults import defaults


def build(parent: tk.Widget, context) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=20)
    ttk.Label(frame, text="Settings", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")

    oci = ttk.LabelFrame(frame, text="OCI", padding=10)
    oci.grid(row=1, column=0, sticky="we", pady=10)
    region_var = tk.StringVar(value=defaults.region)
    model_var = tk.StringVar(value=defaults.llm_model)
    ttk.Label(oci, text="Region/Endpoint").grid(row=0, column=0, sticky="w")
    ttk.Entry(oci, textvariable=region_var, width=30).grid(row=1, column=0, sticky="w")
    ttk.Label(oci, text="Model name").grid(row=2, column=0, sticky="w", pady=(8, 0))
    ttk.Entry(oci, textvariable=model_var, width=30).grid(row=3, column=0, sticky="w")

    ttk.Button(oci, text="Test connection", command=lambda: messagebox.showinfo("Settings", "Conexión simulada OK")).grid(
        row=4, column=0, pady=10, sticky="w"
    )

    git = ttk.LabelFrame(frame, text="Git", padding=10)
    git.grid(row=2, column=0, sticky="we", pady=10)
    ttk.Label(git, text="Proveedor por defecto:").grid(row=0, column=0, sticky="w")
    ttk.Combobox(git, values=["GitHub", "GitLab", "Bitbucket"], state="readonly").grid(row=1, column=0, sticky="w")
    ttk.Button(git, text="Probar push", command=lambda: messagebox.showinfo("Settings", "Push simulado")).grid(
        row=2, column=0, pady=5, sticky="w"
    )

    limits = ttk.LabelFrame(frame, text="LLM Limits", padding=10)
    limits.grid(row=3, column=0, sticky="we", pady=10)
    ttk.Label(limits, text="Max cost per job (USD)").grid(row=0, column=0, sticky="w")
    ttk.Entry(limits, width=10, textvariable=tk.StringVar(value=str(defaults.max_cost_per_job))).grid(
        row=1, column=0, sticky="w"
    )
    ttk.Label(limits, text="Max tokens per file").grid(row=2, column=0, sticky="w", pady=(8, 0))
    ttk.Entry(limits, width=10, textvariable=tk.StringVar(value="2000")).grid(row=3, column=0, sticky="w")

    ui_section = ttk.LabelFrame(frame, text="UI", padding=10)
    ui_section.grid(row=4, column=0, sticky="we", pady=10)
    ttk.Label(ui_section, text="Theme").grid(row=0, column=0, sticky="w")
    ttk.Combobox(ui_section, values=["Light"], state="readonly").grid(row=1, column=0, sticky="w")
    ttk.Label(ui_section, text="Font Size").grid(row=2, column=0, sticky="w", pady=(8, 0))
    ttk.Scale(ui_section, from_=12, to=18, orient="horizontal").grid(row=3, column=0, sticky="we")

    frame.columnconfigure(0, weight=1)
    return frame
