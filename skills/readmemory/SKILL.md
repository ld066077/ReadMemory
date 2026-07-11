---
name: readmemory
description: Use ReadMemory to fully control local English reading memory through the readmemory MCP server, including book discovery, source anchors, progress, vocabulary, sentences, thoughts, reviews, daily logs, status checks, updates, and uninstall guidance.
platforms:
  - linux
---

# ReadMemory Hermes Skill

Use this skill when the user wants Hermes agent to remember, search, review, or
export English reading records. ReadMemory is the source of truth for reading
facts; Hermes agent can summarize and guide the workflow, but it should not keep
exact reading state only in Hermes memory.

## Operating Rules

- Use ReadMemory MCP tools for factual reading records: books, progress,
  anchors, vocabulary, sentence notes, thoughts, reviews, daily logs, and MCP
  health/status checks.
- Start with `status` when the user asks whether ReadMemory works, whether
  Hermes agent is connected, what is loaded, or what needs follow-up.
- Prefer `book_ref` for user-facing workflows. Use exact `book_id` only when it
  was returned by ReadMemory or the user is debugging.
- Do not invent source locations, page numbers, chapter names, progress, or
  notes that ReadMemory did not return.
- Prefer one useful lookup tool call over asking the user for information that
  can be searched in ReadMemory.
- Ask a short clarification only when the missing detail blocks a safe write,
  especially ambiguous book identity or ambiguous source anchor.
- Keep replies concise. Say what was found or saved, and mention the source
  anchor or unanchored status when it matters.

## Tool Names

Hermes agent may expose these as MCP-prefixed tool names such as
`mcp_readmemory_search_notes`; use the ReadMemory tool with the matching action:

- `status`
- `list_books`
- `search_books`
- `resolve_book`
- `import_book`
- `search_source`
- `find_anchor`
- `log_progress`
- `add_vocabulary`
- `add_sentence`
- `add_thought`
- `get_due_reviews`
- `record_review_result`
- `generate_daily_log`
- `reconcile_item`
- `edit_item`
- `delete_item`
- `undo_last`
- `search_notes`
- `get_unanchored_items`

## Book Discovery

When the user mentions a book by title, author, abbreviation, or approximate
name:

1. If the local library state is unclear, call `status` or `list_books`.
2. If the title is approximate, call `search_books(query)`.
3. If one intended book is clear, use that title or id as `book_ref` in later
   calls.
4. If candidates are close, call `resolve_book(book_ref)`. If status is
   `ambiguous`, show the candidate titles and ask the user to choose.
5. Do not ask for an EPUB path until `list_books`/`search_books` shows the book
   is not imported.

## Flexible Intent Handling

### Search Or Recall

When the user asks what they have read, saved, remembered, or previously noted:

1. Resolve the book first if the user named one.
2. Call `search_notes` with the user's key term or phrase and `book_ref` when
   available.
3. If results exist, summarize only those results and include the note type.
4. If no results exist, say ReadMemory has no matching note.
5. Do not answer from general knowledge when the user is asking about their own
   reading memory.

### Reading Progress Check-In

When the user reports a current location, pasted quote, stop point, or reading
session:

1. Resolve the target book with `list_books`, `search_books`, or `resolve_book`
   if needed.
2. Call `find_anchor` with `book_ref` and the provided quote or stop text.
3. If the anchor is resolved, call `log_progress` with the same `book_ref` and
   stop quote.
4. If the user explicitly wants to save a rough location even though the anchor
   is unresolved, call `log_progress(..., allow_unanchored=true)` and state that
   it needs later reconciliation.
5. If the user also gives vocabulary, sentences, or thoughts, save them with the
   same `book_ref`; ReadMemory will attach an anchor when it can.

### Vocabulary, Sentence, And Thought Notes

When the user asks to save words, sentence patterns, examples, reactions, or
thoughts:

1. Resolve the book first if the user named one imprecisely.
2. Resolve an anchor first if the user provided a quote or location.
3. Call `add_vocabulary`, `add_sentence`, or `add_thought` with `book_ref`.
4. If there is no anchor but the user clearly wants the item saved to a known
   book, save it anyway and say no source anchor was attached.
5. Do not silently drop any user-provided meaning, sentence, tags, or examples.

### Reviews

