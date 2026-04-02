from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


STATUS_PENDING = "pending"
STATUS_CONVERTING = "converting"
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"


def format_file_size(size_in_bytes: int) -> str:
    units = ("B", "KB", "MB", "GB")
    size = float(size_in_bytes)
    unit = units[0]

    for unit in units:
        if size < 1024 or unit == units[-1]:
            break
        size /= 1024

    if unit == "B":
        return f"{int(size)} {unit}"
    return f"{size:.1f} {unit}"


@dataclass(slots=True)
class FileItem:
    path: Path
    status: str = STATUS_PENDING
    markdown_text: str = ""
    error_message: str = ""
    saved_path: str = ""
    was_saved: bool = False
    size_bytes: int = field(init=False)

    def __post_init__(self) -> None:
        self.path = Path(self.path).expanduser().resolve()
        self.size_bytes = self.path.stat().st_size if self.path.exists() else 0

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def size_label(self) -> str:
        return format_file_size(self.size_bytes)

    @property
    def default_save_path(self) -> Path:
        return self.path.with_suffix(".md")

    @property
    def is_converted(self) -> bool:
        return self.status == STATUS_SUCCESS and bool(self.markdown_text)

    def reset_for_conversion(self) -> None:
        self.status = STATUS_PENDING
        self.markdown_text = ""
        self.error_message = ""
        self.saved_path = ""
        self.was_saved = False

    def mark_converting(self) -> None:
        self.status = STATUS_CONVERTING
        self.error_message = ""
        self.saved_path = ""
        self.was_saved = False

    def mark_success(self, markdown_text: str) -> None:
        self.status = STATUS_SUCCESS
        self.markdown_text = markdown_text
        self.error_message = ""
        self.saved_path = ""
        self.was_saved = False

    def mark_error(self, message: str) -> None:
        self.status = STATUS_ERROR
        self.markdown_text = ""
        self.error_message = message
        self.saved_path = ""
        self.was_saved = False

    def mark_saved(self, saved_path: Path) -> None:
        self.saved_path = str(saved_path)
        self.was_saved = True
