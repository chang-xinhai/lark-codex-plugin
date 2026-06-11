#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
marketplace_name="xinhai-lark"

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    return 1
  fi
}

need codex
need npx

if ! command -v lark-cli >/dev/null 2>&1; then
  echo "Installing official lark-cli..."
  npx @larksuite/cli@latest install
fi

echo "Registering Codex marketplace from: $repo_root"
codex plugin marketplace add "$repo_root" >/dev/null || true

echo "Installing plugin lark@$marketplace_name..."
codex plugin add "lark@$marketplace_name"

echo
echo "Running lark-cli doctor..."
lark-cli doctor || true

if [[ -t 0 && "${SKIP_LARK_SETUP:-0}" != "1" ]]; then
  echo
  read -r -p "Run Lark app configuration and user authorization now? [y/N] " answer
  case "$answer" in
    y|Y|yes|YES)
      lark-cli config init --new
      lark-cli auth login --recommend
      lark-cli doctor || true
      ;;
  esac
fi

cat <<'EOF'

If setup is still incomplete, run:

  lark-cli config init --new
  lark-cli auth login --recommend
  lark-cli doctor

After setup, start a new Codex thread and use @lark.
EOF
