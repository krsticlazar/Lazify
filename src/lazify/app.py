from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from lazify.converter import ConverterError, FileConverter, SUPPORTED_EXTENSIONS
from lazify.file_item import FileItem
from lazify.resources import icon_path
from lazify.ui.drop_zone import DropZone
from lazify.ui.file_row import FileRow
from lazify.ui.styles import (
    APP_BACKGROUND,
    BORDER_COLOR,
    CONTENT_BACKGROUND,
    STATUS_BACKGROUND,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TITLE_FONT,
    configure_ttk_styles,
)

try:
    from tkinterdnd2 import TkinterDnD
except ImportError:
    TkinterDnD = None


WINDOW_HEIGHT = 520
WINDOW_WIDTH = 720
TITLE = "Lazify"
SUBTITLE = "File -> Markdown Converter"
QUEUE_POLL_MS = 100
BaseWindow = TkinterDnD.Tk if TkinterDnD else tk.Tk


class LazifyApp(BaseWindow):
    def __init__(self) -> None:
        super().__init__()
        self.converter = FileConverter()
        self.items: dict[str, FileItem] = {}
        self.rows: dict[str, FileRow] = {}
        self.event_queue: queue.Queue[tuple[str, str | None, object | None]] = queue.Queue()
        self.is_converting = False
        self.run_total = 0
        self.run_completed = 0
        self.run_successes = 0
        self.mousewheel_bound = False
        self.status_var = tk.StringVar(value="Ready")

        self.title(TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=APP_BACKGROUND)

        self._set_icon()
        configure_ttk_styles(self)
        self._build_layout()
        self.after(QUEUE_POLL_MS, self._drain_events)

    def _set_icon(self) -> None:
        icon_file = icon_path()
        if icon_file.exists():
            try:
                self.iconbitmap(default=str(icon_file))
            except tk.TclError:
                pass

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg=APP_BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 16))

        tk.Label(
            header,
            text=TITLE,
            font=TITLE_FONT,
            fg=TEXT_PRIMARY,
            bg=APP_BACKGROUND,
        ).pack(anchor="w")
        tk.Label(
            header,
            text=SUBTITLE,
            font=("Segoe UI", 11),
            fg=TEXT_SECONDARY,
            bg=APP_BACKGROUND,
        ).pack(anchor="w", pady=(2, 0))

        content = tk.Frame(
            self,
            bg=CONTENT_BACKGROUND,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self.drop_zone = DropZone(content, on_browse=self._browse_files, on_files=self._add_files)
        self.drop_zone.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))

        list_shell = tk.Frame(content, bg=CONTENT_BACKGROUND)
        list_shell.grid(row=1, column=0, sticky="nsew", padx=20)
        list_shell.columnconfigure(0, weight=1)
        list_shell.rowconfigure(0, weight=1)

        self.list_canvas = tk.Canvas(
            list_shell,
            bg=CONTENT_BACKGROUND,
            bd=0,
            highlightthickness=0,
            relief="flat",
        )
        self.list_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            list_shell,
            orient="vertical",
            command=self.list_canvas.yview,
            style="List.Vertical.TScrollbar",
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.list_canvas.configure(yscrollcommand=scrollbar.set)

        self.rows_container = tk.Frame(self.list_canvas, bg=CONTENT_BACKGROUND)
        self.canvas_window = self.list_canvas.create_window((0, 0), window=self.rows_container, anchor="nw")

        self.rows_container.bind("<Configure>", self._refresh_scroll_region)
        self.list_canvas.bind("<Configure>", self._resize_canvas_window)
        self.list_canvas.bind("<Enter>", self._bind_mousewheel)
        self.list_canvas.bind("<Leave>", self._unbind_mousewheel)

        self.empty_state = tk.Label(
            self.rows_container,
            text="No files added yet. Drag files here or use Add Files.",
            font=("Segoe UI", 10),
            fg=TEXT_MUTED,
            bg=CONTENT_BACKGROUND,
            pady=40,
        )
        self.empty_state.pack(fill="x")

        footer = tk.Frame(content, bg=CONTENT_BACKGROUND)
        footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(12, 18))
        footer.columnconfigure(0, weight=1)

        self.clear_button = ttk.Button(
            footer,
            text="Clear All",
            command=self._clear_all,
            style="Secondary.TButton",
        )
        self.clear_button.grid(row=0, column=1, sticky="e")

        actions = tk.Frame(self, bg=APP_BACKGROUND)
        actions.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        actions.columnconfigure(1, weight=1)

        self.add_button = ttk.Button(
            actions,
            text="Add Files",
            command=self._browse_files,
            style="Secondary.TButton",
        )
        self.add_button.grid(row=0, column=0, sticky="w")

        progress_frame = tk.Frame(actions, bg=APP_BACKGROUND)
        progress_frame.grid(row=0, column=1, sticky="ew", padx=16)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            style="Progress.Horizontal.TProgressbar",
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=APP_BACKGROUND,
        )
        self.progress_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.save_all_button = ttk.Button(
            actions,
            text="Save All",
            command=self._save_all,
            style="Secondary.TButton",
        )
        self.save_all_button.grid(row=0, column=2, sticky="e", padx=(0, 8))

        self.convert_button = ttk.Button(
            actions,
            text="Convert All",
            command=self._convert_all,
            style="Primary.TButton",
        )
        self.convert_button.grid(row=0, column=3, sticky="e")

        tk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            font=("Segoe UI", 10),
            fg=TEXT_SECONDARY,
            bg=STATUS_BACKGROUND,
            padx=16,
            pady=10,
        ).grid(row=3, column=0, sticky="ew")

        self._refresh_actions()

    def _browse_files(self) -> None:
        if self.is_converting:
            return

        patterns = " ".join(f"*{extension}" for extension in sorted(SUPPORTED_EXTENSIONS))
        selected_paths = filedialog.askopenfilenames(
            title="Select files to convert",
            filetypes=[
                ("Supported files", patterns),
                ("All files", "*.*"),
            ],
        )
        if selected_paths:
            self._add_files(selected_paths)

    def _add_files(self, raw_paths: list[str] | tuple[str, ...]) -> None:
        if self.is_converting:
            self._set_status("Wait for the current conversion to finish before adding more files.")
            return

        added_count = 0
        duplicate_count = 0
        unsupported_count = 0
        missing_count = 0

        for raw_path in raw_paths:
            try:
                path = Path(raw_path).expanduser().resolve()
            except OSError:
                missing_count += 1
                continue

            key = str(path)

            if key in self.items:
                duplicate_count += 1
                continue
            if not path.exists() or not path.is_file():
                missing_count += 1
                continue
            if not self.converter.is_supported(path):
                unsupported_count += 1
                continue

            item = FileItem(path=path)
            self.items[key] = item
            row = FileRow(
                self.rows_container,
                item=item,
                on_remove=self._remove_file,
                on_save=self._save_file,
            )
            row.pack(fill="x", pady=(0, 10))
            self.rows[key] = row
            added_count += 1

        self._refresh_empty_state()
        self._refresh_actions()

        messages: list[str] = []
        if added_count:
            messages.append(f"Added {added_count} file{'s' if added_count != 1 else ''}.")
        if duplicate_count:
            messages.append(f"Skipped {duplicate_count} duplicate{'s' if duplicate_count != 1 else ''}.")
        if unsupported_count:
            messages.append(f"Skipped {unsupported_count} unsupported file{'s' if unsupported_count != 1 else ''}.")
        if missing_count:
            messages.append(f"Skipped {missing_count} missing item{'s' if missing_count != 1 else ''}.")

        self._set_status(" ".join(messages) if messages else "No new files were added.")

    def _remove_file(self, source_path: Path) -> None:
        if self.is_converting:
            self._set_status("Wait for the current conversion to finish before removing files.")
            return

        key = str(source_path.resolve())
        item = self.items.pop(key, None)
        row = self.rows.pop(key, None)

        if row is not None:
            row.destroy()

        self._refresh_empty_state()
        self._refresh_actions()

        if item is not None:
            self._set_status(f"Removed {item.name}.")

    def _clear_all(self) -> None:
        if self.is_converting:
            self._set_status("Wait for the current conversion to finish before clearing the list.")
            return
        if not self.items:
            return

        if any(item.is_converted for item in self.items.values()):
            should_clear = messagebox.askyesno(
                title="Clear all files",
                message="Some files have already been converted. Clear the list anyway?",
                parent=self,
            )
            if not should_clear:
                return

        for row in self.rows.values():
            row.destroy()

        self.items.clear()
        self.rows.clear()
        self._reset_progress()
        self._refresh_empty_state()
        self._refresh_actions()
        self._set_status("Cleared all files.")

    def _convert_all(self) -> None:
        if self.is_converting:
            return
        if not self.items:
            self._set_status("Add at least one supported file before converting.")
            return

        self.is_converting = True
        self.run_total = len(self.items)
        self.run_completed = 0
        self.run_successes = 0
        self.progress_bar.configure(maximum=self.run_total, value=0)
        self.progress_label.configure(text=f"0 / {self.run_total} complete")

        for item in self.items.values():
            item.reset_for_conversion()
            self.rows[str(item.path)].update_item(item)

        self._refresh_actions()
        self._set_status(f"Converting {self.run_total} file{'s' if self.run_total != 1 else ''}...")

        source_paths = [Path(key) for key in self.items]
        threading.Thread(target=self._convert_worker, args=(source_paths,), daemon=True).start()

    def _convert_worker(self, source_paths: list[Path]) -> None:
        success_count = 0

        for path in source_paths:
            key = str(path)
            self.event_queue.put(("start", key, None))
            try:
                markdown_text = self.converter.convert_file(path)
            except ConverterError as exc:
                self.event_queue.put(("error", key, str(exc)))
                continue
            except Exception as exc:
                self.event_queue.put(("error", key, str(exc)))
                continue

            success_count += 1
            self.event_queue.put(("success", key, markdown_text))

        self.event_queue.put(("complete", None, success_count))

    def _drain_events(self) -> None:
        while True:
            try:
                event_type, key, payload = self.event_queue.get_nowait()
            except queue.Empty:
                break

            if event_type == "start" and key:
                item = self.items.get(key)
                if item is None:
                    continue
                item.mark_converting()
                self.rows[key].update_item(item)
                self._set_status(f"Converting {item.name}...")

            elif event_type == "success" and key:
                item = self.items.get(key)
                if item is None:
                    continue
                item.mark_success(str(payload or ""))
                self.rows[key].update_item(item)
                self._mark_progress(success=True)

            elif event_type == "error" and key:
                item = self.items.get(key)
                if item is None:
                    continue
                item.mark_error(str(payload or "Unknown conversion error"))
                self.rows[key].update_item(item)
                self._mark_progress(success=False)

            elif event_type == "complete":
                success_count = int(payload or 0)
                self.is_converting = False
                self._refresh_actions()

                if success_count == self.run_total:
                    self._set_status(f"{success_count} file{'s' if success_count != 1 else ''} converted successfully.")
                elif success_count == 0:
                    self._set_status("No files were converted successfully.")
                else:
                    self._set_status(f"Converted {success_count} of {self.run_total} files successfully.")

        self.after(QUEUE_POLL_MS, self._drain_events)

    def _mark_progress(self, success: bool) -> None:
        self.run_completed += 1
        if success:
            self.run_successes += 1

        self.progress_bar.configure(value=self.run_completed)
        self.progress_label.configure(text=f"{self.run_completed} / {self.run_total} complete")

    def _save_file(self, source_path: Path) -> None:
        key = str(source_path.resolve())
        item = self.items.get(key)
        if item is None or not item.is_converted:
            return

        suggested_path = Path(item.saved_path).resolve() if item.was_saved and item.saved_path else self.converter.suggest_output_path(item.path)

        target_path = filedialog.asksaveasfilename(
            title=f"Save Markdown for {item.name}",
            initialdir=str(suggested_path.parent),
            initialfile=suggested_path.name,
            defaultextension=".md",
            filetypes=[
                ("Markdown files", "*.md"),
                ("All files", "*.*"),
            ],
        )
        if not target_path:
            return

        try:
            saved_path = self.converter.save_markdown(item.path, item.markdown_text, target_path)
        except ConverterError as exc:
            messagebox.showerror(title="Save failed", message=str(exc), parent=self)
            self._set_status(f"Could not save {item.name}.")
            return

        item.mark_saved(saved_path)
        self.rows[key].update_item(item)
        self._refresh_actions()
        self._set_status(f"Saved {saved_path.name}.")

    def _save_all(self) -> None:
        converted_items = [item for item in self.items.values() if item.is_converted]
        if not converted_items:
            return

        saved_count = 0
        failed_count = 0
        reserved_paths: set[Path] = set()

        for item in converted_items:
            if item.was_saved and item.saved_path:
                target_path = Path(item.saved_path).resolve()
            else:
                target_path = self.converter.suggest_output_path(item.path, reserved_paths=reserved_paths)

            try:
                saved_path = self.converter.save_markdown(item.path, item.markdown_text, target_path)
            except ConverterError:
                failed_count += 1
                continue

            item.mark_saved(saved_path)
            reserved_paths.add(saved_path.resolve())
            self.rows[str(item.path)].update_item(item)
            saved_count += 1

        self._refresh_actions()
        if failed_count:
            self._set_status(f"Saved {saved_count} file{'s' if saved_count != 1 else ''}, {failed_count} failed.")
        else:
            self._set_status(f"Saved {saved_count} file{'s' if saved_count != 1 else ''}.")

    def _refresh_actions(self) -> None:
        has_items = bool(self.items)
        has_converted = any(item.is_converted for item in self.items.values())

        self.add_button.configure(state="disabled" if self.is_converting else "normal")
        self.convert_button.configure(state="disabled" if self.is_converting or not has_items else "normal")
        self.clear_button.configure(state="disabled" if self.is_converting or not has_items else "normal")
        self.save_all_button.configure(state="disabled" if self.is_converting or not has_converted else "normal")

        if has_converted:
            self.save_all_button.grid()
        else:
            self.save_all_button.grid_remove()

        self.drop_zone.set_busy(self.is_converting)
        for row in self.rows.values():
            row.set_busy(self.is_converting)

    def _refresh_empty_state(self) -> None:
        if self.items:
            if self.empty_state.winfo_manager():
                self.empty_state.pack_forget()
        elif not self.empty_state.winfo_manager():
            self.empty_state.pack(fill="x")

    def _reset_progress(self) -> None:
        self.run_total = 0
        self.run_completed = 0
        self.run_successes = 0
        self.progress_bar.configure(value=0, maximum=1)
        self.progress_label.configure(text="")

    def _refresh_scroll_region(self, _event: tk.Event | None = None) -> None:
        self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

    def _resize_canvas_window(self, event: tk.Event) -> None:
        self.list_canvas.itemconfigure(self.canvas_window, width=event.width)

    def _bind_mousewheel(self, _event: tk.Event | None = None) -> None:
        if not self.mousewheel_bound:
            self.bind_all("<MouseWheel>", self._on_mousewheel)
            self.mousewheel_bound = True

    def _unbind_mousewheel(self, _event: tk.Event | None = None) -> None:
        if self.mousewheel_bound:
            self.unbind_all("<MouseWheel>")
            self.mousewheel_bound = False

    def _on_mousewheel(self, event: tk.Event) -> None:
        if self.list_canvas.winfo_height() >= self.rows_container.winfo_height():
            return
        self.list_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)
