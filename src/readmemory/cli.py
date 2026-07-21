from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json
import sys

from .config import load_settings
from .cli_commands import dispatch_extra
from .paths import resolve_paths
from .service import ReadMemoryService
from .storage import Store


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="readmemory", description="Local, verified memory for reading notes.")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--json", action="store_true", dest="json_output", help="print machine-readable JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init")
    subparsers.add_parser("doctor")

    status = subparsers.add_parser("status")
    status.add_argument("--limit", type=int, default=20)

    books = subparsers.add_parser("books")
    books.add_argument("--limit", type=int, default=100)

    search_books = subparsers.add_parser("search-books")
    search_books.add_argument("query")
    search_books.add_argument("--limit", type=int, default=10)

    resolve_book = subparsers.add_parser("resolve-book")
    resolve_book.add_argument("book_ref")
    resolve_book.add_argument("--limit", type=int, default=5)

    import_book = subparsers.add_parser("import-book")
    import_book.add_argument("path", type=Path)

    search_source = subparsers.add_parser("search-source")
    search_source.add_argument("--book-id", default=None)
    search_source.add_argument("--book-ref", default=None)
    search_source.add_argument("--quote", required=True)
    search_source.add_argument("--limit", type=int, default=10)

    find_anchor = subparsers.add_parser("find-anchor")
    find_anchor.add_argument("--book-id", default=None)
    find_anchor.add_argument("--book-ref", default=None)
    find_anchor.add_argument("--quote", required=True)
    find_anchor.add_argument("--limit", type=int, default=5)

    log_progress = subparsers.add_parser("log-progress")
    log_progress.add_argument("--book-id", default=None)
    log_progress.add_argument("--book-ref", default=None)
    log_progress.add_argument("--stop-quote", required=True)
    log_progress.add_argument("--start-quote", default=None)
    log_progress.add_argument("--date", dest="session_date", default=None)
    log_progress.add_argument("--note", dest="user_note", default=None)
    log_progress.add_argument("--allow-unanchored", action="store_true")

    daily_log = subparsers.add_parser("daily-log")
    daily_log.add_argument("--book-id", default=None)
    daily_log.add_argument("--book-ref", default=None)
    daily_log.add_argument("--date", default=None)
    daily_log.add_argument("--output-dir", type=Path, default=None)

    weekly_summary = subparsers.add_parser(
        "weekly-summary", help="generate a weekly reading summary"
    )
    weekly_summary.add_argument("--book-id", default=None)
    weekly_summary.add_argument("--book-ref", default=None)
    weekly_summary.add_argument("--date", default=None)
    weekly_summary.add_argument("--output-dir", type=Path, default=None)

    reviews = subparsers.add_parser("reviews")
    reviews.add_argument("--date", default=None)
    reviews.add_argument("--book-id", default=None)
    reviews.add_argument("--book-ref", default=None)
    reviews.add_argument("--mode", choices=["due", "upcoming", "all"], default="due")
    reviews.add_argument("--grouped", action="store_true", help="group vocabulary by word family")

    add_word = subparsers.add_parser("add-word", help="save vocabulary with optional source context")
    add_word.add_argument("words", nargs="+")
    add_word.add_argument("--book-id", default=None)
    add_word.add_argument("--book-ref", default=None)
    add_word.add_argument("--date", dest="note_date", default=None)
    add_word.add_argument("--source-sentence", default=None)
    add_word.add_argument("--meaning", default=None)
    add_word.add_argument("--verbose", action="store_true", help="return full records instead of compact summary")

    position = subparsers.add_parser("position", help="show latest reading position for a book")
    position.add_argument("--book-id", default=None)
    position.add_argument("--book-ref", default=None)

    vocab = subparsers.add_parser("vocabulary", help="list vocabulary notes for a book")
    vocab.add_argument("--book-id", default=None)
    vocab.add_argument("--book-ref", default=None)
    vocab.add_argument("--status", default=None)
    vocab.add_argument("--group-by-lemma", action="store_true")
    vocab.add_argument("--limit", type=int, default=100)

    sentences = subparsers.add_parser("sentences", help="list saved sentence notes for a book")
    sentences.add_argument("--book-id", default=None)
    sentences.add_argument("--book-ref", default=None)
    sentences.add_argument("--limit", type=int, default=100)

    lesson = subparsers.add_parser("lesson", help="get or save AI lesson for a word family")
    lesson.add_argument("--book-id", default=None)
    lesson.add_argument("--book-ref", default=None)
    lesson.add_argument("--group-key", required=True)
    lesson.add_argument("--save", default=None, help="lesson content to save")

    add_sentence = subparsers.add_parser("add-sentence", help="save a sentence note")
    add_sentence.add_argument("sentence")
    add_sentence.add_argument("--book-id", default=None)
    add_sentence.add_argument("--book-ref", default=None)
    add_sentence.add_argument("--date", dest="note_date", default=None)
    add_sentence.add_argument("--reason", default=None)
    add_sentence.add_argument("--pattern", default=None)

    add_thought = subparsers.add_parser("add-thought", help="save a thought note")
    add_thought.add_argument("thought")
    add_thought.add_argument("--book-id", default=None)
    add_thought.add_argument("--book-ref", default=None)
    add_thought.add_argument("--date", dest="note_date", default=None)
    add_thought.add_argument("--related-quote", default=None)
    add_thought.add_argument("--tag", action="append", dest="tags")

    notes = subparsers.add_parser("notes", help="search saved reading notes")
    notes.add_argument("query")
    notes.add_argument("--book-id", default=None)
    notes.add_argument("--book-ref", default=None)
    notes.add_argument("--limit", type=int, default=20)

    unanchored = subparsers.add_parser("unanchored", help="list items needing source reconciliation")
    unanchored.add_argument("--limit", type=int, default=20)

    reconcile = subparsers.add_parser("reconcile", help="attach an item to a verified source quote")
    reconcile.add_argument("entity_type", choices=["session", "vocabulary", "sentence", "thought"])
    reconcile.add_argument("item_id")
    reconcile.add_argument("--quote", required=True)

    edit = subparsers.add_parser("edit", help="edit a note or reading session")
    edit.add_argument("entity_type", choices=["session", "vocabulary", "sentence", "thought"])
    edit.add_argument("item_id")
    edit.add_argument("--set", action="append", required=True, dest="changes", metavar="FIELD=VALUE")

    delete = subparsers.add_parser("delete", help="delete an item; use undo to restore it")
    delete.add_argument("entity_type", choices=["session", "vocabulary", "sentence", "thought"])
    delete.add_argument("item_id")
    delete.add_argument("--yes", action="store_true", required=True)

    backup = subparsers.add_parser("backup", help="create a portable local backup archive")
    backup.add_argument("--output-dir", type=Path, default=None)

    subparsers.add_parser("undo", help="undo the latest create, edit, reconcile, or delete")

    review_result = subparsers.add_parser("review-result")
    review_result.add_argument("--review-item-id", required=True)
    review_result.add_argument("--result", required=True, choices=["correct", "wrong", "uncertain", "known", "fuzzy", "unknown", "want_lesson"])

    batch_review = subparsers.add_parser("batch-review", help="record multiple review results from JSON")
    batch_review.add_argument("--json-input", required=True, help="JSON list of {review_item_id, result}")
    return parser


