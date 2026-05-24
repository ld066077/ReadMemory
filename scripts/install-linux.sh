#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install-linux.sh

Installs ReadMemory into a versioned user-local release directory and writes
stable wrappers into ~/.local/bin, including readmemory-update.
EOF
}

for arg in "$@"; do
  case "$arg" in
    -h|--help)
      usage
      exit 0
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -z "${HOME:-}" ]; then
  echo "HOME is required." >&2
  exit 1
fi

HOME_REAL="$(realpath "$HOME")"

require_home_child() {
  local label="$1"
  local path="$2"
  local resolved
  resolved="$(realpath -m "$path")"
  case "$resolved" in
    "$HOME_REAL"/*) ;;
    *)
      echo "Refusing to use $label outside $HOME_REAL: $path" >&2
      exit 1
      ;;
  esac
}

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required." >&2
  exit 1
}

APP_VERSION="$(PYTHONPATH="$ROOT_DIR/src" python3 -c 'import readmemory; print(readmemory.__version__)')"

python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' || {
  echo "Python 3.11+ is required." >&2
  exit 1
}

INSTALL_ROOT="${READMEMORY_INSTALL_ROOT:-$HOME/.local/opt/readmemory}"
BIN_DIR="${READMEMORY_BIN_DIR:-$HOME/.local/bin}"
CONFIG_DIR="${READMEMORY_CONFIG_DIR:-$HOME/.config/readmemory}"
DATA_DIR="${READMEMORY_DATA_DIR:-$HOME/.local/share/readmemory}"
BOOKS_DIR="${READMEMORY_BOOKS_DIR:-$DATA_DIR/books}"
EXPORT_DIR="${READMEMORY_EXPORT_DIR:-$DATA_DIR/exports}"
LOG_DIR="${READMEMORY_LOG_DIR:-$DATA_DIR/logs}"
DB_PATH="${READMEMORY_DB_PATH:-$DATA_DIR/readmemory.sqlite}"
SKILL_DIR="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills/readmemory}"
RELEASE_DIR="$INSTALL_ROOT/releases/$APP_VERSION"
CURRENT_LINK="$INSTALL_ROOT/current"
MANIFEST_FILE="$INSTALL_ROOT/install-manifest.txt"
STAGING_DIR=""

require_home_child "install root" "$INSTALL_ROOT"
require_home_child "binary directory" "$BIN_DIR"
require_home_child "config directory" "$CONFIG_DIR"
require_home_child "data directory" "$DATA_DIR"
require_home_child "skill directory" "$SKILL_DIR"

cleanup() {
  if [ -n "$STAGING_DIR" ]; then
    rm -rf "$STAGING_DIR"
  fi
}

rewrite_console_script() {
  local script_path="$1"
  local interpreter="$2"
  python3 - "$script_path" "$interpreter" <<'PY'
from pathlib import Path
import sys
script = Path(sys.argv[1])
interpreter = sys.argv[2]
lines = script.read_text(encoding='utf-8').splitlines()
if not lines:
    raise SystemExit(f'{script} is empty')
lines[0] = f'#!{interpreter}'
script.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY
}

shell_quote() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

write_wrapper() {
  local name="$1"
  local target="$2"
  cat > "$BIN_DIR/$name" <<EOF
#!/usr/bin/env sh
set -eu
export READMEMORY_INSTALL_ROOT=$(shell_quote "$INSTALL_ROOT")
export READMEMORY_BIN_DIR=$(shell_quote "$BIN_DIR")
export READMEMORY_CONFIG_DIR=$(shell_quote "$CONFIG_DIR")
export READMEMORY_DATA_DIR=$(shell_quote "$DATA_DIR")
export READMEMORY_BOOKS_DIR=$(shell_quote "$BOOKS_DIR")
export READMEMORY_EXPORT_DIR=$(shell_quote "$EXPORT_DIR")
export READMEMORY_LOG_DIR=$(shell_quote "$LOG_DIR")
export READMEMORY_DB_PATH=$(shell_quote "$DB_PATH")
export HERMES_SKILLS_DIR=$(shell_quote "$SKILL_DIR")
exec $(shell_quote "$target") "\$@"
EOF
  chmod 755 "$BIN_DIR/$name"
}

write_exec_wrapper() {
  local name="$1"
  local target="$2"
  cat > "$BIN_DIR/$name" <<EOF
#!/usr/bin/env sh
set -eu
export READMEMORY_INSTALL_ROOT=$(shell_quote "$INSTALL_ROOT")
export READMEMORY_BIN_DIR=$(shell_quote "$BIN_DIR")
export READMEMORY_CONFIG_DIR=$(shell_quote "$CONFIG_DIR")
export READMEMORY_DATA_DIR=$(shell_quote "$DATA_DIR")
export READMEMORY_BOOKS_DIR=$(shell_quote "$BOOKS_DIR")
export READMEMORY_EXPORT_DIR=$(shell_quote "$EXPORT_DIR")
export READMEMORY_LOG_DIR=$(shell_quote "$LOG_DIR")
export READMEMORY_DB_PATH=$(shell_quote "$DB_PATH")
export HERMES_SKILLS_DIR=$(shell_quote "$SKILL_DIR")
exec $(shell_quote "$target") "\$@"
EOF
  chmod 755 "$BIN_DIR/$name"
}

trap cleanup EXIT

mkdir -p "$INSTALL_ROOT/releases" "$BIN_DIR" "$CONFIG_DIR" "$SKILL_DIR"
STAGING_DIR="$(mktemp -d "$INSTALL_ROOT/.staging.${APP_VERSION}.XXXXXX")"

if ! python3 -m venv "$STAGING_DIR/venv"; then
  cat >&2 <<'EOF'
Failed to create the ReadMemory Python virtual environment.

ReadMemory requires Python 3.11+ with venv/ensurepip support so it can install
its own MCP-capable runtime. On Debian/Ubuntu, install the matching venv package,
for example:

  sudo apt install python3.12-venv

Then rerun ./scripts/install-linux.sh.
EOF
  exit 1
fi

"$STAGING_DIR/venv/bin/pip" install --upgrade pip setuptools wheel >/dev/null
"$STAGING_DIR/venv/bin/pip" install "$ROOT_DIR[epub,mcp]" >/dev/null

export READMEMORY_INSTALL_ROOT="$INSTALL_ROOT"
export READMEMORY_BIN_DIR="$BIN_DIR"
export READMEMORY_CONFIG_DIR="$CONFIG_DIR"
export READMEMORY_DATA_DIR="$DATA_DIR"
export READMEMORY_BOOKS_DIR="$BOOKS_DIR"
export READMEMORY_EXPORT_DIR="$EXPORT_DIR"
export READMEMORY_LOG_DIR="$LOG_DIR"
export READMEMORY_DB_PATH="$DB_PATH"
export HERMES_SKILLS_DIR="$SKILL_DIR"

"$STAGING_DIR/venv/bin/readmemory" init >/dev/null

if [ -d "$RELEASE_DIR" ] || [ -L "$RELEASE_DIR" ]; then
  rm -rf "$RELEASE_DIR"
fi
mv "$STAGING_DIR" "$RELEASE_DIR"
rewrite_console_script "$RELEASE_DIR/venv/bin/readmemory" "$RELEASE_DIR/venv/bin/python3"
rewrite_console_script "$RELEASE_DIR/venv/bin/readmemory-mcp" "$RELEASE_DIR/venv/bin/python3"
STAGING_DIR=""
ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

cat > "$MANIFEST_FILE" <<EOF
install_root=$INSTALL_ROOT
bin_dir=$BIN_DIR
release_dir=$RELEASE_DIR
current_link=$CURRENT_LINK
uninstall_script=$INSTALL_ROOT/uninstall.sh
bin_readmemory=$BIN_DIR/readmemory
bin_readmemory_mcp=$BIN_DIR/readmemory-mcp
bin_update=$BIN_DIR/readmemory-update
bin_uninstall=$BIN_DIR/readmemory-uninstall
config_dir=$CONFIG_DIR
data_dir=$DATA_DIR
db_path=$DB_PATH
books_dir=$BOOKS_DIR
exports_dir=$EXPORT_DIR
logs_dir=$LOG_DIR
skill_dir=$SKILL_DIR
EOF

printf '%s\n' 'readmemory-install-root-v1' > "$INSTALL_ROOT/.readmemory-install-root"
printf '%s\n' 'readmemory-config-dir-v1' > "$CONFIG_DIR/.readmemory-config-dir"
printf '%s\n' 'readmemory-data-dir-v1' > "$DATA_DIR/.readmemory-data-dir"
printf '%s\n' 'readmemory-skill-dir-v1' > "$SKILL_DIR/.readmemory-skill-dir"

if [ ! -f "$CONFIG_DIR/readmemory.toml" ]; then
  cp "$ROOT_DIR/config/readmemory.example.toml" "$CONFIG_DIR/readmemory.toml"
fi

cp "$ROOT_DIR/skills/readmemory/SKILL.md" "$SKILL_DIR/SKILL.md"

cp "$ROOT_DIR/scripts/uninstall-linux.sh" "$INSTALL_ROOT/uninstall.sh"
chmod 755 "$INSTALL_ROOT/uninstall.sh"
cp "$ROOT_DIR/scripts/update-linux.sh" "$INSTALL_ROOT/update.sh"
chmod 755 "$INSTALL_ROOT/update.sh"

write_wrapper "readmemory" "$READMEMORY_INSTALL_ROOT/current/venv/bin/readmemory"
write_wrapper "readmemory-mcp" "$READMEMORY_INSTALL_ROOT/current/venv/bin/readmemory-mcp"
write_exec_wrapper "readmemory-update" "$READMEMORY_INSTALL_ROOT/update.sh"
write_exec_wrapper "readmemory-uninstall" "$READMEMORY_INSTALL_ROOT/uninstall.sh"

echo "ReadMemory installed."
echo "Version: $APP_VERSION"
echo "Install root: $INSTALL_ROOT"
echo "Commands: $BIN_DIR/readmemory, $BIN_DIR/readmemory-mcp, $BIN_DIR/readmemory-update"
echo "Uninstall: $BIN_DIR/readmemory-uninstall [--purge]"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "Add $BIN_DIR to PATH." ;;
esac
