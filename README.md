# ReadMemory

ReadMemory is a local source-of-truth layer for English reading notes used through [Hermes agent](https://github.com/NousResearch/hermes-agent).

Hermes agent should use ReadMemory through the `readmemory` MCP server and the ReadMemory skill for Hermes agent. Hermes agent memory is not the factual store.

## What It Does

ReadMemory helps you keep reading in your existing EPUB reader while Hermes
agent records durable, searchable reading memory in a local SQLite database.

Core features:

- Import EPUB books and index their source text.
- List and search imported books without remembering exact `book_id` values.
- Resolve approximate book titles or authors into a usable `book_ref`.
- Resolve pasted quotes back to source anchors in the book.
- Record reading progress without relying on chat history.
- Save vocabulary, sentence patterns, and thoughts with source context.
- Save explicitly unanchored progress or notes when the user wants first-pass
  capture before exact source reconciliation.
- Search previous reading notes through Hermes agent.
- Generate due review queues for saved vocabulary, sentences, and thoughts.
- Export daily Markdown reading logs.
- Check ReadMemory/Hermes agent tool health with a status endpoint.

Typical workflow:

1. Import an EPUB into ReadMemory.
2. While reading, paste a quote, sentence, or note into Hermes agent.
3. Hermes agent uses ReadMemory tools to find the book, resolve the source
   location, and save progress or notes.
4. Later, ask Hermes agent what you saved, what to review, what needs anchor
   cleanup, or to generate a daily reading log.

## Linux Install

Requirements:

- Linux shell environment
- Python 3.11+
- Hermes agent with MCP server support

Install from the latest GitHub Release:

```bash
curl -fsSL https://raw.githubusercontent.com/ld066077/ReadMemory/main/scripts/update-linux.sh | bash
```

Then add ReadMemory to Hermes agent:

```bash
hermes mcp add readmemory --command readmemory-mcp
```

When prompted, enable all ReadMemory tools.

Check the Hermes agent connection:

```bash
hermes mcp list
hermes mcp test readmemory
```

Check ReadMemory itself:

```bash
readmemory status
readmemory books
```

Useful first commands:

```bash
readmemory import-book /path/to/book.epub
readmemory search-books "partial title or author"
readmemory resolve-book "partial title"
readmemory find-anchor --book-ref "partial title" --quote "pasted source quote"
readmemory log-progress --book-ref "partial title" --stop-quote "pasted source quote"
```
Save and maintain notes directly from the CLI:

```bash
readmemory add-word margin --book-ref "partial title" --source-sentence "source sentence" --date 2026-07-11
readmemory add-sentence "sentence to remember" --book-ref "partial title" --date 2026-07-11
readmemory add-thought "my reaction" --book-ref "partial title" --date 2026-07-11
readmemory notes "search term"
readmemory unanchored
readmemory reconcile thought ITEM_ID --quote "exact source quote"
readmemory edit thought ITEM_ID --set thought_text="revised thought"
readmemory delete thought ITEM_ID --yes
readmemory undo
readmemory backup
```

For rough capture when the exact source quote cannot be resolved yet:

```bash
readmemory log-progress --book-ref "partial title" --stop-quote "rough location" --note "chapter 2 near the end" --allow-unanchored
readmemory status
```

Default user-local paths:

- App releases: `~/.local/opt/readmemory/releases/`
- Current app: `~/.local/opt/readmemory/current`
- Commands: `~/.local/bin/readmemory`, `~/.local/bin/readmemory-mcp`, `~/.local/bin/readmemory-update`
- Config: `~/.config/readmemory/readmemory.toml`
- Data: `~/.local/share/readmemory/`
- Database: `~/.local/share/readmemory/readmemory.sqlite`
- Exports: `~/.local/share/readmemory/exports/`
- Hermes agent skill: `~/.hermes/skills/readmemory/SKILL.md`

EPUB paths are resolved on the machine running `readmemory-mcp`. A file uploaded
to a Hermes chat is not automatically available to the MCP server. Put the EPUB
in a local directory readable by the MCP host, or download it to that host
before calling `import_book`. ReadMemory does not automatically download remote EPUB URLs.


If `~/.local/bin` is not on `PATH`, add it before running ReadMemory.

## Verify

```bash
readmemory doctor
readmemory status
readmemory-mcp
```

The MCP command should either start the MCP server or print a ready JSON object if the optional MCP package is unavailable.

The installed Hermes agent skill path is:

```text
~/.hermes/skills/readmemory/SKILL.md
```

## Hermes Agent Tools

The MCP server exposes tools for full ReadMemory control:

- `status`, `list_books`, `search_books`, `resolve_book`
- `import_book`, `search_source`, `find_anchor`, `log_progress`
- `add_vocabulary`, `add_sentence`, `add_thought`
- `reconcile_item`, `edit_item`, `delete_item`, `undo_last`
- `create_backup`
- `get_due_reviews`, `record_review_result`, `generate_daily_log`
- `search_notes`, `get_unanchored_items`

Hermes agent should start with `status` or book discovery when book identity is
unclear, use `book_ref` for normal user-facing writes, and only use explicit
unanchored capture when the user wants to save a rough record that needs later
source reconciliation.

## Upgrade

Update to the latest GitHub Release:

```bash
readmemory-update
```

The installer creates a versioned release under `~/.local/opt/readmemory/releases/`, repoints `~/.local/opt/readmemory/current`, refreshes wrappers in `~/.local/bin`, and keeps existing config and data.

See `UPDATE.md` for the GitHub update flow and release checklist.

## Uninstall

Remove the application, command wrappers, and Hermes agent skill while keeping config and data:

```bash
readmemory-uninstall
```

Completely remove ReadMemory, including config and data:

```bash
readmemory-uninstall --purge
```

The purge path is intentionally guarded by marker files so the uninstall script refuses to remove unrelated directories.

## Backup

Create a portable backup archive:

```bash
readmemory backup
```

The archive is written to `~/.local/share/readmemory/backups/` by default and
contains a consistent SQLite snapshot, ReadMemory config, stored books,
exports, and a manifest. It does not include Hermes or GitHub credentials.

Use `--output-dir` to place it elsewhere. For manual backups, copy:

- `~/.local/share/readmemory/readmemory.sqlite`
- `~/.local/share/readmemory/books/`
- `~/.local/share/readmemory/exports/`
- `~/.config/readmemory/readmemory.toml`

## Development

Install from the development branch instead of the latest GitHub Release:

```bash
curl -fsSL https://raw.githubusercontent.com/ld066077/ReadMemory/main/scripts/update-linux.sh | bash -s -- --ref main
```

Install from a checked-out repository:

```bash
./scripts/install-linux.sh
```

Run tests from the repository:

```bash
python -m pytest
```
