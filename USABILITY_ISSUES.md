# v 0.2.0

## Summary

Card-style vocabulary review replaces the cloze-deletion quiz flow. The agent
generates pronunciation, Chinese meaning, sentence translation, and chunked
reading per word, then writes them back so reviews render as complete cards.

## Implemented

- `get_due_reviews` now returns a canonical `review_card` payload per item.
  Vocabulary cards: `word`, `lemma`, `pronunciation`, `meaning_en`,
  `meaning_zh`, `source_sentence`, `sentence_translation_zh`,
  `chunked_sentence`, `needs_enrichment`.
- Cloze-deletion `prompt` generation removed (legacy quiz flow deleted).
- Schema v6: new `vocabulary_notes` columns `meaning_zh`, `pronunciation`,
  `source_sentence_translation`, `source_sentence_chunked` (with migration).
- `add_vocabulary` accepts per-word enrichment metadata (`pronunciation`,
  `sentence_translation`, `sentence_chunked`) via `meanings=[...]`.
- New `enrich_vocabulary` batch tool (service + MCP + CLI
  `enrich-vocabulary`) for writing agent-generated enrichment back in one call.
- `edit_item` on vocabulary supports the four new enrichment fields.
- Auto source-sentence lookup falls back to a book-wide sentence search when
  the anchor range is too narrow.
- Chunking heuristic: ` / ` pause marks from existing marks, commas, or a
  midpoint split for long sentences.

# v 0.1.6

## Summary

Remove all rule-based lemmatization; the agent is now the sole authority on word grouping.

## Implemented

- `normalize_word` only lowercases and strips punctuation; no suffix rules.
- `group_key` comes only from agent-provided `lemma`; `NULL` when absent.
- Duplicate detection only when `lemma` is provided.
- `edit_item` supports editing `lemma` on vocabulary and syncs `group_key`.
- `get_vocabulary` ungrouped words fall back to the word itself.
- Version bump to 0.1.6.

# v 0.1.5

## Summary

ReadMemory v0.1.5 adds grounded weekly reading statistics and pace guidance.

## Implemented

- Added Monday-to-Sunday summaries for reading days, sessions, and words read.
- Added vocabulary, sentence, and thought counts by week and by book.
- Added per-day activity breakdowns and book filtering.
- Added a next-session word target based on average words per active reading day.
- Added CLI `weekly-summary` and MCP `get_weekly_summary` / `generate_weekly_summary`.
- Added idempotent Markdown weekly summary export.

# v 0.1.5-dev (humanization improvements)

## Summary

Ongoing improvements for more human-friendly agent/CLI interaction.

## Implemented

- `add_vocabulary` returns a compact summary by default (saved_count, words list, anchor_id); `--verbose` / `compact=False` returns full records.
- Per-word metadata support in `add_vocabulary`: pass `meanings=[{word, lemma, meaning, meaning_zh, context}]` to set lemma, English meaning, Chinese meaning, and context per word.
- Word-family grouping: `lemma` (agent-provided) or `normalized_form` (rule-based fallback) is used as `group_key` for duplicate detection and review grouping. Same word family (e.g. "annulled" / "annul") is detected as duplicate.
- New `get_reading_position(book_ref)`: returns latest chapter/paragraph/quote for "where did I stop?".
- New `get_vocabulary(book_ref, status, group_by_lemma)`: list vocabulary, optionally grouped by word family.
- New `get_sentences(book_ref)`: list saved sentence notes.
- `get_due_reviews` now includes a conversational `prompt` field (e.g. "In 'Animal Farm', what does 'knacker' mean in: ...?").
- `search_source` filters CSS/meta noise and prefers sentence-level matches over chapter dumps.
- Schema v4: added `normalized_form` and `group_key` to `vocabulary_notes` with migration and indexes.

# v 0.1.4

## Summary

ReadMemory v0.1.4 improves date consistency, import safety, and data portability.

## Implemented

- Added explicit `note_date` support to vocabulary, sentence, and thought notes.
- Daily logs group notes by note date so dated sessions and notes export together.
- Added schema v3 migration with date backfill for existing notes.
- EPUB database writes run in one transaction and roll back fully on failure.
- Added `readmemory backup` and MCP `create_backup` for database, config, stored books, exports, and manifest.
- Backups exclude Hermes credentials, GitHub credentials, and unrelated files.
- Verified migration on a real v0.1.3 database copy without record-count changes.

# v 0.1.3

## Summary

ReadMemory v0.1.3 focuses on trustworthy capture, correction workflows, and friendlier direct CLI use.

