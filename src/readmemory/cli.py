from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .config import load_settings
from .paths import resolve_paths
from .service import ReadMemoryService
from .storage import Store


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="readmemory")
    parser.add_argument("--config", type=Path, default=None)
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

    reviews = subparsers.add_parser("reviews")
    reviews.add_argument("--date", default=None)
    reviews.add_argument("--book-id", default=None)
    reviews.add_argument("--book-ref", default=None)

    review_result = subparsers.add_parser("review-result")
    review_result.add_argument("--review-item-id", required=True)
    review_result.add_argument("--result", required=True, choices=["correct", "wrong", "uncertain"])
    return parser


def _json_print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _make_service() -> ReadMemoryService:
    paths = resolve_paths()
    store = Store(paths.db_path)
    store.initialize()
    return ReadMemoryService(store)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = resolve_paths()
    settings = load_settings(args.config or paths.config_path)

    if args.command == "init":
        paths.ensure()
        Store(paths.db_path).initialize()
        if not paths.config_path.exists():
            paths.config_dir.mkdir(parents=True, exist_ok=True)
            paths.config_path.write_text(
                'log_level = "INFO"\ndefault_language = "en"\n',
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
        result = ReadMemoryService(store).status(
            config_path=args.config or paths.config_path,
            data_dir=paths.data_dir,
            db_path=paths.db_path,
            book_limit=args.limit,
        )
        _json_print(result)
        return 0

    if args.command == "books":
        result = _make_service().list_books(limit=args.limit)
        _json_print(result)
        return 0

    if args.command == "search-books":
        result = _make_service().search_books(query=args.query, limit=args.limit)
        _json_print(result)
        return 0

    if args.command == "resolve-book":
        result = _make_service().resolve_book(book_ref=args.book_ref, limit=args.limit)
        _json_print(result)
        return 0

    if args.command == "import-book":
        result = _make_service().import_book(args.path)
        _json_print(result)
        return 0

    if args.command == "search-source":
        result = _make_service().search_source(
            book_id=args.book_id,
            book_ref=args.book_ref,
            quote=args.quote,
            limit=args.limit,
        )
        _json_print(result)
        return 0

    if args.command == "find-anchor":
        result = _make_service().find_anchor(
            book_id=args.book_id,
            book_ref=args.book_ref,
            quote=args.quote,
            limit=args.limit,
        )
        _json_print(result)
        return 0

    if args.command == "log-progress":
        result = _make_service().log_progress(
            book_id=args.book_id,
            book_ref=args.book_ref,
            stop_quote=args.stop_quote,
            start_quote=args.start_quote,
            session_date=args.session_date,
            user_note=args.user_note,
            allow_unanchored=args.allow_unanchored,
        )
        _json_print(result)
        return 0

    if args.command == "daily-log":
        result = _make_service().generate_daily_log(
            book_id=args.book_id,
            book_ref=args.book_ref,
            on_date=args.date,
            output_dir=args.output_dir,
        )
        _json_print(result)
        return 0

    if args.command == "reviews":
        result = _make_service().get_due_reviews(
            on_date=args.date,
            book_id=args.book_id,
            book_ref=args.book_ref,
        )
        _json_print(result)
        return 0

    if args.command == "review-result":
        result = _make_service().record_review_result(
            review_item_id=args.review_item_id,
            result=args.result,
        )
        _json_print(result)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
