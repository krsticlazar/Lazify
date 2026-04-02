from __future__ import annotations

from pathlib import Path

from markitdown import MarkItDown


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".xml",
    ".jpg",
    ".jpeg",
    ".png",
}


class ConverterError(Exception):
    pass


class UnsupportedFileTypeError(ConverterError):
    pass


class FileConverter:
    def __init__(self) -> None:
        self._converter = MarkItDown()

    def is_supported(self, source_path: str | Path) -> bool:
        return Path(source_path).suffix.lower() in SUPPORTED_EXTENSIONS

    def convert_file(self, source_path: str | Path) -> str:
        path = Path(source_path).expanduser().resolve()
        self._validate_source(path)

        try:
            result = self._converter.convert(path)
        except UnsupportedFileTypeError:
            raise
        except Exception as exc:
            raise ConverterError(self._format_exception(path, exc)) from exc

        markdown_text = (getattr(result, "markdown", None) or getattr(result, "text_content", "")).strip()
        return markdown_text

    def save_markdown(
        self,
        source_path: str | Path,
        markdown_text: str,
        target_path: str | Path | None = None,
    ) -> Path:
        source = Path(source_path).expanduser().resolve()
        destination = Path(target_path).expanduser().resolve() if target_path else source.with_suffix(".md")

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(markdown_text, encoding="utf-8")
        except OSError as exc:
            raise ConverterError(self._format_exception(destination, exc)) from exc

        return destination

    def _validate_source(self, path: Path) -> None:
        if not path.exists():
            raise ConverterError(f"File not found: {path.name}")

        if not path.is_file():
            raise ConverterError(f"Not a file: {path.name}")

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(f"Unsupported file type: {path.suffix or 'unknown'}")

    @staticmethod
    def _format_exception(path: Path, exc: Exception) -> str:
        message = str(exc).strip()
        if not message:
            message = exc.__class__.__name__
        return f"{path.name}: {message}"