def _json_print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _human_print(value: object) -> None:
    if isinstance(value, list):
        if not value:
            print("No results.")
            return
        for item in value:
            if isinstance(item, dict):
                title = item.get("title") or item.get("word") or item.get("sentence") or item.get("thought_text") or item.get("id")
                detail = item.get("author") or item.get("context") or item.get("book_title") or ""
                print(f"- {title}" + (f" — {detail}" if detail else ""))
            else:
                print(f"- {item}")
        return
    if isinstance(value, dict):
        if "book_count" in value:
            print(f"Books: {value['book_count']} | Due reviews: {value.get('due_review_count', 0)}")
            pending = value.get("unanchored_session_count", 0) + value.get("unanchored_note_count", 0)
            print(f"Needs reconciliation: {pending}")
            return
        if value.get("path"):
            print(f"Created: {value['path']}")
            return
        if value.get("status"):
            print(f"Status: {value['status']}")
        _json_print(value)
        return
    print(value)


def _print(value: object, *, as_json: bool) -> None:
    _json_print(value) if as_json else _human_print(value)


def _make_service(config_path: Path | None = None) -> ReadMemoryService:
    paths = resolve_paths()
    store = Store(paths.db_path)
    store.initialize()
    return ReadMemoryService(store, settings=load_settings(config_path or paths.config_path), paths=paths)