## Implemented

- Anchor lookup is read-only; anchors are persisted only during an explicit save or reconciliation workflow.
- Notes without a verified source stay unanchored instead of inheriting the most recently created anchor.
- Review queues distinguish due, upcoming, and all items and include original text, context, and book title.
- Added reconcile, edit, delete, and undo operations to the service, CLI, and MCP tool surface.
- Added direct CLI commands for vocabulary, sentences, thoughts, note search, and unanchored cleanup.
- CLI output is human-readable by default with optional `--json` and friendly expected-error messages.
- Review intervals and Markdown export paths/file names use configured values.
- Documentation explains that EPUB files must be accessible on the machine running the Hermes MCP server.

# v 0.1.1 issues

This document tracks usability issues found in ReadMemory v 0.1.1. Add later
version sections above this section as new issues are found.

## Summary

ReadMemory v 0.1.1 can install, expose MCP tools, connect to Hermes agent, and
store reading records. The main usability gap was discovery: users and agents
did not have enough tools to inspect the local library, find imported books, or
recover gracefully from incomplete book/title/anchor information.

These issues are addressed in the current working tree for the next release by
adding book discovery, fuzzy book resolution, explicit unanchored capture,
ReadMemory status checks, and a fuller Hermes agent skill workflow.

## Issues

### 1. Imported Books Are Not Discoverable

Status: addressed in next release
Priority: high

Problem:
ReadMemory did not provide a user-facing way to list imported books. Users could
not easily confirm whether a book was already imported, what its exact title was,
or which `book_id` should be used.

Implemented fix:
- Added service, CLI, and MCP support for listing books.
- Added `readmemory books` and MCP `list_books`.
- `status` also includes current library count and recent books.

### 2. Book Search Is Missing

Status: addressed in next release
Priority: high

Problem:
There was no read-only search interface for the book library. Users could ask to
check the database or find a book by title/author, but the tool surface could not
answer that directly.

Implemented fix:
- Added fuzzy `search_books(query)` service and MCP tool.
- Added `readmemory search-books QUERY` CLI command.
- Hermes agent skill now instructs the agent to search the library before asking
  for an EPUB path.

### 3. Exact Book Titles Are Too Brittle

Status: addressed in next release
Priority: high

Problem:
The workflow relied too heavily on exact title or `book_id` knowledge. Small
title differences, spelling mistakes, or singular/plural differences could block
progress.

Implemented fix:
- Added `resolve_book(book_ref)` service, CLI, and MCP tool.
- Existing source, anchor, progress, note, review, and daily-log workflows accept
  `book_ref` in addition to `book_id`.
- Ambiguous matches return candidate books instead of silently selecting a weak
  match.

### 4. Anchor Resolution Is Too Strict For First-Pass Capture

Status: addressed in next release
Priority: medium

Problem:
Progress logging required a resolved source anchor. In real use, a user may only
remember a short phrase, chapter heading, or rough location.

Implemented fix:
- `log_progress` now supports explicit `allow_unanchored` capture.
- Unanchored progress is stored with status `unanchored` and no end anchor.
- `status` and `get_unanchored_items` expose records that need later source
  reconciliation.
- Notes can be saved to a resolved book even when no anchor is available.

### 5. Tool Availability Is Not Obvious Across Clients

Status: addressed in next release
Priority: medium

Problem:
ReadMemory tools could be unavailable in a client until Hermes agent MCP setup,
restart, or tool selection was completed. The failure mode was not always obvious
to the user.

Implemented fix:
- Added `readmemory status` and MCP `status`.
- `readmemory-mcp` prints ready status JSON if the optional MCP package is not
  importable.
- README and Hermes skill now document `hermes mcp list`, `hermes mcp test
  readmemory`, `readmemory status`, and tool reload expectations.

## Current Priority Order

All v 0.1.1 usability items are addressed in the current working tree. Before
release, verify:

1. Full test suite passes from the repository with `python -m pytest`.
2. Hermes agent exposes all ReadMemory MCP tools after reinstall/update.
3. `readmemory status`, `readmemory books`, `readmemory search-books`, and
   `readmemory log-progress --allow-unanchored` work on a real user database.

## Future Versions

Add later sections in this format:

```text
# v x.y.z issues

## Summary

## Issues

### 1. Issue title

Status: open
Priority: high | medium | low

Problem:

Impact:

Suggested fix:
```

Hermes网关不能发送epub，需要把文件放在它本地目录，或者给它可用下载连接,这点要在下个版本说明清楚
