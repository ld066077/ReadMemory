---
name: readmemory
description: Use ReadMemory to record verified English reading progress, vocabulary, sentences, thoughts, reviews, and Markdown logs through the readmemory MCP server.
platforms:
  - linux
---

# ReadMemory Hermes Skill

Use this skill when the user wants Hermes to remember, search, review, or export
English reading records. ReadMemory is the source of truth for reading facts;
Hermes can summarize and guide the workflow, but it should not keep exact
reading state only in Hermes memory.

## Operating Rules

- Use ReadMemory MCP tools for factual reading records: books, progress,
  anchors, vocabulary, sentence notes, thoughts, reviews, and daily logs.
- Do not invent source locations, page numbers, chapter names, progress, or
  notes that ReadMemory did not return.
- Prefer one useful tool call over asking the user for information that can be
  searched in ReadMemory.
- Ask a short clarification only when the missing detail blocks a safe write,
  especially book identity or ambiguous source anchor.
- Keep replies concise. Say what was found or saved, and mention the source
  anchor when it matters.

## Tool Names

Hermes may expose these as MCP-prefixed tool names such as
`mcp_readmemory_search_notes`; use the ReadMemory tool with the matching action:

- `import_book`
- `find_anchor`
- `log_progress`
- `add_vocabulary`
- `add_sentence`
- `add_thought`
- `get_due_reviews`
- `record_review_result`
- `generate_daily_log`
- `search_notes`

## Flexible Intent Handling

### Search Or Recall

When the user asks what they have read, saved, remembered, or previously noted:

1. Call `search_notes` with the user's key term or phrase.
2. If results exist, summarize only those results and include the note type.
3. If no results exist, say ReadMemory has no matching note.
4. Do not answer from general knowledge when the user is asking about their own
   reading memory.

### Reading Progress Check-In

When the user reports a current location, pasted quote, stop point, or reading
session:

1. Identify the target book. If the book is not clear, ask which book.
2. Call `find_anchor` with the provided quote or stop text.
3. If the anchor is resolved with high confidence, call `log_progress`.
4. If the user also gives vocabulary, sentences, or thoughts, save them with the
   same anchor when possible.
5. Reply with a short saved summary and the resolved location.

### Vocabulary, Sentence, And Thought Notes

When the user asks to save words, sentence patterns, examples, reactions, or
thoughts:

1. Resolve an anchor first if the user provided a quote or location.
2. Call `add_vocabulary`, `add_sentence`, or `add_thought` as appropriate.
3. If there is no anchor but the user clearly wants the item saved to a known
   book, save it without an anchor and say no source anchor was attached.
4. Do not silently drop any user-provided meaning, sentence, tags, or examples.

### Reviews

When the user asks what to review, what is due, or wants to start review:

1. Call `get_due_reviews`.
2. Present a compact review list grouped by item type if helpful.
3. When the user reports a review result, call `record_review_result` with one
   of `correct`, `wrong`, or `uncertain`.
4. If the user's result wording is informal, map it conservatively: remembered =
   `correct`, forgot = `wrong`, shaky/not sure = `uncertain`.

### Daily Log Or Export

When the user asks for today's reading log, a daily summary, or Markdown export:

1. Call `generate_daily_log` with the book id and date if available.
2. Report the generated path and a compact summary.
3. Do not fabricate a daily log if ReadMemory has no records for that day.

### Importing Books

When the user provides a local EPUB path and asks to add it to ReadMemory:

1. Call `import_book` with the path.
2. Report the imported title, author if available, and book id.
3. If import fails, report the failure plainly and ask for a valid local EPUB
   path.

### Maintenance Commands

When the user asks how to install or update ReadMemory, prefer the fixed GitHub
installer/update flow:

```bash
curl -fsSL https://raw.githubusercontent.com/ld066077/ReadMemory/main/scripts/update-linux.sh | bash
readmemory-update
```

When the user asks how to remove ReadMemory while keeping config and data:

```bash
readmemory-uninstall
```

When the user explicitly asks to remove ReadMemory including config and data:

```bash
readmemory-uninstall --purge
```

Warn that `readmemory-uninstall --purge` deletes ReadMemory config and data.

## Ambiguous Anchor Handling

If `find_anchor.status` is `ambiguous` or `not_found`, do not call
`log_progress` for that check-in.

For ambiguous anchors, show the top candidate locations and ask the user to pick
one:

```text
I found multiple possible source locations. Which one should I use?
1. Chapter ..., paragraph ...: "..."
2. Chapter ..., paragraph ...: "..."
```

For `not_found`, ask the user for a longer quote, nearby sentence, chapter, or
book title. Do not guess.

## Response Style

- For successful writes, start with the saved fact, not tool details.
- Mention "stored in ReadMemory" only when it helps reassure the user; avoid
  repeating it mechanically.
- For searches, distinguish "no matching ReadMemory note" from "I do not know".
- Keep IDs out of normal replies unless the user is debugging or asks for them.
- If the user asks whether ReadMemory/Hermes integration works, use a ReadMemory
  tool and report the concrete result count or tool outcome.

## Install Location

Linux skill path:

```text
~/.hermes/skills/readmemory/SKILL.md
```
