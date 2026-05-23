from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import ReadMemorySettings, load_settings
from .paths import ReadMemoryPaths, resolve_paths


@dataclass(frozen=True)
class ReadMemoryRuntime:
    paths: ReadMemoryPaths
    settings: ReadMemorySettings


def build_runtime(config_path: Path | None = None) -> ReadMemoryRuntime:
    paths = resolve_paths()
    settings = load_settings(config_path or paths.config_path)
    return ReadMemoryRuntime(paths=paths, settings=settings)

