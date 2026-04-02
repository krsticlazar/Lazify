from __future__ import annotations

import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent


def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).joinpath(*parts)
    return PROJECT_ROOT.joinpath(*parts)


def icon_path() -> Path:
    candidates = (
        resource_path("lazify.ico"),
        resource_path("assets", "lazify.ico"),
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]
