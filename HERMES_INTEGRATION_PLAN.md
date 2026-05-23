# Hermes Agent Integration Plan

## 1. Decision

ReadMemory should integrate with Hermes Agent as an external MCP server first.

This is the best fit because ReadMemory is a domain-specific system with its own source-of-truth database, EPUB index, review scheduler, and Markdown exporters. Hermes should act as the conversational agent that calls ReadMemory tools. ReadMemory should not depend on Hermes memory as its primary data store.

Recommended integration stack:

```text
User
  |
Hermes CLI / Messaging Gateway / API frontend
  |
Hermes Agent
  |
ReadMemory MCP Server
  |
ReadMemory Application Service
  |
SQLite or Postgres + EPUB Index + Markdown / Anki Exporters
```

## 2. Why MCP First

Hermes Agent officially supports MCP as the cleanest way to connect tools that live outside Hermes itself. MCP supports both local stdio servers and remote HTTP servers, automatic tool discovery, per-server tool filtering, and utility wrappers for resources and prompts when supported.

For ReadMemory, MCP has the right boundary:

- Hermes handles conversation, reasoning, scheduling, and message delivery.
- ReadMemory owns facts, source anchors, review state, and exports.
- The integration can run locally first through stdio, then move to HTTP when hosted.
- Tool exposure can be minimized with Hermes MCP filtering.
- Hermes core does not need to be modified.

## 3. What ReadMemory Should Expose To Hermes

### 3.1 V1 MCP Tools

Expose a small, explicit tool surface:

- `import_book`: import an EPUB from a local path or uploaded file reference.
- `find_anchor`: locate a quote in a book and return anchor candidates with confidence.
- `log_progress`: record a reading session with start and end anchors.
- `add_vocabulary`: save one or more words with source sentence and review metadata.
- `add_sentence`: save a sentence note linked to a source anchor.
- `add_thought`: save a thought note linked to the latest or specified anchor.
- `get_due_reviews`: return due review items.
- `generate_daily_log`: produce Markdown for a date.
- `generate_weekly_report`: summarize reading progress and review state.
- `search_notes`: retrieve thoughts, sentences, and vocabulary with source anchors.

### 3.2 Tool Design Rules

- Return structured JSON, not prose.
- Always include stable record IDs.
- Always include source anchors when available.
- Include `confidence` for quote matching and semantic retrieval.
- Make write tools idempotent where possible.
- Separate read tools from write tools so Hermes can safely run read-only searches.
- Do not let Hermes write directly to SQLite/Postgres.

## 4. Hermes Features To Use

### 4.1 MCP Client

Primary integration path.

ReadMemory should ship a local stdio MCP server for V1:

```yaml
mcp_servers:
  readmemory:
    command: "readmemory-mcp"
    args: ["--db", "/path/to/readmemory.sqlite"]
    tools:
      include:
        - import_book
        - find_anchor
        - log_progress
        - add_vocabulary
        - add_sentence
        - add_thought
        - get_due_reviews
        - generate_daily_log
        - generate_weekly_report
        - search_notes
      prompts: false
      resources: false
```

Later, hosted ReadMemory can expose an HTTP MCP endpoint:

```yaml
mcp_servers:
  readmemory:
    url: "https://api.readmemory.example.com/mcp"
    headers:
      Authorization: "Bearer ${READMEMORY_API_KEY}"
```

### 4.2 Skills

Create a Hermes skill named `readmemory`.

The skill should not store user data. It should teach Hermes how to use the MCP tools:

- How to parse daily reading check-ins.
- When to call `find_anchor`.
- When to ask for clarification.
- How to distinguish verified facts from inference.
- How to generate a concise daily review.
- How to avoid writing unsupported notes.

Suggested slash commands:

- `/readmemory progress ...`
- `/readmemory words ...`
- `/readmemory sentence ...`
- `/readmemory thought ...`
- `/readmemory review`

The skill is procedural memory. The database is factual memory.

### 4.3 Cron

Use Hermes cron for scheduled review and reports.

Useful jobs:

- Daily morning review: call `get_due_reviews`, then send a short review list.
- Nightly reading log: call `generate_daily_log`.
- Weekly report: call `generate_weekly_report`.

ReadMemory should keep review scheduling state in its own database. Hermes cron only triggers delivery.

### 4.4 Messaging Gateway

Hermes Messaging Gateway is valuable because the user can log reading from Telegram, Discord, Slack, Feishu/Lark, WeCom, Email, and other surfaces without ReadMemory building those integrations first.

V1 should support text-first check-ins:

```text
Book: Animal Farm
Stopped at: "Man is the only creature that consumes without producing."
Words: ensconce, lantern, knacker
Sentence: Man is the only creature that consumes without producing.
Thought: Old Major's speech feels like political mobilization.
```

EPUB import should start as local file path or ReadMemory UI upload. Chat attachment import can come later, because file handling differs across platforms and Hermes API file upload support is limited.

### 4.5 API Server

Hermes API Server is useful if ReadMemory later builds its own web UI and wants Hermes as the agent backend through OpenAI-compatible APIs.

