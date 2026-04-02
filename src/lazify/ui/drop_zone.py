from __future__ import annotations

import tkinter as tk

from lazify.ui.styles import (
    ACCENT_COLOR,
    APP_BACKGROUND,
    BORDER_COLOR,
    CONTENT_ALT_BACKGROUND,
    CONTENT_BACKGROUND,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None


class DropZone(tk.Frame):
    def __init__(self, master: tk.Misc, on_browse, on_files) -> None:
        super().__init__(
            master,
            bg=CONTENT_ALT_BACKGROUND,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            cursor="hand2",
            padx=18,
            pady=18,
        )
        self.on_browse = on_browse
        self.on_files = on_files
        self.is_busy = False

        self.columnconfigure(0, weight=1)

        self.title_label = tk.Label(
            self,
            text="Drag and drop files here or click to browse",
            font=("Segoe UI Semibold", 11),
            fg=TEXT_PRIMARY,
            bg=CONTENT_ALT_BACKGROUND,
        )
        self.title_label.grid(row=0, column=0, sticky="n", pady=(2, 6))

        self.subtitle_label = tk.Label(
            self,
            text="Supports PDF, DOCX and PPTX",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=CONTENT_ALT_BACKGROUND,
            wraplength=560,
            justify="center",
        )
        self.subtitle_label.grid(row=1, column=0, sticky="ew")

        for widget in (self, self.title_label, self.subtitle_label):
            widget.bind("<Button-1>", self._handle_click)

        self.bind("<Enter>", self._handle_hover_enter)
        self.bind("<Leave>", self._handle_hover_leave)

        if DND_FILES and hasattr(self, "drop_target_register"):
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<DropEnter>>", self._handle_drag_enter)
            self.dnd_bind("<<DropLeave>>", self._handle_drag_leave)
            self.dnd_bind("<<Drop>>", self._handle_drop)
        else:
            self.subtitle_label.configure(text="Click to browse files. Drag and drop is unavailable in this environment.")

    def set_busy(self, is_busy: bool) -> None:
        self.is_busy = is_busy
        self.configure(cursor="arrow" if is_busy else "hand2")
        if is_busy:
            self._set_surface(APP_BACKGROUND, BORDER_COLOR)
        else:
            self._set_surface(CONTENT_ALT_BACKGROUND, BORDER_COLOR)

    def _handle_click(self, _event: tk.Event) -> None:
        if not self.is_busy:
            self.on_browse()

    def _handle_hover_enter(self, _event: tk.Event) -> None:
        if not self.is_busy:
            self._set_surface(CONTENT_BACKGROUND, ACCENT_COLOR)

    def _handle_hover_leave(self, _event: tk.Event) -> None:
        if not self.is_busy:
            self._set_surface(CONTENT_ALT_BACKGROUND, BORDER_COLOR)

    def _handle_drag_enter(self, _event: tk.Event) -> str:
        if not self.is_busy:
            self._set_surface(CONTENT_BACKGROUND, ACCENT_COLOR)
        return "copy"

    def _handle_drag_leave(self, _event: tk.Event) -> None:
        if not self.is_busy:
            self._set_surface(CONTENT_ALT_BACKGROUND, BORDER_COLOR)

    def _handle_drop(self, event: tk.Event) -> str:
        self._handle_drag_leave(event)
        if self.is_busy:
            return "break"

        dropped_paths = self.tk.splitlist(event.data)
        if dropped_paths:
            self.on_files(dropped_paths)
        return "break"

    def _set_surface(self, background: str, border: str) -> None:
        self.configure(bg=background, highlightbackground=border)
        self.title_label.configure(bg=background)
        self.subtitle_label.configure(bg=background)
