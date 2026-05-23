from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
import sqlite3

from .schema import initialize_schema


class Store:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.session() as conn:
            initialize_schema(conn)

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        with self.session() as conn:
            conn.execute(sql, params)
            conn.commit()

    def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.session() as conn:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None

    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.session() as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

