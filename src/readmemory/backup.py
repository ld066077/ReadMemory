from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile
import json
import sqlite3


def create_backup(*, paths: Any, output_dir: Path | None = None) -> dict[str, Any]:
    target_dir = output_dir or paths.data_dir / "backups"
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    filename = f"readmemory-backup-{timestamp.strftime('%Y%m%dT%H%M%SZ')}.zip"
    target = _available_target(target_dir / filename)

    with TemporaryDirectory() as tmp:
        snapshot = Path(tmp) / "readmemory.sqlite"
        source_conn = sqlite3.connect(paths.db_path)
        backup_conn = sqlite3.connect(snapshot)
        try:
            source_conn.backup(backup_conn)
        finally:
            backup_conn.close()
            source_conn.close()

        manifest = {
            "format": "readmemory-backup-v1",
            "created_at": timestamp.isoformat(),
            "database": "database/readmemory.sqlite",
            "config_included": paths.config_path.exists(),
            "books_included": paths.books_dir.exists(),
            "exports_included": paths.exports_dir.exists(),
        }

        with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
            archive.write(snapshot, "database/readmemory.sqlite")
            if paths.config_path.exists():
                archive.write(paths.config_path, "config/readmemory.toml")
            _add_tree(archive, paths.books_dir, "books")
            _add_tree(archive, paths.exports_dir, "exports")
            archive.writestr(
                "manifest.json",
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            )

    return {
        "status": "created",
        "path": str(target),
        "size_bytes": target.stat().st_size,
        "manifest": manifest,
    }


def _add_tree(archive: ZipFile, source: Path, prefix: str) -> None:
    if not source.exists():
        return
    for path in sorted(source.rglob("*")):
        if path.is_file():
            archive.write(path, str(Path(prefix) / path.relative_to(source)))


def _available_target(target: Path) -> Path:
    if not target.exists():
        return target
    counter = 2
    while True:
        candidate = target.with_name(f"{target.stem}-{counter}{target.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
