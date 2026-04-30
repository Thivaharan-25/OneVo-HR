# IDE Extension Structured Context Conflict Review

**Reviewed:** 2026-04-30
**Source of truth reviewed:** `docs/superpowers/plans/2026-04-30-ide-extension.md`, `docs/superpowers/specs/2026-04-30-ide-extension-design.md`, `modules/ide-extension/overview.md`, `onevo-unified-entity-map.md`, `docs/onevo-unified-entity-map-audit-2026-04-29.md`

---

## Verdict

The IDE extension structured context is directionally correct and does not conflict with the unified single-DB architecture. It correctly treats the VS Code extension as a client of the existing backend, gates HR actions through tenant modules and permissions, routes WorkSync chat through the same backend chat, and keeps monitoring-agent ownership with Agent Gateway.

The conflicts found were documentation drift, not architecture conflicts:

1. `database/README.md` still described the old 170-table / 23-module model instead of the current 280-table unified map.
2. `database/schemas/documents.md` still labelled Documents as Phase 2, while WorkSync requires shared Phase 1 document/wiki/task-document behaviour.
3. `modules/ide-extension/overview.md` linked to old/nonexistent Work-Management userflow files instead of the existing `Userflow/IDE-Extension` files.
4. The IDE agent-install flow needed a dedicated userflow aligned to `POST /api/v1/ide/agent-install/request` and Agent Gateway ownership.

These have been corrected or filled in this pass.

---

## Non-Conflicts Confirmed

| Area | Result |
|:--|:--|
| Single database | IDE extension uses unified backend APIs; no separate DB is introduced. |
| HR + WorkSync permissions | Entitlements combine `active_modules[]`, tenant HR permissions, and workspace roles. |
| Structured context | Branch/file/task context is stored in `ide_context_links` and session context, matching the unified entity map. |
| Agent ownership | Extension bootstraps install only; Agent Gateway owns registered agents, install jobs, policy, and health. |
| Chat + NLP | Chat remains WorkSync.Chat; NLP is server-side in WorkSync.ChatAI before message persistence. |

---

## Remaining Watch Items

- The implementation plan names DEV9, while current-focus allocates IDE work across DEV7/DEV8. This is scheduling terminology only, but task ownership should be normalized before assigning work.
- `database/schemas/documents.md` now states shared ownership, but its table listing is still HR-heavy. If the team wants schema files to be fully implementation-ready, split or expand it to mirror the WorkSync collaboration tables in the unified entity map.
- Dedicated schema files for WorkSync OKR, time management, and resource management would reduce lookup friction, even though the unified entity map and module docs already cover the entities.
