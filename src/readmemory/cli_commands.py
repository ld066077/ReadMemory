from __future__ import annotations

from typing import Any


def dispatch_extra(args: Any, service: Any) -> tuple[bool, object | None]:
    if args.command == "add-word":
        return True, service.add_vocabulary(
            book_id=args.book_id,
            book_ref=args.book_ref,
            words=args.words,
            source_sentence=args.source_sentence,
            user_meaning=args.meaning,
        )
    if args.command == "add-sentence":
        return True, service.add_sentence(
            book_id=args.book_id,
            book_ref=args.book_ref,
            sentence=args.sentence,
            reason_saved=args.reason,
            pattern_note=args.pattern,
        )
    if args.command == "add-thought":
        return True, service.add_thought(
            book_id=args.book_id,
            book_ref=args.book_ref,
            thought_text=args.thought,
            related_quote=args.related_quote,
            tags=args.tags,
        )
    if args.command == "notes":
        return True, service.search_notes(
            query=args.query,
            book_id=args.book_id,
            book_ref=args.book_ref,
            limit=args.limit,
        )
    if args.command == "unanchored":
        return True, service.get_unanchored_items(limit=args.limit)
    if args.command == "reconcile":
        return True, service.reconcile_item(
            entity_type=args.entity_type,
            item_id=args.item_id,
            quote=args.quote,
        )
    if args.command == "edit":
        changes: dict[str, str] = {}
        for pair in args.changes:
            if "=" not in pair:
                raise ValueError("--set must use FIELD=VALUE")
            key, value = pair.split("=", 1)
            changes[key] = value
        return True, service.edit_item(
            entity_type=args.entity_type,
            item_id=args.item_id,
            changes=changes,
        )
    if args.command == "delete":
        return True, service.delete_item(
            entity_type=args.entity_type,
            item_id=args.item_id,
        )
    if args.command == "undo":
        return True, service.undo_last()
    return False, None
