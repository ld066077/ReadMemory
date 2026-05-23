# ReadMemory

ReadMemory is a local source-of-truth layer for English reading notes used through Hermes.

Hermes should use ReadMemory through the `readmemory` MCP server and the ReadMemory Hermes Skill. Hermes memory is not the factual store.

## Linux Install

Requirements:

- Linux shell environment
- Python 3.11+
- Hermes with MCP server support

Install from the repository:

```bash
./scripts/install-linux.sh
```

Default user-local paths:

- App releases: `~/.local/opt/readmemory/releases/`
- Current app: `~/.local/opt/readmemory/current`
- Commands: `~/.local/bin/readmemory`, `~/.local/bin/readmemory-mcp`
- Config: `~/.config/readmemory/readmemory.toml`
- Data: `~/.local/share/readmemory/`
- Database: `~/.local/share/readmemory/readmemory.sqlite`
- Exports: `~/.local/share/readmemory/exports/`
- Hermes skill: `~/.hermes/skills/readmemory/SKILL.md`

If `~/.local/bin` is not on `PATH`, add it before running ReadMemory.

## Verify

```bash
readmemory doctor
readmemory-mcp
```

The MCP command should either start the MCP server or print a ready JSON object if the optional MCP package is unavailable.

## Hermes MCP Config

Use `config/hermes-mcp.example.yaml` as the starting point:

```yaml
mcp_servers:
  readmemory:
    command: "readmemory-mcp"
    args:
      - "--config"
      - "/home/user/.config/readmemory/readmemory.toml"
```

The installed skill path is:

```text
~/.hermes/skills/readmemory/SKILL.md
```

## Upgrade

Run the installer again from the new repository version:

```bash
./scripts/install-linux.sh
```

The installer creates a versioned release under `~/.local/opt/readmemory/releases/`, repoints `~/.local/opt/readmemory/current`, refreshes wrappers in `~/.local/bin`, and keeps existing config and data.

## Uninstall

Remove the application, command wrappers, and Hermes skill while keeping config and data:

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

Run tests from the repository:

```bash
python -m pytest
```