def _main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = resolve_paths()
    settings = load_settings(args.config or paths.config_path)

    if args.command == "init":
        paths.ensure()
        Store(paths.db_path).initialize()
        if not paths.config_path.exists():
            paths.config_dir.mkdir(parents=True, exist_ok=True)
            paths.config_path.write_text(
                'log_level = "INFO"\n'
                'default_language = "en"\n'
                'review_horizon_days = 7\n'
                'allow_unanchored_notes = true\n'
                'markdown_filename_pattern = "{date}-reading-log.md"\n'
                'review_interval_new_days = 1\n'
                'review_interval_correct_days = 3\n'
                'review_interval_weekly_days = 7\n',
                encoding="utf-8",
            )
        print(f"Initialized ReadMemory at {paths.data_dir}")
        return 0

    if args.command == "doctor":
        _json_print(
            {
                "config_path": str(paths.config_path),
                "data_dir": str(paths.data_dir),
                "db_path": str(paths.db_path),
                "books_dir": str(paths.books_dir),
                "exports_dir": str(paths.exports_dir),
                "logs_dir": str(paths.logs_dir),
                "log_level": settings.log_level,
                "default_language": settings.default_language,
            }
        )
        return 0

    if args.command == "status":
        store = Store(paths.db_path)
        store.initialize()
        result = ReadMemoryService(store, settings=settings, paths=paths).status(
            config_path=args.config or paths.config_path,
            data_dir=paths.data_dir,
            db_path=paths.db_path,
            book_limit=args.limit,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "books":
        result = _make_service(args.config).list_books(limit=args.limit)
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "search-books":
        result = _make_service(args.config).search_books(query=args.query, limit=args.limit)
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "resolve-book":
        result = _make_service(args.config).resolve_book(book_ref=args.book_ref, limit=args.limit)
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "import-book":
        result = _make_service(args.config).import_book(args.path)
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "search-source":
        result = _make_service(args.config).search_source(
            book_id=args.book_id,
            book_ref=args.book_ref,
            quote=args.quote,
            limit=args.limit,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "find-anchor":
        result = _make_service(args.config).find_anchor(
            book_id=args.book_id,
            book_ref=args.book_ref,
            quote=args.quote,
            limit=args.limit,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "log-progress":
        result = _make_service(args.config).log_progress(
            book_id=args.book_id,
            book_ref=args.book_ref,
            stop_quote=args.stop_quote,
            start_quote=args.start_quote,
            session_date=args.session_date,
            user_note=args.user_note,
            allow_unanchored=args.allow_unanchored,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "daily-log":
        result = _make_service(args.config).generate_daily_log(
            book_id=args.book_id,
            book_ref=args.book_ref,
            on_date=args.date,
            output_dir=args.output_dir,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "weekly-summary":
        result = _make_service(args.config).generate_weekly_summary(
            book_id=args.book_id,
            book_ref=args.book_ref,
            on_date=args.date,
            output_dir=args.output_dir,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "reviews":
        result = _make_service(args.config).get_due_reviews(
            on_date=args.date,
            book_id=args.book_id,
            book_ref=args.book_ref,
            mode=args.mode,
            group_by_family=args.grouped,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "lesson":
        service = _make_service(args.config)
        if args.save is not None:
            result = service.save_lesson(
                book_id=args.book_id,
                book_ref=args.book_ref,
                group_key=args.group_key,
                lesson_content=args.save,
            )
        else:
            result = service.get_lesson(
                book_id=args.book_id,
                book_ref=args.book_ref,
                group_key=args.group_key,
            )
        _print(result, as_json=args.json_output)
        return 0

    handled, result = dispatch_extra(args, _make_service(args.config))
    if handled:
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "review-result":
        result = _make_service(args.config).record_review_result(
            review_item_id=args.review_item_id,
            result=args.result,
        )
        _print(result, as_json=args.json_output)
        return 0

    if args.command == "batch-review":
        import json as _json
        results = _json.loads(args.json_input)
        result = _make_service(args.config).batch_record_review_results(results=results)
        _print(result, as_json=args.json_output)
        return 0

    return 1


def main(argv: list[str] | None = None) -> int:
    try:
        return _main(argv)
    except (ValueError, KeyError, OSError) as exc:
        message = exc.args[0] if isinstance(exc, KeyError) and exc.args else str(exc)
        print(f"Error: {message}", file=sys.stderr)
        if "book_ref" in str(exc) or "book_id" in str(exc):
            print("Try: readmemory books or readmemory search-books QUERY", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