When the user asks what to review, what is due, or wants to start review:

1. Call `get_due_reviews`, with `book_ref` if the user limited the request to a
   book.
2. Present a compact review list grouped by item type if helpful.
3. When the user reports a review result, call `record_review_result` with one
   of `correct`, `wrong`, or `uncertain`.
4. Map informal wording conservatively: remembered = `correct`, forgot =
   `wrong`, shaky/not sure = `uncertain`.

### Daily Log Or Export

When the user asks for today's reading log, a daily summary, or Markdown export:

1. Resolve the book first if needed.
2. Call `generate_daily_log` with `book_ref` and date if available.
3. Report the generated path and a compact summary.
4. Do not fabricate a daily log if ReadMemory has no records for that day.

### Importing Books

EPUB paths refer to the filesystem of the machine running `readmemory-mcp`.
Files uploaded through a Hermes chat or gateway are not automatically available
to ReadMemory. The EPUB must first be placed or downloaded on the MCP host, then
passed to `import_book` as a local path. ReadMemory v0.1.3 does not download
remote URLs itself.

When the user asks to add a book:

1. Call `search_books` first when the title is known, to avoid duplicate import
   requests.
2. If the book is not imported and the user provides a local EPUB path, call
   `import_book` with the path.
3. Report the imported title, author if available, and book id.
4. If import fails, report the failure plainly and ask for a valid local EPUB
   path.

## Status And Recovery

Use `status` to verify that the MCP server is reachable and to inspect current
library counts, due reviews, and unanchored follow-up items.

If ReadMemory tools are missing in Hermes agent:

1. Tell the user the MCP tools are not loaded in the current Hermes agent
   session.
2. Ask them to verify the MCP server and restart or reload Hermes agent tools.
3. Use these commands for terminal verification:

```bash
hermes mcp list
hermes mcp test readmemory
readmemory status
```

When `status` reports unanchored sessions or notes, mention that they are saved
but need source reconciliation. Use `get_unanchored_items` when the user asks
what needs cleanup.

When the user supplies a reliable source quote for an unanchored item, call
`reconcile_item`. Use `edit_item` for explicit corrections and `delete_item`
only after the user clearly requests deletion. If the user immediately regrets
the latest supported write, edit, reconciliation, or deletion, call
`undo_last`.

## Ambiguous Anchor Handling

If `find_anchor.status` is `ambiguous` or `not_found`, do not call
`log_progress` as a completed anchored check-in.

For ambiguous anchors, show the top candidate locations and ask the user to pick
one:

```text
I found multiple possible source locations. Which one should I use?
1. Chapter ..., paragraph ...: "..."
2. Chapter ..., paragraph ...: "..."
```

For `not_found`, ask the user for a longer quote, nearby sentence, chapter, or
book title. If the user still wants the record saved now, use explicit
unanchored capture and say it needs follow-up.

## Maintenance Commands

When the user asks how to install or update ReadMemory, prefer the fixed GitHub
installer/update flow:

```bash
curl -fsSL https://raw.githubusercontent.com/ld066077/ReadMemory/main/scripts/update-linux.sh | bash
readmemory-update
```

When the user asks how to connect ReadMemory to Hermes agent, tell them to add
and verify the MCP server:

```bash
hermes mcp add readmemory --command readmemory-mcp
hermes mcp list
hermes mcp test readmemory
```

Tell the user to enable all ReadMemory tools when Hermes agent prompts for tool
selection.

When the user asks how to remove ReadMemory while keeping config and data:

```bash
readmemory-uninstall
```

When the user explicitly asks to remove ReadMemory including config and data:

```bash
readmemory-uninstall --purge
```

Warn that `readmemory-uninstall --purge` deletes ReadMemory config and data.

## Response Style

- For successful writes, start with the saved fact, not tool details.
- Mention "stored in ReadMemory" only when it helps reassure the user; avoid
  repeating it mechanically.
- For searches, distinguish "no matching ReadMemory note" from "I do not know".
- Keep IDs out of normal replies unless the user is debugging or asks for them.
- If the user asks whether ReadMemory/Hermes agent integration works, use a
  ReadMemory tool and report the concrete result count or tool outcome.

## Install Location

Linux skill path:

```text
~/.hermes/skills/readmemory/SKILL.md
```
