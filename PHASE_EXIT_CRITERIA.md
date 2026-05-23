# ReadMemory Phase Exit Criteria

This document defines the minimum acceptable finish line for each phase in `DEVELOPMENT_PROGRESS.md`.

Test fixture:

- `tests/On the Heights of Despair (E. M. Cioran).epub`

If a phase cannot be verified against this file, the phase is not closed.

## General Rules

- Keep the scope small.
- Verify against the single EPUB fixture first.
- Prefer one working path over broad feature coverage.
- Do not count code skeletons as completion.
- Do not count prompt behavior as completion unless the tool layer is also working.
- Do not use Hermes memory as a substitute for the ReadMemory database.

## Phase 0: Project Foundation

Exit only when:

- The project can be installed on Linux.
- `readmemory` starts.
- `readmemory-mcp` starts.
- Config is loaded from a real file.
- Data directories are created automatically.
- The install path is documented for user-local Linux install.

## Phase 1: Core Local Database

Exit only when:

- SQLite schema exists and initializes cleanly.
- Core tables can be created from scratch.
- Insert, fetch, and lookup work for books, anchors, notes, and review items.
- IDs are stable and unique.
- A fresh database can be created without manual steps.

## Phase 2: EPUB Import And Indexing

Exit only when:

- The fixture EPUB can be imported successfully.
- Book title, author, language, and hash are extracted.
- Chapters, paragraphs, and sentences are created as source units.
- Word count is available.
- Exact quote search finds text from the fixture EPUB.
- Re-importing the same EPUB does not duplicate the book.

## Phase 3: Anchor Resolver

Exit only when:

- Exact quotes resolve to a source anchor.
- Normalized quotes resolve when punctuation or spacing changes.
- Ambiguous matches return candidates instead of guessing.
- Low-confidence matches are not treated as final progress.
- Anchor results include confidence and source location fields.

## Phase 4: Reading Notes Workflow

Exit only when:

- A reading session can be logged from the latest anchor.
- Vocabulary notes can be attached to source text.
- Sentence notes can be attached to source text.
- Thought notes can be attached to source text.
- Unanchored notes are explicitly marked as such.
- Today’s session and notes can be retrieved from storage.

## Phase 5: MCP Server

Exit only when:

- Hermes can discover the ReadMemory MCP tools.
- `import_book`, `find_anchor`, `log_progress`, `add_vocabulary`, `add_sentence`, `add_thought`, `get_due_reviews`, `generate_daily_log`, and `search_notes` are callable.
- Tool responses are structured and include IDs.
- Tool responses include source anchors or explicit uncertainty.
- The MCP layer does not own the source of truth.

## Phase 6: Hermes Skill

Exit only when:

- The Skill exists at `~/.hermes/skills/readmemory/SKILL.md`.
- The Skill tells Hermes to use MCP tools, not memory, for facts.
- The Skill handles ambiguous anchors by asking for confirmation.
- The Skill can support one complete check-in flow.
- The Skill remains Linux-targeted and English-reading-specific.

## Phase 7: Markdown Export

Exit only when:

- A daily Markdown log can be generated from stored records.
- The output contains progress, vocabulary, sentences, thoughts, and review items.
- Re-running export does not create duplicate note content.
- The file is usable in Obsidian or plain Markdown.

## Phase 8: Review Queue

Exit only when:

- Due items can be listed for a given day.
- New items receive a next review date.
- Review results update the schedule.
- Wrong answers reset or shorten the interval.
- Review generation works without manual SQL.

## Phase 9: Linux Automation

Exit only when:

- A Linux user can install ReadMemory without editing source code.
- Hermes config for MCP is documented or generated.
- The Skill install step is documented or automated.
- Backup and data directory locations are clear.
- A full local loop runs end to end on Linux.

## Final Gate

The MVP is not finished until this loop works with the fixture EPUB:

1. Install on Linux.
2. Import the EPUB fixture.
3. Ask Hermes to locate a stop quote.
4. Log progress.
5. Save one word, one sentence, and one thought.
6. Generate a daily Markdown log.
7. Ask for due reviews.

If any step depends on guessing instead of verified source data, the phase is not done.
