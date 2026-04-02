from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk


WINDOW_HEIGHT = 520
WINDOW_WIDTH = 720
TITLE = "Lazify"
SUBTITLE = "File -> Markdown Converter"


class LazifyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg="#f3f4f6")

        self._set_icon()
        self._build_layout()

    def _set_icon(self) -> None:
        icon_path = Path(__file__).resolve().parent / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(default=str(icon_path))
            except tk.TclError:
                pass

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg="#f3f4f6")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 16))

        title_label = tk.Label(
            header,
            text=TITLE,
            font=("Segoe UI Semibold", 24),
            fg="#111827",
            bg="#f3f4f6",
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header,
            text=SUBTITLE,
            font=("Segoe UI", 11),
            fg="#6b7280",
            bg="#f3f4f6",
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        content = tk.Frame(self, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#d1d5db")
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        drop_zone = tk.Label(
            content,
            text="Drag and drop support and file list will be enabled next.",
            font=("Segoe UI", 11),
            fg="#4b5563",
            bg="#ffffff",
            padx=24,
            pady=28,
        )
        drop_zone.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))

        placeholder = tk.Label(
            content,
            text="The converter workspace is being prepared.",
            font=("Segoe UI", 10),
            fg="#9ca3af",
            bg="#ffffff",
        )
        placeholder.grid(row=1, column=0, sticky="n", pady=40)

        actions = tk.Frame(self, bg="#f3f4f6")
        actions.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        actions.columnconfigure(0, weight=1)

        ttk.Button(actions, text="Add Files").grid(row=0, column=0, sticky="w")
        ttk.Button(actions, text="Convert All").grid(row=0, column=1, sticky="e")

        status = tk.Label(
            self,
            text="Ready",
            anchor="w",
            font=("Segoe UI", 10),
            fg="#4b5563",
            bg="#e5e7eb",
            padx=16,
            pady=10,
        )
        status.grid(row=3, column=0, sticky="ew")
