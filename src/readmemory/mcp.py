from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .paths import resolve_paths
from .config import load_settings
from .service import ReadMemoryService
from .storage import Store


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="readmemory-mcp")
    parser.add_argument("--config", type=Path, default=None)
    return parser


def _make_service(config_path: Path | None = None) -> tuple[ReadMemoryService, object]:
    paths = resolve_paths()
    paths.ensure()
    store = Store(paths.db_path)
    store.initialize()
    return ReadMemoryService(store, settings=load_settings(config_path or paths.config_path), paths=paths), paths


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service, paths = _make_service(args.config)
    config_path = args.config or paths.config_path

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            json.dumps(
                service.status(
                    config_path=config_path,
                    data_dir=paths.data_dir,
                    db_path=paths.db_path,
                    book_limit=20,
                ),
                ensure_ascii=False,
            )
        )
        return 0

    app = FastMCP("readmemory")

    @app.tool()
    def status(book_limit: int = 20, unanchored_limit: int = 20) -> dict:
        return service.status(
            config_path=config_path,
            data_dir=paths.data_dir,
            db_path=paths.db_path,
            book_limit=book_limit,
            unanchored_limit=unanchored_limit,
        )

    @app.tool()
    def list_books(limit: int = 100) -> list[dict]:
        return service.list_books(limit=limit)

    @app.tool()
    def search_books(query: str, limit: int = 10) -> list[dict]:
        return service.search_books(query=query, limit=limit)

    @app.tool()
    def resolve_book(book_ref: str, limit: int = 5) -> dict:
        return service.resolve_book(book_ref=book_ref, limit=limit)

    @app.tool()
    def import_book(path: str) -> dict:
        return service.import_book(Path(path))

    @app.tool()
    def search_source(
        quote: str,
        book_id: str | None = None,
        book_ref: str | None = None,
        limit: int = 10,
    ) -> dict:
        return service.search_source(book_id=book_id, book_ref=book_ref, quote=quote, limit=limit)

    @app.tool()
    def find_anchor(
        quote: str,
        book_id: str | None = None,
        book_ref: str | None = None,
        limit: int = 5,
    ) -> dict:
        return service.find_anchor(book_id=book_id, book_ref=book_ref, quote=quote, limit=limit)

    @app.tool()
    def log_progress(
        stop_quote: str,
        book_id: str | None = None,
        book_ref: str | None = None,
        start_quote: str | None = None,
        session_date: str | None = None,
        user_note: str | None = None,
        allow_unanchored: bool = False,
    ) -> dict:
        return service.log_progress(
            book_id=book_id,
            book_ref=book_ref,
            stop_quote=stop_quote,
            start_quote=start_quote,
            session_date=session_date,
            user_note=user_note,
            allow_unanchored=allow_unanchored,
        )

    @app.tool()
    def add_vocabulary(
        words: list[str],
        book_id: str | None = None,
        book_ref: str | None = None,
        source_sentence: str | None = None,
        user_meaning: str | None = None,
        ai_context_meaning: str | None = None,
        meanings: list[dict] | None = None,
        anchor_id: str | None = None,
        note_date: str | None = None,
        compact: bool = True,
    ) -> dict:
        """Save vocabulary words. Returns a compact summary by default.

        For per-word metadata (lemma, meaning, meaning_zh, context,
        pronunciation, sentence_translation, sentence_chunked), pass
        meanings as a list of dicts: [{"word": "...", "lemma": "...",
        "meaning": "...", "meaning_zh": "...", "context": "...",
        "pronunciation": "...", "sentence_translation": "...",
        "sentence_chunked": "..."}].
        Lemma is used to group word families (e.g. "annulled" -> "annul").
        """
        return service.add_vocabulary(
            book_id=book_id,
            book_ref=book_ref,
            words=words,
            source_sentence=source_sentence,
            user_meaning=user_meaning,
            ai_context_meaning=ai_context_meaning,
            meanings=meanings,
            anchor_id=anchor_id,
            note_date=note_date,
            compact=compact,
        )

    @app.tool()
    def get_reading_position(
        book_id: str | None = None,
        book_ref: str | None = None,
    ) -> dict:
        """Return the latest reading position (chapter/paragraph/quote)."""
        return service.get_reading_position(book_id=book_id, book_ref=book_ref)

    @app.tool()
    def get_vocabulary(
        book_id: str | None = None,
        book_ref: str | None = None,
        status: str | None = None,
        group_by_lemma: bool = False,
        limit: int = 100,
    ) -> list[dict]:
        """List vocabulary notes for a book, optionally grouped by lemma."""
        return service.get_vocabulary(
            book_id=book_id,
            book_ref=book_ref,
            status=status,
            group_by_lemma=group_by_lemma,
            limit=limit,
        )

    @app.tool()
    def get_sentences(
        book_id: str | None = None,
        book_ref: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """List saved sentence notes for a book."""
        return service.get_sentences(book_id=book_id, book_ref=book_ref, limit=limit)

    @app.tool()
    def add_sentence(
        sentence: str,
        book_id: str | None = None,
        book_ref: str | None = None,
        reason_saved: str | None = None,
        pattern_note: str | None = None,
        imitation_examples: list[str] | None = None,
        anchor_id: str | None = None,
        note_date: str | None = None,
    ) -> dict:
        return service.add_sentence(
            book_id=book_id,
            book_ref=book_ref,
            sentence=sentence,
            reason_saved=reason_saved,
            pattern_note=pattern_note,
            imitation_examples=imitation_examples,
            anchor_id=anchor_id,
            note_date=note_date,
        )

    @app.tool()
    def add_thought(
        thought_text: str,
        book_id: str | None = None,
        note_date: str | None = None,
        book_ref: str | None = None,
        anchor_id: str | None = None,
        related_quote: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        return service.add_thought(
            book_id=book_id,
            book_ref=book_ref,
            thought_text=thought_text,
            anchor_id=anchor_id,
            note_date=note_date,
            related_quote=related_quote,
            tags=tags,
        )

    @app.tool()
    def get_due_reviews(
        on_date: str | None = None,
        book_id: str | None = None,
        book_ref: str | None = None,
        mode: str = "due",
        group_by_family: bool = False,
    ) -> list[dict] | dict:
        return service.get_due_reviews(
            on_date=on_date, book_id=book_id, book_ref=book_ref,
            mode=mode, group_by_family=group_by_family,
        )

    @app.tool()
    def get_lesson(
        group_key: str,
        book_id: str | None = None,
        book_ref: str | None = None,
    ) -> dict:
        """Get lesson content and context for a word family."""
        return service.get_lesson(book_id=book_id, book_ref=book_ref, group_key=group_key)

    @app.tool()
    def save_lesson(
        group_key: str,
        lesson_content: str,
        book_id: str | None = None,
        book_ref: str | None = None,
    ) -> dict:
        """Save AI-generated lesson content for a word family."""
        return service.save_lesson(
            book_id=book_id, book_ref=book_ref,
            group_key=group_key, lesson_content=lesson_content,
        )

    @app.tool()
    def enrich_vocabulary(enrichments: list[dict]) -> dict:
        """Batch-write agent-generated enrichment fields (pronunciation, meaning_zh,
        source_sentence_translation, source_sentence_chunked) back to vocabulary notes.
        Each entry: {item_id, ...fields}."""
        return service.enrich_vocabulary(enrichments=enrichments)

    @app.tool()
    def record_review_result(review_item_id: str, result: str) -> dict:
        return service.record_review_result(review_item_id=review_item_id, result=result)

    @app.tool()
    def batch_record_review_results(results: list[dict]) -> dict:
        """Record multiple review results at once. Each entry: {review_item_id, result}."""
        return service.batch_record_review_results(results=results)

    @app.tool()
    def generate_daily_log(
        book_id: str | None = None,
        book_ref: str | None = None,
        on_date: str | None = None,
    ) -> dict:
        return service.generate_daily_log(book_id=book_id, book_ref=book_ref, on_date=on_date)

    @app.tool()
    def get_weekly_summary(
        on_date: str | None = None,
        book_id: str | None = None,
        book_ref: str | None = None,
    ) -> dict:
        """Return grounded reading and note statistics for the selected week."""
        return service.get_weekly_summary(
            on_date=on_date, book_id=book_id, book_ref=book_ref
        )

    @app.tool()
    def generate_weekly_summary(
        on_date: str | None = None,
        book_id: str | None = None,
        book_ref: str | None = None,
    ) -> dict:
        """Write a Markdown weekly reading summary and return its statistics."""
        return service.generate_weekly_summary(
            on_date=on_date, book_id=book_id, book_ref=book_ref
        )

    @app.tool()
    def search_notes(
        query: str,
        book_id: str | None = None,
        book_ref: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        return service.search_notes(query=query, book_id=book_id, book_ref=book_ref, limit=limit)

    @app.tool()
    def get_unanchored_items(limit: int = 20) -> dict:
        return service.get_unanchored_items(limit=limit)

    @app.tool()
    def reconcile_item(entity_type: str, item_id: str, quote: str) -> dict:
        """Attach an unanchored session or note to a verified source quote."""
        return service.reconcile_item(entity_type=entity_type, item_id=item_id, quote=quote)

    @app.tool()
    def edit_item(entity_type: str, item_id: str, changes: dict) -> dict:
        """Edit allowed user-facing fields on a reading session or note."""
        return service.edit_item(entity_type=entity_type, item_id=item_id, changes=changes)

    @app.tool()
    def delete_item(entity_type: str, item_id: str) -> dict:
        """Delete a session or note; the latest deletion can be undone."""
        return service.delete_item(entity_type=entity_type, item_id=item_id)

    @app.tool()
    def undo_last() -> dict:
        """Undo the latest supported create, edit, reconcile, or delete action."""
        return service.undo_last()

    @app.tool()
    def create_backup(output_dir: str | None = None) -> dict:
        """Create a portable backup of the database, config, books, and exports."""
        return service.backup(output_dir=None if output_dir is None else Path(output_dir))

    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
