#!/usr/bin/env bash
set -euo pipefail

marketplace_name="xinhai-lark"
marketplace_source="https://github.com/chang-xinhai/lark-codex-plugin.git"

if command -v codex >/dev/null 2>&1; then
  codex_bin="$(command -v codex)"
elif [[ -x /Applications/Codex.app/Contents/Resources/codex ]]; then
  codex_bin="/Applications/Codex.app/Contents/Resources/codex"
else
  echo "Codex CLI was not found on PATH or inside /Applications/Codex.app." >&2
  exit 1
fi

if ! "$codex_bin" plugin marketplace upgrade "$marketplace_name" --json; then
  echo "Marketplace is not registered yet; adding $marketplace_source ..."
  "$codex_bin" plugin marketplace add "$marketplace_source" --json
  "$codex_bin" plugin marketplace upgrade "$marketplace_name" --json
fi

"$codex_bin" plugin add "lark@$marketplace_name" --json

echo "Lark plugin is current. Start a new Codex task to load the updated skills."
