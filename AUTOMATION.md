Keep the local Lark/Feishu Codex plugin up to date from the registered Codex plugin marketplace `xinhai-lark`, whose source should be `git@github.com:chang-xinhai/lark-codex-plugin.git`.

Steps:
1. Inspect `~/.codex/config.toml` and confirm `[marketplaces.xinhai-lark]` exists with `source_type = "git"` and `source = "git@github.com:chang-xinhai/lark-codex-plugin.git"`. If it is missing or points somewhere else, report that clearly and do not change unrelated config.
2. Read the currently installed plugin version from `~/.codex/plugins/cache/xinhai-lark/lark/*/.codex-plugin/plugin.json` if present.
3. Refresh the marketplace. First try `codex plugin marketplace upgrade xinhai-lark`. If that fails because the Codex CLI fresh clone times out or reports `fatal: early EOF`, use the known local marketplace clone fallback:
   - Confirm `~/.codex/.tmp/marketplaces/xinhai-lark` is a git worktree with remote `origin` equal to `git@github.com:chang-xinhai/lark-codex-plugin.git`.
   - Run `git -C ~/.codex/.tmp/marketplaces/xinhai-lark fetch --prune origin main`.
   - Run `git -C ~/.codex/.tmp/marketplaces/xinhai-lark reset --hard origin/main`. Only do this inside that marketplace cache clone.
4. Reinstall/update the plugin cache with `codex plugin add lark@xinhai-lark --json`. Prefer `/Applications/Codex.app/Contents/Resources/codex` if `codex` is not on PATH.
5. Read the installed plugin version again from the cache and verify `plugins."lark@xinhai-lark".enabled = true` remains set in `~/.codex/config.toml`.
6. Report the result compactly: old version, new version, whether an update happened, which refresh path was used, and any command errors. If SSH/GitHub access fails, include the exact failure and leave the existing local plugin install in place.
