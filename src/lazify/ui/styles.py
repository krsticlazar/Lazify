from __future__ import annotations

import tkinter as tk
from tkinter import ttk


APP_BACKGROUND = "#eff2f6"
CONTENT_BACKGROUND = "#ffffff"
CONTENT_ALT_BACKGROUND = "#f7f9fc"
STATUS_BACKGROUND = "#dde3ea"
BORDER_COLOR = "#d4dbe5"
ACCENT_COLOR = "#2d6ae3"
ACCENT_ACTIVE = "#1f58c7"
ACCENT_SOFT = "#dce7fb"
TEXT_PRIMARY = "#131826"
TEXT_SECONDARY = "#586273"
TEXT_MUTED = "#8a94a3"
SUCCESS_COLOR = "#1f7a47"
SUCCESS_SOFT = "#dff4e6"
ERROR_COLOR = "#c23a3a"
ERROR_SOFT = "#ffe4e4"
PENDING_COLOR = "#607085"
PENDING_SOFT = "#e9eef4"
TITLE_FONT = ("Segoe UI Semibold", 24)


def configure_ttk_styles(root: tk.Misc) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=(14, 10),
        relief="flat",
        borderwidth=0,
    )
    style.map("TButton", relief=[("pressed", "flat"), ("active", "flat")])

    style.configure(
        "Primary.TButton",
        background=ACCENT_COLOR,
        foreground="#ffffff",
    )
    style.map(
        "Primary.TButton",
        background=[("disabled", "#aabada"), ("active", ACCENT_ACTIVE)],
        foreground=[("disabled", "#eef2fb")],
    )

    style.configure(
        "Secondary.TButton",
        background=CONTENT_ALT_BACKGROUND,
        foreground=TEXT_PRIMARY,
    )
    style.map(
        "Secondary.TButton",
        background=[("disabled", "#eef2f6"), ("active", "#e8edf5")],
        foreground=[("disabled", "#98a2b1")],
    )

    style.configure(
        "Progress.Horizontal.TProgressbar",
        troughcolor="#dfe5ec",
        borderwidth=0,
        background=ACCENT_COLOR,
        lightcolor=ACCENT_COLOR,
        darkcolor=ACCENT_COLOR,
        thickness=9,
    )

    style.configure(
        "List.Vertical.TScrollbar",
        background="#d2dae4",
        troughcolor=CONTENT_ALT_BACKGROUND,
        bordercolor=CONTENT_ALT_BACKGROUND,
        arrowcolor=TEXT_SECONDARY,
        relief="flat",
    )
