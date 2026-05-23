#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: uninstall-linux.sh [--purge]

Removes the installed binaries and skill. Use --purge to also remove config
and data directories.
EOF
}

PURGE=0
for arg in "$@"; do
  case "$arg" in
    --purge)
      PURGE=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="$SCRIPT_DIR"
MARKER_FILE="$INSTALL_ROOT/.readmemory-install-root"
MANIFEST_FILE="$INSTALL_ROOT/install-manifest.txt"
HOME_REAL="$(realpath "$HOME")"

if [ ! -f "$MARKER_FILE" ] || [ "$(cat "$MARKER_FILE")" != "readmemory-install-root-v1" ]; then
  echo "Refusing to uninstall: missing ReadMemory install marker at $MARKER_FILE" >&2
  exit 1
fi

if [ ! -f "$MANIFEST_FILE" ]; then
  echo "Refusing to uninstall: missing manifest at $MANIFEST_FILE" >&2
  exit 1
fi

manifest_get() {
  key="$1"
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      "$key="*)
        printf '%s\n' "${line#*=}"
        return 0
        ;;
    esac
  done < "$MANIFEST_FILE"
  return 1
}

if [ "$(manifest_get install_root)" != "$INSTALL_ROOT" ]; then
  echo "Refusing to uninstall: manifest root does not match script location." >&2
  exit 1
fi

require_manifest_value() {
  key="$1"
  value="$(manifest_get "$key")"
  if [ -z "$value" ]; then
    echo "Refusing to uninstall: manifest is missing $key" >&2
    exit 1
  fi
  printf '%s\n' "$value"
}

require_home_child() {
  label="$1"
  path="$2"
  resolved="$(realpath -m "$path")"
  case "$resolved" in
    "$HOME_REAL"/*) ;;
    *)
      echo "Refusing to use $label outside $HOME_REAL: $path" >&2
      exit 1
      ;;
  esac
}

BIN_DIR="$(require_manifest_value bin_dir)"
CONFIG_DIR="$(require_manifest_value config_dir)"
DATA_DIR="$(require_manifest_value data_dir)"
SKILL_DIR="$(require_manifest_value skill_dir)"

require_home_child "install root" "$INSTALL_ROOT"
require_home_child "binary directory" "$BIN_DIR"
require_home_child "config directory" "$CONFIG_DIR"
require_home_child "data directory" "$DATA_DIR"
require_home_child "skill directory" "$SKILL_DIR"

safe_rm_install_root() {
  case "$INSTALL_ROOT" in
    ""|"/"|"$HOME"|"$HOME/"|"$HOME/.local"|"$HOME/.local/")
      echo "Refusing to remove unsafe install root: $INSTALL_ROOT" >&2
      exit 1
      ;;
  esac
  rm -rf "$INSTALL_ROOT"
}

safe_rm_marked_dir() {
  dir="$1"
  marker="$2"
  marker_value="$3"
  if [ ! -d "$dir" ]; then
    return 0
  fi
  case "$dir" in
    ""|"/"|"$HOME"|"$HOME/"|"$HOME/.config"|"$HOME/.config/"|"$HOME/.local"|"$HOME/.local/"|"$HOME/.local/share"|"$HOME/.local/share/"|"$HOME/.hermes"|"$HOME/.hermes/"|"$HOME/.hermes/skills"|"$HOME/.hermes/skills/")
      echo "Refusing to remove unsafe path: $dir" >&2
      exit 1
      ;;
  esac
  if [ ! -f "$dir/$marker" ] || [ "$(cat "$dir/$marker")" != "$marker_value" ]; then
    echo "Refusing to purge unmarked ReadMemory path: $dir" >&2
    exit 1
  fi
  rm -rf "$dir"
}

assert_marked_dir() {
  dir="$1"
  marker="$2"
  marker_value="$3"
  if [ ! -d "$dir" ]; then
    return 0
  fi
  if [ ! -f "$dir/$marker" ] || [ "$(cat "$dir/$marker")" != "$marker_value" ]; then
    echo "Refusing to purge unmarked ReadMemory path: $dir" >&2
    exit 1
  fi
}

assert_marked_dir "$SKILL_DIR" ".readmemory-skill-dir" "readmemory-skill-dir-v1"
if [ "$PURGE" -eq 1 ]; then
  assert_marked_dir "$CONFIG_DIR" ".readmemory-config-dir" "readmemory-config-dir-v1"
  assert_marked_dir "$DATA_DIR" ".readmemory-data-dir" "readmemory-data-dir-v1"
fi

rm -f "$BIN_DIR/readmemory" "$BIN_DIR/readmemory-mcp" "$BIN_DIR/readmemory-uninstall"
safe_rm_marked_dir "$SKILL_DIR" ".readmemory-skill-dir" "readmemory-skill-dir-v1"

if [ "$PURGE" -eq 1 ]; then
  safe_rm_marked_dir "$CONFIG_DIR" ".readmemory-config-dir" "readmemory-config-dir-v1"
  safe_rm_marked_dir "$DATA_DIR" ".readmemory-data-dir" "readmemory-data-dir-v1"
fi

safe_rm_install_root

echo "ReadMemory removed."
if [ "$PURGE" -eq 1 ]; then
  echo "Config and data were removed."
else
  echo "Config and data were kept. Re-run with --purge to remove them."
fi
