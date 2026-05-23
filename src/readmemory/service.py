from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from .ids import new_id

from .anchors import AnchorResolver
from .epub_importer import parse_epub
from .markdown import render_daily_log, write_daily_log
from .repository import Repository
from .storage import Store


class ReadMemoryService:
    def __init__(self, store: Store):
        self.store = store
        self.repo = Repository(store)
        self.anchor_resolver = AnchorResolver(self.repo)

    def import_book(self, path: Path) -> dict[str, Any]:
        parsed = parse_epub(path)
        existing = self.repo.get_book_by_hash(parsed.epub_hash)
        if existing:
            return {"book": existing, "source_units_created": 0, "status": "already_imported"}

        book = self.repo.create_book(
            title=parsed.title,
            author=parsed.author,
            language=parsed.language,
            epub_hash=parsed.epub_hash,
            source_path=str(path),
            total_words=parsed.total_words,
            import_status="importing",
        )
        for unit in parsed.source_units:
            self.repo.create_source_unit_from_import(book_id=book["id"], unit=unit)
        book = self.repo.update_book_imported(book_id=book["id"], total_words=parsed.total_words)
        return {
            "book": book,
            "source_units_created": len(parsed.source_units),
            "status": "imported",
        }

    def search_source(self, *, book_id: str, quote: str, limit: int = 10) -> dict[str, Any]:
        return {
            "book_id": book_id,
            "quote": quote,
            "matches": self.repo.search_source_exact(book_id=book_id, quote=quote, limit=limit),
        }

    def find_anchor(self, *, book_id: str, quote: str, limit: int = 5) -> dict[str, Any]:
        return self.anchor_resolver.find_anchor(book_id=book_id, quote=quote, limit=limit)

    def get_latest_anchor(self, *, book_id: str) -> dict[str, Any] | None:
        return self.store.fetchone(
            """
            SELECT a.*
            FROM anchors a
            WHERE a.book_id = ?
            ORDER BY a.created_at DESC
            LIMIT 1
            """,
            (book_id,),
        )

    def log_progress(
        self,
        *,
        book_id: str,
        stop_quote: str,
        start_quote: str | None = None,
        session_date: str | None = None,
        user_note: str | None = None,
    ) -> dict[str, Any]:
        result = self.find_anchor(book_id=book_id, quote=stop_quote)
        if result["status"] != "resolved" or not result["selected"]:
            raise ValueError("Could not resolve stop_quote to a verified anchor")

        end_anchor = result["selected"]
        start_anchor_id = None
        if start_quote:
            start_result = self.find_anchor(book_id=book_id, quote=start_quote)
            if start_result["status"] == "resolved" and start_result["selected"]:
                start_anchor_id = start_result["selected"]["id"]

        source_unit = self.store.fetchone(
            "SELECT word_count FROM source_units WHERE id = ?",
            (end_anchor["source_unit_id"],),
        )
        session_id = new_id("session")
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.store.execute(
            """
            INSERT INTO reading_sessions (
                id, book_id, session_date, start_anchor_id, end_anchor_id,
                words_read, status, user_note, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                book_id,
                session_date or date.today().isoformat(),
                start_anchor_id,
                end_anchor["id"],
                int((source_unit or {}).get("word_count") or 0),
                "partial",
                user_note,
                now,
                now,
            ),
        )
        return {
            "session": self.store.fetchone("SELECT * FROM reading_sessions WHERE id = ?", (session_id,)),
            "end_anchor": end_anchor,
        }

    def _resolve_note_anchor(self, *, book_id: str, anchor_id: str | None, fallback_quote: str | None = None) -> str | None:
        if anchor_id:
            return anchor_id
        if fallback_quote:
            latest = self.find_anchor(book_id=book_id, quote=fallback_quote)
            if latest["status"] == "resolved" and latest["selected"]:
                return latest["selected"]["id"]
        latest_anchor = self.get_latest_anchor(book_id=book_id)
        return latest_anchor["id"] if latest_anchor else None

    def _create_review_due_at(self, *, days: int) -> str:
        return (datetime.now(timezone.utc) + timedelta(days=days)).replace(microsecond=0).isoformat()

    def add_vocabulary(
        self,
        *,
        book_id: str,
        words: list[str],
        source_sentence: str | None = None,
        user_meaning: str | None = None,
        ai_context_meaning: str | None = None,
        anchor_id: str | None = None,
    ) -> list[dict[str, Any]]:
        resolved_anchor_id = self._resolve_note_anchor(
            book_id=book_id,
            anchor_id=anchor_id,
            fallback_quote=source_sentence,
        )
        created: list[dict[str, Any]] = []
        for word in words:
            note = self.repo.create_vocabulary_note(
                book_id=book_id,
                anchor_id=resolved_anchor_id or None,
                word=word,
            )
            if source_sentence or user_meaning or ai_context_meaning:
                self.store.execute(
                    """
                    UPDATE vocabulary_notes
                    SET source_sentence = ?, user_meaning = ?, ai_context_meaning = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (source_sentence, user_meaning, ai_context_meaning, datetime.now(timezone.utc).replace(microsecond=0).isoformat(), note["id"]),
                )
            self.repo.create_review_item(
                book_id=book_id,
                item_type="vocabulary",
                item_id=note["id"],
                due_at=self._create_review_due_at(days=1),
            )
            created.append(self.store.fetchone("SELECT * FROM vocabulary_notes WHERE id = ?", (note["id"],)))
        return created

    def add_sentence(
        self,
        *,
        book_id: str,
        sentence: str,
        reason_saved: str | None = None,
        pattern_note: str | None = None,
        imitation_examples: list[str] | None = None,
        anchor_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_anchor_id = self._resolve_note_anchor(book_id=book_id, anchor_id=anchor_id, fallback_quote=sentence)
        note = self.repo.create_sentence_note(
            book_id=book_id,
            anchor_id=resolved_anchor_id or None,
            sentence=sentence,
        )
        self.store.execute(
            """
            UPDATE sentence_notes
            SET reason_saved = ?, pattern_note = ?, imitation_examples = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                reason_saved,
                pattern_note,
                None if imitation_examples is None else str(imitation_examples),
                datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                note["id"],
            ),
        )
        self.repo.create_review_item(
            book_id=book_id,
            item_type="sentence",
            item_id=note["id"],
            due_at=self._create_review_due_at(days=1),
        )
        return self.store.fetchone("SELECT * FROM sentence_notes WHERE id = ?", (note["id"],))

    def add_thought(
        self,
        *,
        book_id: str,
        thought_text: str,
        anchor_id: str | None = None,
        related_quote: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        resolved_anchor_id = self._resolve_note_anchor(
            book_id=book_id,
            anchor_id=anchor_id,
            fallback_quote=related_quote or thought_text,
        )
        note = self.repo.create_thought_note(
            book_id=book_id,
            anchor_id=resolved_anchor_id or None,
            thought_text=thought_text,
        )
        self.store.execute(
            """
            UPDATE thought_notes
            SET related_quote = ?, tags = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                related_quote,
                None if tags is None else str(tags),
                datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                note["id"],
            ),
        )
        self.repo.create_review_item(
            book_id=book_id,
            item_type="thought",
            item_id=note["id"],
            due_at=self._create_review_due_at(days=7),
        )
        return self.store.fetchone("SELECT * FROM thought_notes WHERE id = ?", (note["id"],))

    def get_today_records(self, *, book_id: str, on_date: str | None = None) -> dict[str, Any]:
        target = on_date or date.today().isoformat()
        return {
            "sessions": self.store.fetchall(
                "SELECT * FROM reading_sessions WHERE book_id = ? AND session_date = ? ORDER BY created_at ASC",
                (book_id, target),
            ),
            "vocabulary": self.store.fetchall(
                "SELECT * FROM vocabulary_notes WHERE book_id = ? AND date(created_at) = ? ORDER BY created_at ASC",
                (book_id, target),
            ),
            "sentences": self.store.fetchall(
                "SELECT * FROM sentence_notes WHERE book_id = ? AND date(created_at) = ? ORDER BY created_at ASC",
                (book_id, target),
            ),
            "thoughts": self.store.fetchall(
                "SELECT * FROM thought_notes WHERE book_id = ? AND date(created_at) = ? ORDER BY created_at ASC",
                (book_id, target),
            ),
        }

    def get_due_reviews(self, *, on_date: str | None = None) -> list[dict[str, Any]]:
        target = on_date or "9999-12-31"
        return self.store.fetchall(
            "SELECT * FROM review_items WHERE due_at <= ? ORDER BY due_at ASC, created_at ASC",
            (target,),
        )

    def record_review_result(self, *, review_item_id: str, result: str) -> dict[str, Any]:
        review = self.store.fetchone("SELECT * FROM review_items WHERE id = ?", (review_item_id,))
        if not review:
            raise KeyError(review_item_id)
        current_interval = int(review["interval_days"] or 1)
        if result == "correct":
            next_interval = max(current_interval + 2, current_interval * 2)
            ease = min(float(review["ease"] or 2.5) + 0.05, 3.0)
        elif result == "wrong":
            next_interval = 1
            ease = max(float(review["ease"] or 2.5) - 0.2, 1.3)
        else:
            next_interval = 1
            ease = float(review["ease"] or 2.5)

        due_at = (datetime.now(timezone.utc) + timedelta(days=next_interval)).replace(microsecond=0).isoformat()
        self.store.execute(
            """
            UPDATE review_items
            SET due_at = ?, interval_days = ?, ease = ?, last_result = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                due_at,
                next_interval,
                ease,
                result,
                datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                review_item_id,
            ),
        )
        return self.store.fetchone("SELECT * FROM review_items WHERE id = ?", (review_item_id,))

    def generate_daily_log(self, *, book_id: str, on_date: str | None = None, output_dir: Path | None = None) -> dict[str, Any]:
        target = on_date or date.today().isoformat()
        records = self.get_today_records(book_id=book_id, on_date=target)
        reviews = self.get_due_reviews(on_date=target)
        markdown = render_daily_log(date=target, records=records, reviews=reviews)
        path = write_daily_log(
            output_dir=output_dir or Path.cwd(),
            date=target,
            markdown=markdown,
        )
        return {"path": str(path), "markdown": markdown}
