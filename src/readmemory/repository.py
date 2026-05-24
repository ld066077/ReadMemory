from __future__ import annotations

from typing import Any
import difflib
import re

from .epub_importer import SourceUnit
from .ids import new_id
from .storage import Store
from .time import utc_now


def normalize_quote(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def match_score(query: str, candidate: str) -> float:
    normalized_query = normalize_quote(query)
    normalized_candidate = normalize_quote(candidate)
    if not normalized_query or not normalized_candidate:
        return 0.0
    if normalized_query == normalized_candidate:
        return 1.0
    if normalized_query in normalized_candidate:
        return 0.95

    query_tokens = set(normalized_query.split())
    candidate_tokens = set(normalized_candidate.split())
    token_score = 0.0
    if query_tokens:
        token_score = len(query_tokens & candidate_tokens) / len(query_tokens)

    sequence_score = difflib.SequenceMatcher(None, normalized_query, normalized_candidate).ratio()
    return max(sequence_score, token_score * 0.9)


class Repository:
    def __init__(self, store: Store):
        self.store = store

    def create_book(
        self,
        *,
        title: str,
        epub_hash: str,
        author: str | None = None,
        language: str = "en",
        source_path: str | None = None,
        total_words: int = 0,
        import_status: str = "pending",
    ) -> dict[str, Any]:
        item_id = new_id("book")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO books (
                id, title, author, language, epub_hash, source_path,
                total_words, import_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, title, author, language, epub_hash, source_path, total_words, import_status, now, now),
        )
        return self.get_book(item_id)

    def get_book(self, book_id: str) -> dict[str, Any]:
        row = self.store.fetchone("SELECT * FROM books WHERE id = ?", (book_id,))
        if row is None:
            raise KeyError(book_id)
        return row

    def get_book_by_hash(self, epub_hash: str) -> dict[str, Any] | None:
        return self.store.fetchone("SELECT * FROM books WHERE epub_hash = ?", (epub_hash,))

    def list_books(self, *, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.fetchall(
            """
            SELECT * FROM books
            ORDER BY updated_at DESC, created_at DESC
            LIMIT ?
            """,
            (limit,),
        )

    def search_books(self, *, query: str, limit: int = 10) -> list[dict[str, Any]]:
        term = f"%{query}%"
        return self.store.fetchall(
            """
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR id = ?
            ORDER BY updated_at DESC, created_at DESC
            LIMIT ?
            """,
            (term, term, query, limit),
        )

    def update_book_imported(self, *, book_id: str, total_words: int) -> dict[str, Any]:
        self.store.execute(
            "UPDATE books SET total_words = ?, import_status = ?, updated_at = ? WHERE id = ?",
            (total_words, "imported", utc_now(), book_id),
        )
        return self.get_book(book_id)

    def create_source_unit(self, *, book_id: str, unit_type: str, text: str) -> dict[str, Any]:
        item_id = new_id("unit")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO source_units (id, book_id, unit_type, text, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item_id, book_id, unit_type, text, now, now),
        )
        return self.store.fetchone("SELECT * FROM source_units WHERE id = ?", (item_id,))

    def create_source_unit_from_import(self, *, book_id: str, unit: SourceUnit) -> dict[str, Any]:
        item_id = new_id("unit")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO source_units (
                id, book_id, unit_type, chapter_index, paragraph_index, sentence_index,
                text, word_count, content_hash, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
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
        return self.store.fetchone("SELECT * FROM source_units WHERE id = ?", (item_id,))

    def search_source_exact(self, *, book_id: str, quote: str, limit: int = 10) -> list[dict[str, Any]]:
        return self.store.fetchall(
            """
            SELECT * FROM source_units
            WHERE book_id = ? AND text LIKE ?
            ORDER BY chapter_index, paragraph_index, sentence_index
            LIMIT ?
            """,
            (book_id, f"%{quote}%", limit),
        )

    def source_units_for_anchor_search(self, *, book_id: str) -> list[dict[str, Any]]:
        return self.store.fetchall(
            """
            SELECT * FROM source_units
            WHERE book_id = ? AND unit_type IN ('paragraph', 'sentence')
            ORDER BY chapter_index, paragraph_index, sentence_index
            """,
            (book_id,),
        )

    def create_anchor(self, *, book_id: str, source_unit_id: str, anchor_quote: str, confidence: float = 1.0) -> dict[str, Any]:
        item_id = new_id("anchor")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO anchors (
                id, book_id, source_unit_id, anchor_quote, confidence, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, book_id, source_unit_id, anchor_quote, confidence, now, now),
        )
        return self.store.fetchone("SELECT * FROM anchors WHERE id = ?", (item_id,))

    def create_vocabulary_note(self, *, book_id: str, anchor_id: str | None, word: str) -> dict[str, Any]:
        item_id = new_id("vocab")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO vocabulary_notes (id, book_id, anchor_id, word, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item_id, book_id, anchor_id, word, now, now),
        )
        return self.store.fetchone("SELECT * FROM vocabulary_notes WHERE id = ?", (item_id,))

    def create_sentence_note(self, *, book_id: str, anchor_id: str | None, sentence: str) -> dict[str, Any]:
        item_id = new_id("sentence")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO sentence_notes (id, book_id, anchor_id, sentence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item_id, book_id, anchor_id, sentence, now, now),
        )
        return self.store.fetchone("SELECT * FROM sentence_notes WHERE id = ?", (item_id,))

    def create_thought_note(self, *, book_id: str, anchor_id: str | None, thought_text: str) -> dict[str, Any]:
        item_id = new_id("thought")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO thought_notes (id, book_id, anchor_id, thought_text, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item_id, book_id, anchor_id, thought_text, now, now),
        )
        return self.store.fetchone("SELECT * FROM thought_notes WHERE id = ?", (item_id,))

    def create_review_item(self, *, book_id: str, item_type: str, item_id: str, due_at: str) -> dict[str, Any]:
        review_id = new_id("review")
        now = utc_now()
        self.store.execute(
            """
            INSERT INTO review_items (
                id, item_type, item_id, book_id, due_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (review_id, item_type, item_id, book_id, due_at, now, now),
        )
        return self.store.fetchone("SELECT * FROM review_items WHERE id = ?", (review_id,))
