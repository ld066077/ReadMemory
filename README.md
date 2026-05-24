# ReadMemory

ReadMemory is a local source-of-truth layer for English reading notes used through [Hermes agent](https://github.com/NousResearch/hermes-agent).

Hermes agent should use ReadMemory through the `readmemory` MCP server and the ReadMemory skill for Hermes agent. Hermes agent memory is not the factual store.

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

Default user-local paths:

- App releases: `~/.local/opt/readmemory/releases/`
- Current app: `~/.local/opt/readmemory/current`
- Commands: `~/.local/bin/readmemory`, `~/.local/bin/readmemory-mcp`, `~/.local/bin/readmemory-update`
- Config: `~/.config/readmemory/readmemory.toml`
- Data: `~/.local/share/readmemory/`
- Database: `~/.local/share/readmemory/readmemory.sqlite`
- Exports: `~/.local/share/readmemory/exports/`
- Hermes agent skill: `~/.hermes/skills/readmemory/SKILL.md`

If `~/.local/bin` is not on `PATH`, add it before running ReadMemory.

## Verify

```bash
readmemory doctor
readmemory-mcp
```

The MCP command should either start the MCP server or print a ready JSON object if the optional MCP package is unavailable.

The installed Hermes agent skill path is:

```text
~/.hermes/skills/readmemory/SKILL.md
```

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

Back up these paths together:

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
