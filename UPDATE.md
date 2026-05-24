# ReadMemory Update and Release Notes

ReadMemory supports a fixed user-facing update command:

```bash
readmemory-update
```

The command downloads a fresh ReadMemory source archive from GitHub into a
temporary directory, runs the normal Linux installer from that source tree, and
then removes the temporary copy. The installed runtime still uses the same
versioned layout:

```text
~/.local/opt/readmemory/releases/<version>/venv
~/.local/opt/readmemory/current -> releases/<version>
~/.local/bin/readmemory
~/.local/bin/readmemory-mcp
~/.local/bin/readmemory-update
```

Config and user data remain outside the release directory:

```text
~/.config/readmemory
~/.local/share/readmemory
```

## User Update Flow

For normal users, the update command should be the only command they need:

```bash
readmemory-update
```

By default, it resolves the latest GitHub Release for
`ld066077/ReadMemory`, downloads that release source archive, and installs it as
a new local release. The existing config, database, imported books, exports, and
Hermes skill path are preserved.

Advanced users can install a specific release, branch, or commit:

```bash
readmemory-update --ref v0.1.1
readmemory-update --ref main
readmemory-update --repo owner/ReadMemory --ref v0.1.1
```

Environment variables are also supported:

```bash
READMEMORY_UPDATE_REPO=ld066077/ReadMemory readmemory-update
READMEMORY_UPDATE_REF=v0.1.1 readmemory-update
```

This is not an automatic background updater. The user still runs
`readmemory-update` when they want to upgrade.

## First Install From GitHub

For a machine that does not have ReadMemory installed yet, run the update script
directly from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/ld066077/ReadMemory/main/scripts/update-linux.sh | bash
```

Before the first GitHub Release exists, install from the development branch:

```bash
curl -fsSL https://raw.githubusercontent.com/ld066077/ReadMemory/main/scripts/update-linux.sh | bash -s -- --ref main
```

After installation, future upgrades use:

```bash
readmemory-update
```

## Release Rules

The fixed update command makes releases easier for users, but it requires a
stricter release process.

1. Bump the application version for every published release.

   Keep these files in sync:

   ```text
   pyproject.toml
   src/readmemory/__init__.py
   ```

   The installer uses `readmemory.__version__` as the release directory name. If
   code changes are published without a version bump, the installer may replace
   an existing `releases/<version>` directory.

2. Publish stable updates as GitHub Releases.

   `readmemory-update` defaults to the latest GitHub Release, not the `main`
   branch. Use tags such as `v0.1.1`, create a GitHub Release for the tag, and
   make sure the release has passed the Linux install gate.

3. Treat `main` as a development channel.

   `readmemory-update --ref main` is useful for testing, but normal user
   documentation should point to the default release-based update flow.

4. Keep database migrations safe.

   Any schema change must be handled by `readmemory init` or the runtime startup
   path before a release is published. A release should not require users to run
   `readmemory-uninstall --purge`; purge is a destructive reinstall path, not an
   upgrade path.

5. Validate dependencies before publishing.

   The installer creates a fresh virtual environment and resolves Python
   dependencies again. Release validation should include a clean Linux install
   so dependency resolver changes are caught before users run `readmemory-update`.

6. Keep old release cleanup separate from upgrade.

   Upgrades may leave old directories under
   `~/.local/opt/readmemory/releases/`. That is expected for the versioned
   layout and does not affect the active `current` release. Add explicit cleanup
   behavior later if needed; do not make purge part of normal update.

## Release Checklist

Before publishing a GitHub Release:

```text
1. Update the version in pyproject.toml and src/readmemory/__init__.py.
2. Run the test suite.
3. Run ./scripts/install-linux.sh on Linux from a clean checkout.
4. Verify readmemory doctor.
5. Verify readmemory-mcp starts.
6. Verify readmemory-update --ref <tag> from an installed copy.
7. Create and push the git tag.
8. Create the GitHub Release for that tag.
9. Run readmemory-update from an existing installation and verify current moves.
```