Use this later, not for the first integration.

Reason:

- API Server is good for frontends.
- MCP is better when Hermes needs to use ReadMemory as a tool.
- ReadMemory needs direct file upload and structured database operations, which fit its own app service better than pushing all input through the Hermes API.

### 4.6 Built-In And External Hermes Memory

Do not use Hermes memory as ReadMemory's source of truth.

Hermes built-in memory is bounded and curated. It is good for preferences and stable user/project facts, such as:

- User reads English books to improve English.
- User prefers British pronunciation practice.
- User uses Obsidian or Markdown.
- User prefers concise daily reviews.

It is not suitable for exact reading sessions, source anchors, vocabulary records, or review state.

External memory providers can be useful later for personalization or cross-session recall, but they should remain additive. ReadMemory should keep all exact learning records in its own structured database.

## 5. Paths Not Recommended For V1

### 5.1 Native Hermes Core Tool

Do not add ReadMemory as a built-in Hermes core tool in V1.

Reason:

- Higher maintenance burden.
- Coupled to Hermes internals.
- Harder to distribute independently.
- MCP already provides the right extension boundary.

### 5.2 Hermes Plugin First

Hermes plugins are useful for custom local tools and hooks, but they are more coupled than MCP.

Use a plugin only if:

- ReadMemory needs Hermes lifecycle hooks.
- ReadMemory needs native slash-command registration beyond a skill.
- MCP cannot express the required interaction.

### 5.3 Python Library Embedding First

Embedding `AIAgent` directly inside ReadMemory is not the best first step.

Reason:

- It makes ReadMemory own Hermes runtime configuration.
- It couples app deployment to Hermes Python internals.
- Hermes already provides CLI, gateway, cron, API, and MCP surfaces.

Use Python embedding only for experiments or tightly controlled local automation.

### 5.4 Hermes Memory As Main Database

Do not store reading facts in `MEMORY.md`, `USER.md`, Honcho, Mem0, Hindsight, or other agent memory providers as the only copy.

Use those systems for personalization and recall hints, not authoritative facts.

## 6. Implementation Phases

### Phase 1: Local MCP Prototype

Goal: prove Hermes can record and retrieve English reading notes through ReadMemory.

Deliverables:

- SQLite schema.
- EPUB import command.
- Local stdio MCP server.
- `find_anchor`, `log_progress`, `add_vocabulary`, `add_sentence`, `add_thought`.
- Basic Hermes MCP config example.
- Manual test from `hermes chat`.

### Phase 2: Hermes Skill

Goal: make Hermes reliably use the tools in the intended workflow.

Deliverables:

- `readmemory` skill.
- Examples for progress, words, sentence, thought, and review.
- Clarification rules for ambiguous anchors.
- Grounding rule: no source, no factual claim.

### Phase 3: Review And Markdown Automation

Goal: make the system useful every day.

Deliverables:

- `get_due_reviews`.
- `generate_daily_log`.
- `generate_weekly_report`.
- Hermes cron examples for daily and weekly jobs.
- Markdown export to an Obsidian-compatible folder.

### Phase 4: Hosted HTTP MCP

Goal: support multi-device or hosted use.

Deliverables:

- HTTP MCP server.
- User authentication.
- Per-user database isolation.
- Rate limits and audit logs.
- Tool whitelist examples.

### Phase 5: Rich Integrations

Goal: add ecosystem integrations after the reading-note loop is stable.

Candidates:

- Anki export or sync.
- Obsidian vault sync.
- Readwise import/export.
- Messaging attachment import.
- Semantic search over thoughts.
- Optional memory provider integration for user preferences.

## 7. Reliability Rules

ReadMemory should enforce these rules at the tool layer, not only in prompts:

- `log_progress` requires a verified book and anchor.
- `add_vocabulary` should attach the best source sentence or mark the item as unanchored.
- `add_thought` should attach to the latest reading anchor only if the latest anchor is recent enough.
- `search_notes` should return record IDs and source anchors.
- `generate_daily_log` should only summarize stored records.
- Any low-confidence match should require user confirmation before becoming progress.

## 8. Best Fit Summary

The best adaptation plan is:

```text
MCP server for capabilities
+ Hermes skill for workflow instructions
+ Hermes cron for daily/weekly review delivery
+ Hermes messaging gateway for user-facing chat surfaces
+ ReadMemory database as source of truth
+ Optional Hermes memory only for user preferences
```

This keeps the product boundary clean:

- Hermes is the agent and user interface layer.
- ReadMemory is the verified English reading memory layer.
- The integration remains portable, testable, and independent of Hermes internals.

## Official Documentation References

- Hermes Agent documentation: https://hermes-agent.nousresearch.com/docs/
- MCP integration: https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp
- Skills system: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Cron: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron
- Messaging Gateway: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/
- API Server: https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server
- Persistent Memory: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- Memory Providers: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers
- Plugins: https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
- Python Library: https://hermes-agent.nousresearch.com/docs/guides/python-library
