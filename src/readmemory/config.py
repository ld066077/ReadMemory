from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib


@dataclass(frozen=True)
class ReadMemorySettings:
    log_level: str = "INFO"
    default_language: str = "en"
    review_horizon_days: int = 7
    allow_unanchored_notes: bool = True
    markdown_filename_pattern: str = "{date}-reading-log.md"
    review_interval_new_days: int = 1
    review_interval_correct_days: int = 3
    review_interval_weekly_days: int = 7

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "ReadMemorySettings":
        return cls(**{k: v for k, v in mapping.items() if k in cls.__annotations__})


def load_settings(config_path: Path | None) -> ReadMemorySettings:
    if config_path is None or not config_path.exists():
        return ReadMemorySettings()
    with config_path.open("rb") as handle:
        mapping = tomllib.load(handle)
    return ReadMemorySettings.from_mapping(mapping)

