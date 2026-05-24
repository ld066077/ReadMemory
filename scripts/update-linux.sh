#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: update-linux.sh [--repo OWNER/REPO] [--ref REF]

Downloads ReadMemory from GitHub and runs the Linux installer from the
downloaded source tree.

Defaults:
  --repo ld066077/ReadMemory
  --ref latest

The special ref "latest" resolves to the latest GitHub Release tag. Use
--ref main to install from the development branch.
EOF
}

REPO="${READMEMORY_UPDATE_REPO:-ld066077/ReadMemory}"
REF="${READMEMORY_UPDATE_REF:-latest}"
TMP_DIR=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then
        echo "--repo requires OWNER/REPO." >&2
        exit 1
      fi
      REPO="$2"
      shift 2
      ;;
    --ref)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then
        echo "--ref requires a release tag, branch, or commit." >&2
        exit 1
      fi
      REF="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require_command() {
  local name="$1"
  command -v "$name" >/dev/null 2>&1 || {
    echo "$name is required." >&2
    exit 1
  }
}

cleanup() {
  if [ -n "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
  fi
}

resolve_latest_release() {
  local latest_url
  latest_url="$(curl -fsSLI -o /dev/null -w '%{url_effective}' "https://github.com/$REPO/releases/latest")" || {
    cat >&2 <<EOF
Failed to resolve the latest GitHub Release for $REPO.

If this project has not published a release yet, install from a specific ref:

  readmemory-update --ref main
EOF
    exit 1
  }

  case "$latest_url" in
    */releases/tag/*)
      printf '%s\n' "${latest_url##*/releases/tag/}"
      ;;
    *)
      cat >&2 <<EOF
Could not find a latest GitHub Release tag for $REPO.

Install a specific ref instead:

  readmemory-update --ref main
EOF
      exit 1
      ;;
  esac
}

find_source_dir() {
  local dir
  dir="$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | sort | sed -n '1p')"
  if [ -z "$dir" ] || [ ! -f "$dir/scripts/install-linux.sh" ]; then
    echo "Downloaded archive does not contain scripts/install-linux.sh." >&2
    exit 1
  fi
  printf '%s\n' "$dir"
}

require_command curl
require_command bash
require_command tar
require_command find
require_command sed
require_command sort
require_command mktemp

case "$REPO" in
  */*) ;;
  *)
    echo "--repo must be in OWNER/REPO form." >&2
    exit 1
    ;;
esac

RESOLVED_REF="$REF"
if [ "$REF" = "latest" ]; then
  RESOLVED_REF="$(resolve_latest_release)"
fi

trap cleanup EXIT
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/readmemory-update.XXXXXX")"
ARCHIVE="$TMP_DIR/readmemory.tar.gz"

echo "Downloading ReadMemory from $REPO@$RESOLVED_REF..."
curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$RESOLVED_REF" -o "$ARCHIVE"
tar -xzf "$ARCHIVE" -C "$TMP_DIR"

SOURCE_DIR="$(find_source_dir)"
echo "Installing ReadMemory from $REPO@$RESOLVED_REF..."
bash "$SOURCE_DIR/scripts/install-linux.sh"
