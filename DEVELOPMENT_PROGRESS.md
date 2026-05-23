# ReadMemory Development Progress

## Current State

ReadMemory is now a release candidate for the English-reading-notes MVP.

The product boundary remains:

- ReadMemory owns the verified database, EPUB index, anchors, notes, review queue, and Markdown export.
- Hermes owns orchestration and user interaction through the `readmemory` Skill.
- Hermes memory must not be used as the factual store.

## Release Candidate Scope

Included:

- Linux-first user-local installation.
- SQLite source-of-truth database.
- English EPUB import and source indexing.
- Quote anchor resolution with ambiguity handling.
- Reading progress, vocabulary, sentence, and thought notes.
- MCP tool surface for Hermes.
- Hermes Skill instructions.
- Daily Markdown export.
- Simple review queue.
- Safe uninstall and purge workflow.

Not included:

- Chinese reading notes.
- Other languages.
- Packaged distro install through deb/rpm/pacman.
- Production systemd service.
- Real Hermes UI integration test on a Linux host.

## Linux Installation Shape

The RC installer uses a user-local, versioned layout:

```text
~/.local/opt/readmemory/
  .readmemory-install-root
  current -> releases/<version>
  install-manifest.txt
  uninstall.sh
  releases/
    <version>/
      venv/

~/.local/bin/
  readmemory
  readmemory-mcp
  readmemory-uninstall

~/.config/readmemory/
  .readmemory-config-dir
  readmemory.toml

~/.local/share/readmemory/
  .readmemory-data-dir
  readmemory.sqlite
  books/
  exports/
  logs/

~/.hermes/skills/readmemory/
  .readmemory-skill-dir
  SKILL.md
```

This layout is intended to make upgrades and uninstall predictable:

- Upgrade: install the new version, repoint `current`, preserve config and data.
- Normal uninstall: remove app, wrappers, and skill; keep config and data.
- Purge uninstall: remove app, wrappers, skill, config, and data.

## Phase Status

| Phase | Status | RC Notes |
| --- | --- | --- |
| 0. Project Foundation | Implemented | CLI, MCP entry point, config, data paths, Linux installer. |
| 1. Core Local Database | Implemented | SQLite schema and repository layer covered by tests. |
| 2. EPUB Import And Indexing | Implemented | Fixture EPUB import, metadata, source units, search, duplicate prevention. |
| 3. Anchor Resolver | Implemented | Exact, normalized, ambiguous, and low-confidence paths covered. |
| 4. Reading Notes Workflow | Implemented | Progress, vocabulary, sentence, thought, and today's retrieval. |
| 5. MCP Server | Implemented | Tool wrappers over service methods; ReadMemory remains source of truth. |
| 6. Hermes Skill | Implemented | Skill installed by Linux script and instructs Hermes to use MCP tools. |
| 7. Markdown Export | Implemented | Daily export with idempotent output. |
| 8. Review Queue | Implemented | Due reviews and review result scheduling. |
| 9. Linux Automation | RC | Installer, config sample, skill install, manifest, uninstall, and purge exist. Actual Linux-host final gate remains. |

## Verification Already Done

Validated in the local workspace:

- Unit and workflow tests for phases 1-8.
- Fixture EPUB import using `tests/On the Heights of Despair (E. M. Cioran).epub`.
- CLI startup through `readmemory init` and `readmemory doctor`.
- MCP fallback startup through `python -m readmemory.mcp`.
- Shell syntax checks for Linux install and uninstall scripts.

Known limitation:

- The final install gate still requires a Linux run of `./scripts/install-linux.sh`, import, note creation, export, review lookup, uninstall, and purge.

## Final Gate Before MVP

Run this on Linux or WSL:

1. `./scripts/install-linux.sh`
2. `readmemory doctor`
3. `readmemory import-book "tests/On the Heights of Despair (E. M. Cioran).epub"`
4. Locate a stop quote with `find_anchor` or Hermes via MCP.
5. Log progress.
6. Save one vocabulary note, one sentence note, and one thought note.
7. Generate a daily Markdown log.
8. Get due reviews.
9. Run `readmemory-uninstall`.
10. Reinstall and confirm config/data are preserved.
11. Run `readmemory-uninstall --purge`.
12. Confirm install root, wrappers, skill, config, and data are removed.

The MVP should not be called final until this gate passes on Linux.
