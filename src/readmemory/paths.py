from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class ReadMemoryPaths:
    config_dir: Path
    config_path: Path
    data_dir: Path
    db_path: Path
    books_dir: Path
    exports_dir: Path
    logs_dir: Path

    def ensure(self) -> None:
        for path in (
            self.config_dir,
            self.data_dir,
            self.db_path.parent,
            self.books_dir,
            self.exports_dir,
            self.logs_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


def resolve_paths() -> ReadMemoryPaths:
    home = Path.home()
    config_dir = Path(os.getenv("READMEMORY_CONFIG_DIR", home / ".config" / "readmemory"))
    data_dir = Path(os.getenv("READMEMORY_DATA_DIR", home / ".local" / "share" / "readmemory"))
    db_path = Path(os.getenv("READMEMORY_DB_PATH", data_dir / "readmemory.sqlite"))
    books_dir = Path(os.getenv("READMEMORY_BOOKS_DIR", data_dir / "books"))
    exports_dir = Path(os.getenv("READMEMORY_EXPORT_DIR", data_dir / "exports"))
    logs_dir = Path(os.getenv("READMEMORY_LOG_DIR", data_dir / "logs"))
    return ReadMemoryPaths(
        config_dir=config_dir,
        config_path=config_dir / "readmemory.toml",
        data_dir=data_dir,
        db_path=db_path,
        books_dir=books_dir,
        exports_dir=exports_dir,
        logs_dir=logs_dir,
    )

