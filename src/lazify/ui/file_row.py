from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lazify.file_item import (
    STATUS_CONVERTING,
    STATUS_ERROR,
    STATUS_PENDING,
    STATUS_SUCCESS,
    FileItem,
)
from lazify.ui.styles import (
    ACCENT_COLOR,
    ACCENT_SOFT,
    BORDER_COLOR,
    CONTENT_ALT_BACKGROUND,
    CONTENT_BACKGROUND,
    ERROR_COLOR,
    ERROR_SOFT,
    PENDING_COLOR,
    PENDING_SOFT,
    SUCCESS_COLOR,
    SUCCESS_SOFT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


ICON_BY_EXTENSION = {
    ".pdf": "PDF",
    ".docx": "DOC",
    ".xlsx": "XLS",
    ".pptx": "PPT",
    ".html": "HTML",
    ".htm": "HTML",
    ".csv": "CSV",
    ".json": "JSON",
    ".xml": "XML",
    ".jpg": "IMG",
    ".jpeg": "IMG",
    ".png": "IMG",
}

STATUS_TEXT = {
    STATUS_PENDING: "Queued",
    STATUS_CONVERTING: "Converting",
    STATUS_SUCCESS: "Converted",
    STATUS_ERROR: "Failed",
}

STATUS_COLORS = {
    STATUS_PENDING: (PENDING_SOFT, PENDING_COLOR),
    STATUS_CONVERTING: (ACCENT_SOFT, ACCENT_COLOR),
    STATUS_SUCCESS: (SUCCESS_SOFT, SUCCESS_COLOR),
    STATUS_ERROR: (ERROR_SOFT, ERROR_COLOR),
}


class FileRow(tk.Frame):
    def __init__(self, master: tk.Misc, item: FileItem, on_remove) -> None:
        super().__init__(
            master,
            bg=CONTENT_BACKGROUND,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            padx=12,
            pady=10,
        )
        self.item = item
        self.on_remove = on_remove
        self.is_busy = False
        self.tooltip_text = ""
        self.tooltip_window: tk.Toplevel | None = None

        self.columnconfigure(1, weight=1)

        self.icon_label = tk.Label(
            self,
            width=6,
            font=("Segoe UI Semibold", 9),
            fg=TEXT_SECONDARY,
            bg=CONTENT_ALT_BACKGROUND,
            padx=8,
            pady=6,
        )
        self.icon_label.grid(row=0, column=0, rowspan=2, sticky="nw")

        self.name_label = tk.Label(
            self,
            anchor="w",
            font=("Segoe UI Semibold", 10),
            fg=TEXT_PRIMARY,
            bg=CONTENT_BACKGROUND,
        )
        self.name_label.grid(row=0, column=1, sticky="ew", padx=(12, 12))

        self.meta_label = tk.Label(
            self,
            anchor="w",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=CONTENT_BACKGROUND,
        )
        self.meta_label.grid(row=1, column=1, sticky="ew", padx=(12, 12), pady=(4, 0))

        self.status_badge = tk.Label(
            self,
            font=("Segoe UI Semibold", 9),
            padx=10,
            pady=5,
            cursor="question_arrow",
        )
        self.status_badge.grid(row=0, column=2, rowspan=2, sticky="e", padx=(0, 8))
        self.status_badge.bind("<Enter>", self._show_tooltip)
        self.status_badge.bind("<Leave>", self._hide_tooltip)
        self.status_badge.bind("<ButtonPress-1>", self._hide_tooltip)

        self.saved_label = tk.Label(
            self,
            text="Saved",
            font=("Segoe UI", 9),
            fg=SUCCESS_COLOR,
            bg=CONTENT_BACKGROUND,
        )
        self.saved_label.grid(row=0, column=3, rowspan=2, sticky="e", padx=(0, 8))

        self.remove_button = ttk.Button(
            self,
            text="Remove",
            command=self._handle_remove,
            style="Secondary.TButton",
        )
        self.remove_button.grid(row=0, column=4, rowspan=2, sticky="e")

        self.update_item(item)

    def update_item(self, item: FileItem) -> None:
        self.item = item
        self.icon_label.configure(text=ICON_BY_EXTENSION.get(item.extension, "FILE"))
        self.name_label.configure(text=item.name)

        extension_text = item.extension[1:].upper() if item.extension else "FILE"
        self.meta_label.configure(text=f"{extension_text}  |  {item.size_label}")

        badge_background, badge_foreground = STATUS_COLORS[item.status]
        self.status_badge.configure(
            text=STATUS_TEXT[item.status],
            bg=badge_background,
            fg=badge_foreground,
        )

        if item.was_saved:
            self.saved_label.grid()
        else:
            self.saved_label.grid_remove()

        self.tooltip_text = item.error_message if item.status == STATUS_ERROR else ""
        self.set_busy(self.is_busy)

    def set_busy(self, is_busy: bool) -> None:
        self.is_busy = is_busy
        self.remove_button.configure(state="disabled" if is_busy else "normal")

    def _handle_remove(self) -> None:
        self.on_remove(self.item.path)

    def _show_tooltip(self, _event: tk.Event) -> None:
        if not self.tooltip_text or self.tooltip_window is not None:
            return

        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.attributes("-topmost", True)

        tk.Label(
            self.tooltip_window,
            text=self.tooltip_text,
            justify="left",
            wraplength=280,
            bg="#111827",
            fg="#f8fafc",
            font=("Segoe UI", 9),
            padx=10,
            pady=6,
        ).pack()

        x_pos = self.status_badge.winfo_rootx()
        y_pos = self.status_badge.winfo_rooty() - self.status_badge.winfo_height() - 12
        self.tooltip_window.geometry(f"+{x_pos}+{max(y_pos, 0)}")

    def _hide_tooltip(self, _event: tk.Event | None = None) -> None:
        if self.tooltip_window is not None:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def destroy(self) -> None:
        self._hide_tooltip()
        super().destroy()
