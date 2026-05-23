from __future__ import annotations

import sqlite3


SCHEMA_VERSION = "1"


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS schema_meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS books (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        language TEXT NOT NULL DEFAULT 'en',
        epub_hash TEXT NOT NULL UNIQUE,
        source_path TEXT,
        total_words INTEGER NOT NULL DEFAULT 0,
        import_status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS source_units (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        unit_type TEXT NOT NULL,
        chapter_index INTEGER,
        paragraph_index INTEGER,
        sentence_index INTEGER,
        text TEXT NOT NULL,
        word_count INTEGER NOT NULL DEFAULT 0,
        char_start INTEGER,
        char_end INTEGER,
        content_hash TEXT,
        epub_cfi TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS anchors (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        source_unit_id TEXT,
        anchor_quote TEXT NOT NULL,
        before_quote TEXT,
        after_quote TEXT,
        char_offset INTEGER,
        confidence REAL NOT NULL DEFAULT 0.0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (source_unit_id) REFERENCES source_units(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reading_sessions (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        session_date TEXT NOT NULL,
        start_anchor_id TEXT,
        end_anchor_id TEXT,
        words_read INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'partial',
        user_note TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (start_anchor_id) REFERENCES anchors(id) ON DELETE SET NULL,
        FOREIGN KEY (end_anchor_id) REFERENCES anchors(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS vocabulary_notes (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        anchor_id TEXT,
        word TEXT NOT NULL,
        lemma TEXT,
        source_sentence TEXT,
        user_meaning TEXT,
        ai_context_meaning TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        next_review_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (anchor_id) REFERENCES anchors(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sentence_notes (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        anchor_id TEXT,
        sentence TEXT NOT NULL,
        reason_saved TEXT,
        pattern_note TEXT,
        imitation_examples TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        next_review_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (anchor_id) REFERENCES anchors(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS thought_notes (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        anchor_id TEXT,
        thought_text TEXT NOT NULL,
        related_quote TEXT,
        tags TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (anchor_id) REFERENCES anchors(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS review_items (
        id TEXT PRIMARY KEY,
        item_type TEXT NOT NULL,
        item_id TEXT NOT NULL,
        book_id TEXT NOT NULL,
        due_at TEXT NOT NULL,
        interval_days INTEGER NOT NULL DEFAULT 1,
        ease REAL NOT NULL DEFAULT 2.5,
        last_result TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS exports (
        id TEXT PRIMARY KEY,
        export_type TEXT NOT NULL,
        book_id TEXT,
        export_date TEXT NOT NULL,
        path TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_source_units_book_id ON source_units(book_id)",
    "CREATE INDEX IF NOT EXISTS idx_anchors_book_id ON anchors(book_id)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_book_date ON reading_sessions(book_id, session_date)",
    "CREATE INDEX IF NOT EXISTS idx_review_items_due ON review_items(due_at)",
]


def initialize_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    for statement in SCHEMA_STATEMENTS:
        conn.execute(statement)
    conn.execute(
        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
        ("schema_version", SCHEMA_VERSION),
    )
    conn.commit()

