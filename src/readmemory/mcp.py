from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .paths import resolve_paths
from .service import ReadMemoryService
from .storage import Store


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="readmemory-mcp")
    parser.add_argument("--config", type=Path, default=None)
    return parser


def _make_service() -> tuple[ReadMemoryService, Path]:
    paths = resolve_paths()
    paths.ensure()
    store = Store(paths.db_path)
    store.initialize()
    return ReadMemoryService(store), paths.data_dir


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    service, data_dir = _make_service()

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(json.dumps({"status": "ready", "data_dir": str(data_dir)}, ensure_ascii=False))
        return 0

    app = FastMCP("readmemory")

    @app.tool()
    def import_book(path: str) -> dict:
        return service.import_book(Path(path))

    @app.tool()
    def find_anchor(book_id: str, quote: str, limit: int = 5) -> dict:
        return service.find_anchor(book_id=book_id, quote=quote, limit=limit)

    @app.tool()
    def log_progress(
        book_id: str,
        stop_quote: str,
        start_quote: str | None = None,
        session_date: str | None = None,
        user_note: str | None = None,
    ) -> dict:
        return service.log_progress(
            book_id=book_id,
            stop_quote=stop_quote,
            start_quote=start_quote,
            session_date=session_date,
            user_note=user_note,
        )

    @app.tool()
    def add_vocabulary(
        book_id: str,
        words: list[str],
        source_sentence: str | None = None,
        user_meaning: str | None = None,
        ai_context_meaning: str | None = None,
        anchor_id: str | None = None,
    ) -> list[dict]:
        return service.add_vocabulary(
            book_id=book_id,
            words=words,
            source_sentence=source_sentence,
            user_meaning=user_meaning,
            ai_context_meaning=ai_context_meaning,
            anchor_id=anchor_id,
        )

    @app.tool()
    def add_sentence(
        book_id: str,
        sentence: str,
        reason_saved: str | None = None,
        pattern_note: str | None = None,
        imitation_examples: list[str] | None = None,
        anchor_id: str | None = None,
    ) -> dict:
        return service.add_sentence(
            book_id=book_id,
            sentence=sentence,
            reason_saved=reason_saved,
            pattern_note=pattern_note,
            imitation_examples=imitation_examples,
            anchor_id=anchor_id,
        )

    @app.tool()
    def add_thought(
        book_id: str,
        thought_text: str,
        anchor_id: str | None = None,
        related_quote: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        return service.add_thought(
            book_id=book_id,
            thought_text=thought_text,
            anchor_id=anchor_id,
            related_quote=related_quote,
            tags=tags,
        )

    @app.tool()
    def get_due_reviews(on_date: str | None = None) -> list[dict]:
        return service.get_due_reviews(on_date=on_date)

    @app.tool()
    def record_review_result(review_item_id: str, result: str) -> dict:
        return service.record_review_result(review_item_id=review_item_id, result=result)

    @app.tool()
    def generate_daily_log(book_id: str, on_date: str | None = None) -> dict:
        return service.generate_daily_log(book_id=book_id, on_date=on_date)

    @app.tool()
    def search_notes(query: str, book_id: str | None = None, limit: int = 20) -> list[dict]:
        if book_id:
            return service.store.fetchall(
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
                    book_id,
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    book_id,
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    book_id,
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    limit,
                ),
            )
        return service.store.fetchall(
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
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                limit,
            ),
        )

    app.run()
    return 0
