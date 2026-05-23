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
    import_book = subparsers.add_parser("import-book")
    import_book.add_argument("path", type=Path)
    search_source = subparsers.add_parser("search-source")
    search_source.add_argument("--book-id", required=True)
    search_source.add_argument("--quote", required=True)
    search_source.add_argument("--limit", type=int, default=10)
    find_anchor = subparsers.add_parser("find-anchor")
    find_anchor.add_argument("--book-id", required=True)
    find_anchor.add_argument("--quote", required=True)
    find_anchor.add_argument("--limit", type=int, default=5)
    daily_log = subparsers.add_parser("daily-log")
    daily_log.add_argument("--book-id", required=True)
    daily_log.add_argument("--date", default=None)
    daily_log.add_argument("--output-dir", type=Path, default=None)
    reviews = subparsers.add_parser("reviews")
    reviews.add_argument("--date", default=None)
    review_result = subparsers.add_parser("review-result")
    review_result.add_argument("--review-item-id", required=True)
    review_result.add_argument("--result", required=True, choices=["correct", "wrong", "uncertain"])
    return parser


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
                "log_level = \"INFO\"\ndefault_language = \"en\"\n",
                encoding="utf-8",
            )
        print(f"Initialized ReadMemory at {paths.data_dir}")
        return 0

    if args.command == "doctor":
        print(json.dumps({
            "config_path": str(paths.config_path),
            "data_dir": str(paths.data_dir),
            "db_path": str(paths.db_path),
            "books_dir": str(paths.books_dir),
            "exports_dir": str(paths.exports_dir),
            "logs_dir": str(paths.logs_dir),
            "log_level": settings.log_level,
            "default_language": settings.default_language,
        }, ensure_ascii=False, indent=2))
        return 0

    if args.command == "import-book":
        store = Store(paths.db_path)
        store.initialize()
        result = ReadMemoryService(store).import_book(args.path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "search-source":
        store = Store(paths.db_path)
        store.initialize()
        result = ReadMemoryService(store).search_source(
            book_id=args.book_id,
            quote=args.quote,
            limit=args.limit,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "find-anchor":
        store = Store(paths.db_path)
        store.initialize()
        result = ReadMemoryService(store).find_anchor(
            book_id=args.book_id,
            quote=args.quote,
            limit=args.limit,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "daily-log":
        store = Store(paths.db_path)
        store.initialize()
        result = ReadMemoryService(store).generate_daily_log(
            book_id=args.book_id,
            on_date=args.date,
            output_dir=args.output_dir,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "reviews":
        store = Store(paths.db_path)
        store.initialize()
        result = ReadMemoryService(store).get_due_reviews(on_date=args.date)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "review-result":
        store = Store(paths.db_path)
        store.initialize()
        result = ReadMemoryService(store).record_review_result(
            review_item_id=args.review_item_id,
            result=args.result,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    return 1
