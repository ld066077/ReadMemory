from __future__ import annotations

from pathlib import Path
from typing import Any

from .ids import new_id
from .time import utc_now


def import_parsed_book(*, store: Any, parsed: Any, source_path: Path) -> dict[str, Any]:
    existing = store.fetchone("SELECT * FROM books WHERE epub_hash = ?", (parsed.epub_hash,))
    if existing:
        return {"book": existing, "source_units_created": 0, "status": "already_imported"}

    book_id = new_id("book")
    now = utc_now()
    with store.transaction() as conn:
        duplicate = conn.execute(
            "SELECT * FROM books WHERE epub_hash = ?", (parsed.epub_hash,)
        ).fetchone()
        if duplicate:
            return {
                "book": dict(duplicate),
                "source_units_created": 0,
                "status": "already_imported",
            }
        conn.execute(
            """
            INSERT INTO books (
                id, title, author, language, epub_hash, source_path,
                total_words, import_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                book_id,
                parsed.title,
                parsed.author,
                parsed.language,
                parsed.epub_hash,
                str(source_path),
                parsed.total_words,
                "importing",
                now,
                now,
            ),
        )
        for unit in parsed.source_units:
            conn.execute(
                """
                INSERT INTO source_units (
                    id, book_id, unit_type, chapter_index, paragraph_index, sentence_index,
                    text, word_count, content_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_id("unit"),
                    book_id,
                    unit.unit_type,
                    unit.chapter_index,
                    unit.paragraph_index,
                    unit.sentence_index,
                    unit.text,
                    unit.word_count,
                    unit.content_hash,
                    now,
                    now,
                ),
            )
        conn.execute(
            "UPDATE books SET import_status = ?, updated_at = ? WHERE id = ?",
            ("imported", now, book_id),
        )
    book = store.fetchone("SELECT * FROM books WHERE id = ?", (book_id,))
    return {
        "book": book,
        "source_units_created": len(parsed.source_units),
        "status": "imported",
    }
