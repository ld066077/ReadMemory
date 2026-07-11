from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import json

from .anchors import AnchorResolver
from .backup import create_backup
from .config import ReadMemorySettings
from .epub_importer import parse_epub
from .ids import new_id
from .import_store import import_parsed_book
from .markdown import render_daily_log, write_daily_log
from .maintenance import MaintenanceMixin
from .paths import ReadMemoryPaths
from .repository import Repository, match_score, normalize_quote
from .storage import Store


class ReadMemoryService(MaintenanceMixin):
    def __init__(
        self,
        store: Store,
        *,
        settings: ReadMemorySettings | None = None,
        paths: ReadMemoryPaths | None = None,
    ):
        self.store = store
        self.settings = settings or ReadMemorySettings()
        self.paths = paths
        self.repo = Repository(store)
        self.anchor_resolver = AnchorResolver(self.repo)

    def import_book(self, path: Path) -> dict[str, Any]:
        parsed = parse_epub(path)
        return import_parsed_book(store=self.store, parsed=parsed, source_path=path)

    def list_books(self, *, limit: int = 100) -> list[dict[str, Any]]:
        return self.repo.list_books(limit=max(limit, 0))

    def search_books(self, *, query: str, limit: int = 10) -> list[dict[str, Any]]:
        normalized_query = normalize_quote(query)
        if not normalized_query:
            return []

        scored: list[dict[str, Any]] = []
        for book in self.repo.list_books(limit=1000):
            title = str(book.get("title") or "")
            author = str(book.get("author") or "")
            book_id = str(book.get("id") or "")
            score = 1.0 if query == book_id else max(
                match_score(query, title),
                match_score(query, author),
                match_score(query, f"{title} {author} {book_id}"),
            )
            if score >= 0.25:
                item = dict(book)
                item["match_score"] = round(score, 4)
                scored.append(item)

        scored.sort(key=lambda item: item["match_score"], reverse=True)
        return scored[: max(limit, 0)]

    def resolve_book(self, *, book_ref: str, limit: int = 5) -> dict[str, Any]:
        try:
            book = self.repo.get_book(book_ref)
        except KeyError:
            book = None
        if book:
            return {
                "status": "resolved",
                "selected": book,
                "candidates": [dict(book, match_score=1.0)],
            }

        candidates = self.search_books(query=book_ref, limit=limit)
        selected = None
        status = "not_found"
        if candidates:
            top = candidates[0]
            second = candidates[1] if len(candidates) > 1 else None
            normalized_ref = normalize_quote(book_ref)
            normalized_title = normalize_quote(str(top.get("title") or ""))
            score_gap = top["match_score"] - (second["match_score"] if second else 0.0)
            if normalized_ref == normalized_title or top["match_score"] >= 0.9:
                selected = top
                status = "resolved"
            elif top["match_score"] >= 0.55 and score_gap >= 0.1:
                selected = top
                status = "resolved"
            else:
                status = "ambiguous"
        return {"status": status, "selected": selected, "candidates": candidates}

    def _book_id_from_ref(self, *, book_id: str | None = None, book_ref: str | None = None) -> str:
        if book_id:
            self.repo.get_book(book_id)
            return book_id
        if not book_ref:
            raise ValueError("book_id or book_ref is required")
        resolved = self.resolve_book(book_ref=book_ref)
        if resolved["status"] != "resolved" or not resolved["selected"]:
            raise ValueError(f"Could not resolve book_ref: {book_ref}")
        return resolved["selected"]["id"]

    def search_source(
        self,
        *,
        book_id: str | None = None,
        quote: str,
        limit: int = 10,
        book_ref: str | None = None,
    ) -> dict[str, Any]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        return {
            "book_id": resolved_book_id,
            "quote": quote,
            "matches": self.repo.search_source_exact(book_id=resolved_book_id, quote=quote, limit=limit),
        }

    def find_anchor(
        self,
        *,
        book_id: str | None = None,
        quote: str = "",
        limit: int = 5,
        book_ref: str | None = None,
    ) -> dict[str, Any]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        return self.anchor_resolver.find_anchor(book_id=resolved_book_id, quote=quote, limit=limit)

    def _materialize_anchor(self, *, book_id: str, quote: str, selected: dict[str, Any]) -> dict[str, Any]:
        source_unit_id = str(selected["source_unit_id"])
        existing = self.repo.find_anchor(
            book_id=book_id,
            source_unit_id=source_unit_id,
            anchor_quote=quote,
        )
        if existing:
            return existing
        return self.repo.create_anchor(
            book_id=book_id,
            source_unit_id=source_unit_id,
            anchor_quote=quote,
            confidence=float(selected.get("confidence") or 0.0),
        )

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
        book_id: str | None = None,
        stop_quote: str,
        start_quote: str | None = None,
        session_date: str | None = None,
        user_note: str | None = None,
        book_ref: str | None = None,
        allow_unanchored: bool = False,
    ) -> dict[str, Any]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        result = self.find_anchor(book_id=resolved_book_id, quote=stop_quote)
        if result["status"] != "resolved" or not result["selected"]:
            if not allow_unanchored:
                raise ValueError("Could not resolve stop_quote to a verified anchor")
            session = self._create_reading_session(
                book_id=resolved_book_id,
                session_date=session_date,
                start_anchor_id=None,
                end_anchor_id=None,
                words_read=0,
                status="unanchored",
                user_note=user_note or f"Unanchored stop quote: {stop_quote}",
            )
            return {
                "session": session,
                "end_anchor": None,
                "anchor_result": result,
                "status": "unanchored",
            }

        end_anchor = self._materialize_anchor(
            book_id=resolved_book_id, quote=stop_quote, selected=result["selected"]
        )
        start_anchor_id = None
        if start_quote:
            start_result = self.find_anchor(book_id=resolved_book_id, quote=start_quote)
            if start_result["status"] == "resolved" and start_result["selected"]:
                start_anchor_id = self._materialize_anchor(
                    book_id=resolved_book_id,
                    quote=start_quote,
                    selected=start_result["selected"],
                )["id"]

        source_unit = self.store.fetchone(
            "SELECT word_count FROM source_units WHERE id = ?",
            (end_anchor["source_unit_id"],),
        )
        session = self._create_reading_session(
            book_id=resolved_book_id,
            session_date=session_date,
            start_anchor_id=start_anchor_id,
            end_anchor_id=end_anchor["id"],
            words_read=int((source_unit or {}).get("word_count") or 0),
            status="partial",
            user_note=user_note,
        )
        return {
            "session": session,
            "end_anchor": end_anchor,
            "anchor_result": result,
        }

    def _record_action(
        self, *, action_type: str, entity_type: str, entity_id: str, payload: dict[str, Any]
    ) -> None:
        self.store.execute(
            """
            INSERT INTO action_history (id, action_type, entity_type, entity_id, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                new_id("action"), action_type, entity_type, entity_id,
                json.dumps(payload, ensure_ascii=False),
                datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            ),
        )

    def _create_reading_session(
        self,
        *,
        book_id: str,
        session_date: str | None,
        start_anchor_id: str | None,
        end_anchor_id: str | None,
        words_read: int,
        status: str,
        user_note: str | None,
    ) -> dict[str, Any]:
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
                end_anchor_id,
                words_read,
                status,
                user_note,
                now,
                now,
            ),
        )
        session = self.store.fetchone("SELECT * FROM reading_sessions WHERE id = ?", (session_id,))
        if session:
            self._record_action(action_type="create", entity_type="session", entity_id=session_id, payload={})
        return session

    def _resolve_note_anchor(
        self,
        *,
        book_id: str,
        anchor_id: str | None,
        fallback_quote: str | None = None,
    ) -> str | None:
        if anchor_id:
            anchor = self.store.fetchone(
                "SELECT id FROM anchors WHERE id = ? AND book_id = ?", (anchor_id, book_id)
            )
            if not anchor:
                raise ValueError("anchor_id does not belong to the selected book")
            return anchor_id
        if fallback_quote:
            latest = self.find_anchor(book_id=book_id, quote=fallback_quote)
            if latest["status"] == "resolved" and latest["selected"]:
                return self._materialize_anchor(
                    book_id=book_id, quote=fallback_quote, selected=latest["selected"]
                )["id"]
        return None

    def _create_review_due_at(self, *, days: int) -> str:
        return (datetime.now(timezone.utc) + timedelta(days=days)).replace(microsecond=0).isoformat()

    def add_vocabulary(
        self,
        *,
        book_id: str | None = None,
        words: list[str],
        source_sentence: str | None = None,
        user_meaning: str | None = None,
        ai_context_meaning: str | None = None,
        anchor_id: str | None = None,
        book_ref: str | None = None,
        note_date: str | None = None,
    ) -> list[dict[str, Any]]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        resolved_anchor_id = self._resolve_note_anchor(
            book_id=resolved_book_id,
            anchor_id=anchor_id,
            fallback_quote=source_sentence,
        )
        created: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for word in words:
            note = self.repo.create_vocabulary_note(
                book_id=resolved_book_id,
                anchor_id=resolved_anchor_id,
                word=word,
                note_date=note_date or date.today().isoformat(),
            )
            if source_sentence or user_meaning or ai_context_meaning:
                self.store.execute(
                    """
                    UPDATE vocabulary_notes
                    SET source_sentence = ?, user_meaning = ?, ai_context_meaning = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (source_sentence, user_meaning, ai_context_meaning, now, note["id"]),
                )
            self.repo.create_review_item(
                book_id=resolved_book_id,
                item_type="vocabulary",
                item_id=note["id"],
                due_at=self._create_review_due_at(days=self.settings.review_interval_new_days),
            )
            saved = self.store.fetchone("SELECT * FROM vocabulary_notes WHERE id = ?", (note["id"],))
            self._record_action(action_type="create", entity_type="vocabulary", entity_id=note["id"], payload={})
            created.append(saved)
        return created

    def add_sentence(
        self,
        *,
        book_id: str | None = None,
        sentence: str,
        reason_saved: str | None = None,
        pattern_note: str | None = None,
        imitation_examples: list[str] | None = None,
        anchor_id: str | None = None,
        note_date: str | None = None,
        book_ref: str | None = None,
    ) -> dict[str, Any]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        resolved_anchor_id = self._resolve_note_anchor(
            book_id=resolved_book_id,
            anchor_id=anchor_id,
            fallback_quote=sentence,
        )
        note = self.repo.create_sentence_note(
            book_id=resolved_book_id,
            note_date=note_date or date.today().isoformat(),
            anchor_id=resolved_anchor_id,
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
            book_id=resolved_book_id,
            item_type="sentence",
            item_id=note["id"],
            due_at=self._create_review_due_at(days=self.settings.review_interval_new_days),
        )
        saved = self.store.fetchone("SELECT * FROM sentence_notes WHERE id = ?", (note["id"],))
        self._record_action(action_type="create", entity_type="sentence", entity_id=note["id"], payload={})
        return saved

    def add_thought(
        self,
        *,
        book_id: str | None = None,
        thought_text: str,
        anchor_id: str | None = None,
        related_quote: str | None = None,
        tags: list[str] | None = None,
        book_ref: str | None = None,
        note_date: str | None = None,
    ) -> dict[str, Any]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        resolved_anchor_id = self._resolve_note_anchor(
            book_id=resolved_book_id,
            anchor_id=anchor_id,
            fallback_quote=related_quote or thought_text,
        )
        note = self.repo.create_thought_note(
            book_id=resolved_book_id,
            anchor_id=resolved_anchor_id,
            thought_text=thought_text,
            note_date=note_date or date.today().isoformat(),
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
            book_id=resolved_book_id,
            item_type="thought",
            item_id=note["id"],
            due_at=self._create_review_due_at(days=self.settings.review_interval_weekly_days),
        )
        saved = self.store.fetchone("SELECT * FROM thought_notes WHERE id = ?", (note["id"],))
        self._record_action(action_type="create", entity_type="thought", entity_id=note["id"], payload={})
        return saved

    def get_today_records(
        self,
        *,
        book_id: str | None = None,
        on_date: str | None = None,
        book_ref: str | None = None,
    ) -> dict[str, Any]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        target = on_date or date.today().isoformat()
        return {
            "sessions": self.store.fetchall(
                "SELECT * FROM reading_sessions WHERE book_id = ? AND session_date = ? ORDER BY created_at ASC",
                (resolved_book_id, target),
            ),
            "vocabulary": self.store.fetchall(
                "SELECT * FROM vocabulary_notes WHERE book_id = ? AND note_date = ? ORDER BY created_at ASC",
                (resolved_book_id, target),
            ),
            "sentences": self.store.fetchall(
                "SELECT * FROM sentence_notes WHERE book_id = ? AND note_date = ? ORDER BY created_at ASC",
                (resolved_book_id, target),
            ),
            "thoughts": self.store.fetchall(
                "SELECT * FROM thought_notes WHERE book_id = ? AND note_date = ? ORDER BY created_at ASC",
                (resolved_book_id, target),
            ),
        }

    def _review_cutoff(self, on_date: str | None) -> str:
        if not on_date:
            return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        if len(on_date) == 10:
            return f"{on_date}T23:59:59+00:00"
        return on_date

    def _review_rows(self, *, where: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
        return self.store.fetchall(
            f"""
            SELECT r.*, b.title AS book_title,
                CASE r.item_type
                    WHEN 'vocabulary' THEN v.word
                    WHEN 'sentence' THEN s.sentence
                    WHEN 'thought' THEN t.thought_text
                END AS title,
                CASE r.item_type
                    WHEN 'vocabulary' THEN COALESCE(v.source_sentence, v.user_meaning, v.ai_context_meaning)
                    WHEN 'sentence' THEN COALESCE(s.pattern_note, s.reason_saved)
                    WHEN 'thought' THEN t.related_quote
                END AS context,
                COALESCE(v.anchor_id, s.anchor_id, t.anchor_id) AS anchor_id
            FROM review_items r
            JOIN books b ON b.id = r.book_id
            LEFT JOIN vocabulary_notes v ON r.item_type = 'vocabulary' AND v.id = r.item_id
            LEFT JOIN sentence_notes s ON r.item_type = 'sentence' AND s.id = r.item_id
            LEFT JOIN thought_notes t ON r.item_type = 'thought' AND t.id = r.item_id
            WHERE {where}
            ORDER BY r.due_at ASC, r.created_at ASC
            """,
            params,
        )

    def get_due_reviews(
        self,
        *,
        on_date: str | None = None,
        book_id: str | None = None,
        book_ref: str | None = None,
        mode: str = "due",
    ) -> list[dict[str, Any]]:
        if mode not in {"due", "upcoming", "all"}:
            raise ValueError("review mode must be due, upcoming, or all")
        target = self._review_cutoff(on_date)
        clauses: list[str] = []
        params: list[Any] = []
        if book_id or book_ref:
            resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
            clauses.append("r.book_id = ?")
            params.append(resolved_book_id)
        if mode == "due":
            clauses.append("r.due_at <= ?")
            params.append(target)
        elif mode == "upcoming":
            clauses.append("r.due_at > ?")
            params.append(target)
        return self._review_rows(where=" AND ".join(clauses) or "1 = 1", params=tuple(params))

    def record_review_result(self, *, review_item_id: str, result: str) -> dict[str, Any]:
        review = self.store.fetchone("SELECT * FROM review_items WHERE id = ?", (review_item_id,))
        if not review:
            raise KeyError(review_item_id)
        current_interval = int(review["interval_days"] or 1)
        if result == "correct":
            next_interval = max(self.settings.review_interval_correct_days, current_interval * 2)
            ease = min(float(review["ease"] or 2.5) + 0.05, 3.0)
        elif result == "wrong":
            next_interval = self.settings.review_interval_new_days
            ease = max(float(review["ease"] or 2.5) - 0.2, 1.3)
        else:
            next_interval = self.settings.review_interval_new_days
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

    def generate_daily_log(
        self,
        *,
        book_id: str | None = None,
        on_date: str | None = None,
        output_dir: Path | None = None,
        book_ref: str | None = None,
    ) -> dict[str, Any]:
        resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
        target = on_date or date.today().isoformat()
        records = self.get_today_records(book_id=resolved_book_id, on_date=target)
        reviews = self.get_due_reviews(on_date=target, book_id=resolved_book_id)
        markdown = render_daily_log(date=target, records=records, reviews=reviews)
        default_output_dir = self.paths.exports_dir if self.paths else Path.cwd()
        path = write_daily_log(
            output_dir=output_dir or default_output_dir,
            date=target,
            markdown=markdown,
            filename_pattern=self.settings.markdown_filename_pattern,
        )
        return {"path": str(path), "markdown": markdown}

    def search_notes(
        self,
        *,
        query: str,
        book_id: str | None = None,
        book_ref: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        pattern = f"%{query}%"
        if book_id or book_ref:
            resolved_book_id = self._book_id_from_ref(book_id=book_id, book_ref=book_ref)
            return self.store.fetchall(
                """
                SELECT 'vocabulary' AS note_type, id, book_id, word AS title, source_sentence AS body, anchor_id, created_at
                FROM vocabulary_notes
                WHERE book_id = ? AND (word LIKE ? OR source_sentence LIKE ? OR user_meaning LIKE ? OR ai_context_meaning LIKE ?)
                UNION ALL
                SELECT 'sentence' AS note_type, id, book_id, sentence AS title, reason_saved AS body, anchor_id, created_at
                FROM sentence_notes
                WHERE book_id = ? AND (sentence LIKE ? OR reason_saved LIKE ? OR pattern_note LIKE ?)
                UNION ALL
                SELECT 'thought' AS note_type, id, book_id, thought_text AS title, related_quote AS body, anchor_id, created_at
                FROM thought_notes
                WHERE book_id = ? AND (thought_text LIKE ? OR related_quote LIKE ? OR tags LIKE ?)
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (
                    resolved_book_id,
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    resolved_book_id,
                    pattern,
                    pattern,
                    pattern,
                    resolved_book_id,
                    pattern,
                    pattern,
                    pattern,
                    limit,
                ),
            )
        return self.store.fetchall(
            """
            SELECT 'vocabulary' AS note_type, id, book_id, word AS title, source_sentence AS body, anchor_id, created_at
            FROM vocabulary_notes
            WHERE word LIKE ? OR source_sentence LIKE ? OR user_meaning LIKE ? OR ai_context_meaning LIKE ?
            UNION ALL
            SELECT 'sentence' AS note_type, id, book_id, sentence AS title, reason_saved AS body, anchor_id, created_at
            FROM sentence_notes
            WHERE sentence LIKE ? OR reason_saved LIKE ? OR pattern_note LIKE ?
            UNION ALL
            SELECT 'thought' AS note_type, id, book_id, thought_text AS title, related_quote AS body, anchor_id, created_at
            FROM thought_notes
            WHERE thought_text LIKE ? OR related_quote LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                limit,
            ),
        )

    def backup(self, *, output_dir: Path | None = None) -> dict[str, Any]:
        if not self.paths:
            raise ValueError("backup requires configured ReadMemory paths")
        return create_backup(paths=self.paths, output_dir=output_dir)

    def _count(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        row = self.store.fetchone(sql, params) or {"count": 0}
        return int(row["count"] or 0)

    def get_unanchored_items(self, *, limit: int = 20) -> dict[str, Any]:
        sessions = self.store.fetchall(
            "SELECT * FROM reading_sessions WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            ("unanchored", limit),
        )
        notes = self.store.fetchall(
            """
            SELECT 'vocabulary' AS item_type, id, book_id, word AS title, source_sentence AS body, created_at
            FROM vocabulary_notes
            WHERE anchor_id IS NULL
            UNION ALL
            SELECT 'sentence' AS item_type, id, book_id, sentence AS title, reason_saved AS body, created_at
            FROM sentence_notes
            WHERE anchor_id IS NULL
            UNION ALL
            SELECT 'thought' AS item_type, id, book_id, thought_text AS title, related_quote AS body, created_at
            FROM thought_notes
            WHERE anchor_id IS NULL
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        session_count = self._count("SELECT COUNT(*) AS count FROM reading_sessions WHERE status = ?", ("unanchored",))
        note_count = self._count(
            """
            SELECT (
                (SELECT COUNT(*) FROM vocabulary_notes WHERE anchor_id IS NULL) +
                (SELECT COUNT(*) FROM sentence_notes WHERE anchor_id IS NULL) +
                (SELECT COUNT(*) FROM thought_notes WHERE anchor_id IS NULL)
            ) AS count
            """
        )
        return {
            "session_count": session_count,
            "sessions": sessions,
            "note_count": note_count,
            "notes": notes,
        }

    def status(
        self,
        *,
        config_path: Path | None = None,
        data_dir: Path | None = None,
        db_path: Path | None = None,
        book_limit: int = 100,
        unanchored_limit: int = 20,
    ) -> dict[str, Any]:
        books = self.list_books(limit=book_limit)
        book_count = self._count("SELECT COUNT(*) AS count FROM books")
        unanchored = self.get_unanchored_items(limit=unanchored_limit)
        due_reviews = self.get_due_reviews(on_date=date.today().isoformat())
        return {
            "status": "ready",
            "config_path": None if config_path is None else str(config_path),
            "data_dir": None if data_dir is None else str(data_dir),
            "db_path": None if db_path is None else str(db_path),
            "book_count": book_count,
            "books": books,
            "unanchored_session_count": unanchored["session_count"],
            "unanchored_sessions": unanchored["sessions"],
            "unanchored_note_count": unanchored["note_count"],
            "unanchored_notes": unanchored["notes"],
            "due_review_count": len(due_reviews),
        }
