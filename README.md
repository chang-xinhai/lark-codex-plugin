# Lark / Feishu Codex Plugin

One Codex plugin entry point for the official Lark/Feishu `lark-cli` skills.

This repository packages the official `lark-*` agent skills from
[`larksuite/cli`](https://github.com/larksuite/cli) as a Codex plugin named
`lark`, plus a small `@lark` router skill for first-run setup and cross-domain
requests.

## What This Gives You

- `@lark` as one plugin entry point in Codex.
- Bundled Lark skills for Calendar, Docs, Drive, Wiki, Base, Sheets, IM, Mail,
  Tasks, meetings, approvals, OKR, attendance, Slides, Whiteboard, Apps, and
  OpenAPI exploration.
- A bootstrap script for machines that have Codex and Lark.app but no
  `lark-cli`, no `lark-*` skills, and no plugin installed yet.
- A sync script and GitHub Action to pull the latest official skills from
  `larksuite/cli`.

## Fresh Install

Requirements:

- Codex CLI / Codex desktop installed.
- Node.js with `npm` / `npx`.
- A Lark or Feishu account.

From a terminal:

```bash
git clone https://github.com/chang-xinhai/lark-codex-plugin.git
cd lark-codex-plugin
./scripts/bootstrap.sh
```

The bootstrap script will:

1. Install `lark-cli` if missing using the official npm installer.
2. Register this repository as a Codex plugin marketplace.
3. Install `lark@xinhai-lark`.
4. Run `lark-cli doctor`.
5. Offer to run Lark app configuration and user authorization.

Then open a new Codex thread and use:

```text
@lark summarize today's calendar, tasks, and meeting notes
```

## Manual Install

If you prefer explicit steps:

```bash
npx @larksuite/cli@latest install
lark-cli config init --new
lark-cli auth login --recommend
lark-cli doctor

codex plugin marketplace add https://github.com/chang-xinhai/lark-codex-plugin
codex plugin add lark@xinhai-lark
```

Start a new Codex thread after installation so the plugin skills are loaded.

## Authentication Lifecycle

The plugin distinguishes application setup from user-token maintenance:

- **First-time application setup:** use `lark-cli config init --new` only when a
  profile has no application configuration. Organization administrators may
  need to approve the application's requested scopes.
- **Normal token refresh:** when `auth status --verify` succeeds, continue using
  the profile and let `lark-cli` refresh the user access token automatically.
- **Expired refresh token:** keep the existing profile and application, then
  reauthorize only the already-approved scopes needed for the task. Do not run
  `config init --new`, and do not default to `--domain all`.

For example:

```bash
lark-cli --profile <name> auth status --json --verify
lark-cli --profile <name> auth login \
  --scope "<already-approved-scope-1> <already-approved-scope-2>" \
  --no-wait --json
```

This reissues the organization's user/refresh token for the same application.
Requesting a new scope is a separate permission change and may require an
administrator; reauthorizing previously approved scopes should not.

## Updating An Existing Install

This repository can stay current through GitHub Actions, but Codex keeps an
installed plugin cache locally. Existing users should refresh the Git
marketplace and reinstall the plugin after upstream syncs:

```bash
codex plugin marketplace upgrade xinhai-lark
codex plugin add lark@xinhai-lark
```

Then start a new Codex thread.

For automatic daily refreshes, use the ready-to-copy Codex automation prompt in
[`AUTOMATION.md`](AUTOMATION.md).

## Keeping Up With Official Lark Skills

This repository intentionally treats
[`larksuite/cli`](https://github.com/larksuite/cli) as the upstream source of
truth. To sync manually:

```bash
python3 scripts/sync_official_lark_skills.py
```

The script clones the official repo, copies `skills/lark-*`, preserves this
plugin's `skills/lark` router, applies repository-owned patches from
`overrides/`, updates plugin version metadata, and refreshes third-party
attribution files. Override patches are checked before application so an
upstream conflict fails visibly instead of silently dropping local guidance.

The included GitHub Action runs on a schedule and can also be triggered
manually from the Actions tab.

## Notes On Icons And Trademarks

The public repository uses a Lark-blue original plugin icon. It does not vendor
the proprietary macOS app icon from `Lark.app`. Lark, Feishu, and their logos
are trademarks of their respective owners.

## Upstream License

The official `larksuite/cli` project and its skills are MIT licensed. See
[`THIRD_PARTY_NOTICES/larksuite-cli-LICENSE`](THIRD_PARTY_NOTICES/larksuite-cli-LICENSE).
