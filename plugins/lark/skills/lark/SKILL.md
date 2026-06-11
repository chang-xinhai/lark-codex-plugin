---
name: lark
description: Use when the user mentions @lark, @plugin, Lark, Feishu, 飞书, or asks for broad workspace help that may involve multiple Lark/Feishu surfaces. Route to the bundled specialist skills for calendar, docs, drive, wiki, base, sheets, IM, mail, tasks, VC/minutes, approvals, OKR, attendance, slides, whiteboard, apps, events, contacts, or raw OpenAPI exploration.
---

# Lark / Feishu Plugin Router

This is the plugin front door. Use it to choose the smallest set of bundled
specialist skills needed for the user's request.

## Routing Map

- Setup, identity, auth, permissions, CLI updates: `lark-shared`
- Calendar, events, meeting rooms, scheduling: `lark-calendar`
- Contacts and resolving people to user IDs: `lark-contact`
- Instant messages, group chats, files in chats, reactions: `lark-im`
- Mail search, triage, drafts, replies, sending: `lark-mail`
- Tasks, task lists, subtasks, comments, assignment: `lark-task`
- Docs, wiki docs, document content, embedded document tokens: `lark-doc`
- Drive files, folders, permissions, comments, import/export: `lark-drive`
- Wiki spaces and node organization: `lark-wiki`
- Native Markdown files in Drive: `lark-markdown`
- Sheets, workbooks, formulas, charts, pivots, formatting: `lark-sheets`
- Base or bitable tables, fields, records, views, forms, dashboards, workflow: `lark-base`
- Slides and presentation page edits: `lark-slides`
- Whiteboards and visual structure updates: `lark-whiteboard`
- Meeting history, notes, transcripts, participants: `lark-vc`
- Live meeting join/leave and live meeting events: `lark-vc-agent`
- Minutes search, upload, downloads, speaker replacement: `lark-minutes`
- Approval tasks and approval instances: `lark-approval`
- Attendance records: `lark-attendance`
- OKR cycles, objectives, key results, progress: `lark-okr`
- Realtime events and subscriptions: `lark-event`
- Spark/Miaoda app creation, local dev, publish, deployment: `lark-apps`
- Custom lark-cli skill creation: `lark-skill-maker`
- Raw OpenAPI discovery when no wrapped skill fits: `lark-openapi-explorer`
- Meeting-summary workflow: `lark-workflow-meeting-summary`
- Standup report workflow: `lark-workflow-standup-report`

## Operating Rules

- First-run preflight:
  1. Check `command -v lark-cli`.
  2. If missing, install the CLI with the official npm installer: `npx @larksuite/cli@latest install`.
  3. Run `lark-cli doctor` after installation.
  4. If app config is missing, use `lark-shared` and start `lark-cli config init --new`.
  5. If user auth is missing, use `lark-shared` split-flow auth.
  6. Do not ask the user to install separate `lark-*` skills when this plugin is already installed; they are bundled here.
- Prefer read-only actions for first contact unless the user clearly asks to create, update, send, or delete.
- For writes, confirm the intended target and content before acting when the request is ambiguous or high impact.
- Use `lark-shared` whenever authentication, identity, scope, `_notice`, or permission errors appear.
- Keep bot and user identity boundaries explicit: user resources normally require user identity.
- When a specialist skill has a referenced file, read only the sections needed for the current request.
