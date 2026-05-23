---
name: readmemory
description: Use ReadMemory to record verified English reading progress, vocabulary, sentences, thoughts, reviews, and Markdown logs through the readmemory MCP server.
platforms:
  - linux
---

# ReadMemory Hermes Skill

Use this skill for English reading notes only.

Always use the `readmemory` MCP tools for factual reading records.

## Rules

- Do not store exact reading progress only in Hermes memory.
- Do not invent source locations.
- Ask for confirmation when anchors are ambiguous.
- Use ReadMemory for facts, Hermes for workflow.

## Core Flow

1. Parse the user's check-in.
2. Call `find_anchor`.
3. If confidence is high, call `log_progress`.
4. Call `add_vocabulary`, `add_sentence`, and `add_thought` if provided.
5. Return a short grounded summary.

## Tool Names

- `import_book`
- `find_anchor`
- `log_progress`
- `add_vocabulary`
- `add_sentence`
- `add_thought`
- `get_due_reviews`
- `generate_daily_log`
- `search_notes`

## Ambiguous Anchor Handling

If `find_anchor.status` is `ambiguous` or `not_found`, do not call `log_progress`.

Ask the user to confirm the source location:

```text
I found multiple possible source locations. Which one should I use?
1. Chapter ..., paragraph ...: "..."
2. Chapter ..., paragraph ...: "..."
```

## Grounded Summary

Every saved-fact response should mention that the record was stored in ReadMemory and include the source anchor if available.

If no verified record exists, say that ReadMemory has no verified record instead of guessing.

## Install Location

Linux skill path:

```text
~/.hermes/skills/readmemory/SKILL.md
```
