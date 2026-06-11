# Lark / Feishu Codex Plugin

This local plugin bundles the Lark/Feishu Codex skills behind one plugin entry
point. It keeps the specialist skills for each Lark product area while exposing
`@lark` as the normal way to start.

## What Is Bundled

- Calendar, tasks, contacts, IM, mail, approvals, attendance, OKR
- Docs, Drive, Wiki, Markdown, Sheets, Base
- Meetings, VC, Minutes, Slides, Whiteboard, Apps, Events
- Shared setup, auth, permission, and raw OpenAPI exploration guidance

## Required External Dependency

This plugin contains the agent skills, but it does not bundle the `lark-cli`
binary or a Lark developer app credential. A new user still needs:

1. Node.js / npm available.
2. `lark-cli` installed:
   ```bash
   npx @larksuite/cli@latest install
   ```
3. Lark app configuration:
   ```bash
   lark-cli config init --new
   ```
4. User authorization for the scopes they want to use.
5. A health check:
   ```bash
   lark-cli doctor
   ```

After that, `@lark` can route requests to the bundled skills.
