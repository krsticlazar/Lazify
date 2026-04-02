from __future__ import annotations

from pathlib import Path

import mammoth
from pdfminer.high_level import extract_text
from pptx import Presentation


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
}


class ConverterError(Exception):
    pass


class UnsupportedFileTypeError(ConverterError):
    pass


class FileConverter:
    def is_supported(self, source_path: str | Path) -> bool:
        return Path(source_path).suffix.lower() in SUPPORTED_EXTENSIONS

    def default_output_path(self, source_path: str | Path) -> Path:
        source = Path(source_path).expanduser().resolve()
        return source.with_suffix(".md")

    def suggest_output_path(
        self,
        source_path: str | Path,
        reserved_paths: set[Path] | None = None,
    ) -> Path:
        candidate = self.default_output_path(source_path)
        reserved = {Path(path).resolve() for path in (reserved_paths or set())}

        if candidate.resolve() not in reserved and not candidate.exists():
            return candidate

        counter = 1
        while True:
            fallback = candidate.with_name(f"{candidate.stem} ({counter}){candidate.suffix}")
            resolved_fallback = fallback.resolve()
            if resolved_fallback not in reserved and not fallback.exists():
                return fallback
            counter += 1

    def convert_file(self, source_path: str | Path) -> str:
        path = Path(source_path).expanduser().resolve()
        self._validate_source(path)

        try:
            if path.suffix.lower() == ".pdf":
                markdown_text = self._convert_pdf(path)
            elif path.suffix.lower() == ".docx":
                markdown_text = self._convert_docx(path)
            elif path.suffix.lower() == ".pptx":
                markdown_text = self._convert_pptx(path)
            else:
                raise UnsupportedFileTypeError(f"Unsupported file type: {path.suffix or 'unknown'}")
        except ConverterError:
            raise
        except Exception as exc:
            raise ConverterError(self._format_exception(path, exc)) from exc

        if not markdown_text.strip():
            raise ConverterError(f"{path.name}: No readable content found.")

        return markdown_text.strip()

    def save_markdown(
        self,
        source_path: str | Path,
        markdown_text: str,
        target_path: str | Path | None = None,
    ) -> Path:
        source = Path(source_path).expanduser().resolve()
        destination = Path(target_path).expanduser().resolve() if target_path else self.default_output_path(source)

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

    def _convert_pdf(self, path: Path) -> str:
        text = extract_text(str(path))
        return self._normalize_text(text)

    def _convert_docx(self, path: Path) -> str:
        with path.open("rb") as handle:
            result = mammoth.convert_to_markdown(handle)
        return self._normalize_text(result.value)

    def _convert_pptx(self, path: Path) -> str:
        presentation = Presentation(str(path))
        sections: list[str] = []

        for slide_index, slide in enumerate(presentation.slides, start=1):
            slide_blocks: list[str] = [f"# Slide {slide_index}"]

            for shape in slide.shapes:
                if not hasattr(shape, "text"):
                    continue

                text = self._normalize_text(shape.text)
                if not text:
                    continue

                if getattr(shape, "has_text_frame", False) and shape == getattr(slide.shapes, "title", None):
                    slide_blocks.append(f"## {text}")
                    continue

                paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
                for paragraph in paragraphs:
                    slide_blocks.append(f"- {paragraph}")

            sections.append("\n\n".join(slide_blocks))

        return "\n\n---\n\n".join(section for section in sections if section.strip())

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
        compact: list[str] = []
        previous_blank = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not previous_blank:
                    compact.append("")
                previous_blank = True
                continue

            compact.append(stripped)
            previous_blank = False

        return "\n".join(compact).strip()

    @staticmethod
    def _format_exception(path: Path, exc: Exception) -> str:
        message = str(exc).strip()
        if not message:
            message = exc.__class__.__name__
        return f"{path.name}: {message}"
