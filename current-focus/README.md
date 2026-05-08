# Current Focus: ONEVO Build Packs

**Team size:** 8 developers
**Build model:** 4 backend developers + 4 frontend developers
**ADE rule:** when a developer asks to continue their work, open that developer's canonical file and start from the first unchecked item.

---

## Canonical Developer Files

Use these files as the active source of truth:

| Developer | Track | Canonical File | Owns |
|---|---|---|---|
| Dev 1 | Backend | [[current-focus/DEV1|DEV1]] (current-focus/DEV1.md) | Platform foundation, auth/RBAC, tenant context, audit, Developer Platform Admin API |
| Dev 2 | Backend | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md) | HR core, leave, calendar, workforce presence, notifications |
| Dev 3 | Backend | [[current-focus/DEV3|DEV3]] (current-focus/DEV3.md) | WorkSync backend, chat, Chat AI, IDE backend APIs, tag execution |
| Dev 4 | Backend | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md) | Monitoring agent, Agent Gateway, activity ingestion, IDE install jobs, agent version rollout |
| Dev 5 | Frontend | [[current-focus/DEV5|DEV5]] (current-focus/DEV5.md) | Main app foundation, auth UI, shared components, standalone Developer Platform console |
| Dev 6 | Frontend | [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) | HR, leave, calendar, presence, agent management UI |
| Dev 7 | Frontend | [[current-focus/DEV7|DEV7]] (current-focus/DEV7.md) | WorkSync web UI, projects, tasks, boards, docs, time, analytics |
| Dev 8 | Frontend | [[current-focus/DEV8|DEV8]] (current-focus/DEV8.md) | VS Code IDE extension |

Only these eight developer files are active in this folder. Supporting architecture, schema, module, and userflow references live outside `current-focus`.

---

## ADE Start Protocol

When a developer says "build my unfinished task" or "continue Dev N":

1. Open `current-focus/DEVN.md`.
2. Read the **Current Unfinished Task** section.
3. Check the **Blocked By** line.
4. Read only the linked wiki references needed for that task.
   > **Wikilink resolution:** `[[path/to/file|Display]]` -> `path/to/file.md` from repo root. Strip the display alias and append `.md` to navigate directly.
5. Implement the first unchecked acceptance criteria.
6. Run the task's verification commands.
7. Update checkbox status in the same `DEVN.md` file.
8. Stop only when the task is complete, blocked, or verification exposes a real issue.

If a dependency is missing, build the smallest mock or contract stub needed for local progress, then record it under **Open Backend Contracts** or **Open Frontend Contracts** in that developer file.

---

## Ownership Rules

- Backend Devs 1-4 own server code, database schema, permissions, SignalR contracts, background jobs, and the Windows monitoring agent.
- Frontend Devs 5-8 own web UI and the VS Code IDE extension.
- Dev 4 owns the monitoring agent lifecycle: installer, TrayApp enrollment, device credential, policy, telemetry, health, ingestion, and rollout rings.
- Dev 8 owns the IDE extension UX. The extension can request an agent install job, but backend entitlement and the monitoring agent own enrollment.
- Authorization is always backend-enforced. Frontend and IDE clients only hide/show actions based on backend responses.
- Every IDE tag execution attempt must be logged server-side.

---

## Foundation Owners Rule

Two developers own the shared foundation files. All others build on top — they do not directly modify foundation files. If a change is needed, raise it with the owner who adds the extension point.

| Owner | Track | Protected areas |
|---|---|---|
| **Dev 1** | Backend | Auth/RBAC core, `ITenantContext`, `BaseRepository<T>`, `ApplicationDbContext` boot config, shared middleware pipeline, workflow engine internals |
| **Dev 5** | Frontend | App shell, sidebar, `router.tsx`, global provider stack, shared UI primitives, TanStack Query defaults, Zustand store structure, API client base |

**Why this matters:** these files are touched by every developer indirectly. Without ownership enforcement, merge conflicts on shared kernel and shell layout become the most common blocker in the first two weeks.

---

## Developer Platform Ownership

The Developer Platform is a standalone internal control plane. It is not part of the main customer frontend and is not part of the IDE extension.

| Layer | Owner | Scope | Required Wiki References |
|---|---|---|---|
| Admin API surface | Dev 1 | `ONEVO.Api` `/admin/v1/*`, platform-admin auth, issuer isolation | [[developer-platform/system-design|Developer Platform System Design]] (developer-platform/system-design.md), [[developer-platform/backend/admin-api-layer|Admin API Layer]] (developer-platform/backend/admin-api-layer.md) |
| DevPlatform backend feature | Dev 1 | `dev_platform_accounts`, `dev_platform_sessions`, admin auth/session CQRS | [[modules/dev-platform/overview|Dev Platform Feature]] (modules/dev-platform/overview.md), [[developer-platform/database/schema|Developer Platform Schema]] (developer-platform/database/schema.md) |
| Tenant Console backend | Dev 1 | tenant list/detail/status/provisioning/subscription/impersonation APIs | [[developer-platform/modules/tenant-console/overview|Tenant Console]] (developer-platform/modules/tenant-console/overview.md), [[developer-platform/userflow/provisioning-flow|Provisioning Flow]] (developer-platform/userflow/provisioning-flow.md) |
| Role Template backend | Dev 1 | module-filtered permission catalog, operator-managed role templates, tenant role materialization | [[developer-platform/modules/role-template-manager|Role Template Manager]] (developer-platform/modules/role-template-manager.md), [[modules/auth/overview|Auth]] (modules/auth/overview.md), [[Userflow/Auth-Access/role-creation|Role Creation]] (Userflow/Auth-Access/role-creation.md) |
| Feature Flag backend | Dev 1 | global flags, per-tenant overrides, module toggles | [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]] (developer-platform/modules/feature-flag-manager/overview.md), [[developer-platform/userflow/feature-flags|Feature Flag Flows]] (developer-platform/userflow/feature-flags.md) |
| Audit/System/App Catalog backend | Dev 1 | cross-tenant audit query, global config, catalog management contracts | [[developer-platform/modules/audit-console/overview|Audit Console]] (developer-platform/modules/audit-console/overview.md), [[developer-platform/modules/system-config/overview|System Config]] (developer-platform/modules/system-config/overview.md), [[developer-platform/modules/app-catalog-manager/overview|App Catalog Manager]] (developer-platform/modules/app-catalog-manager/overview.md) |
| Agent release backend | Dev 4 | agent versions, deployment rings, tenant ring assignments, force-update dispatch via Agent Gateway | [[developer-platform/modules/agent-version-manager/overview|Agent Version Manager]] (developer-platform/modules/agent-version-manager/overview.md), [[developer-platform/userflow/agent-versions|Agent Version Flows]] (developer-platform/userflow/agent-versions.md) |
| Dev Console frontend | Dev 5 | standalone Next.js console at `console.onevo.io` | [[developer-platform/frontend/overview|Developer Platform Frontend]] (developer-platform/frontend/overview.md), [[developer-platform/frontend/app-structure|Developer Platform App Structure]] (developer-platform/frontend/app-structure.md) |

Required boundary:

- `ONEVO.Api` is the only backend host deployed in Phase 1. `/admin/v1/*` is a logically separated admin API surface inside that host, not a second deployment.
- Admin data access goes through module interfaces. Admin controllers must not bypass feature modules.
- Platform-admin JWTs are rejected at `/api/v1/*`.
- Tenant JWTs are rejected at `/admin/v1/*`.
- DevPlatform entities have no `TenantId` and are excluded from tenant query filters.

---

## Cross-Team Contracts

| Contract | Backend Owner | Frontend Consumer | Contract File |
|---|---|---|---|
| Auth session + refresh | Dev 1 | Dev 5, Dev 8 | `contracts/auth-session.md` |
| Permissions and module entitlements | Dev 1 | Dev 5, Dev 6, Dev 7, Dev 8 | `contracts/auth-session.md` |
| Developer Platform Admin API `/admin/v1/*` | Dev 1 | Dev 5 | `contracts/admin-api.md` |
| Platform-admin JWT exchange | Dev 1 | Dev 5 | `contracts/admin-api.md` |
| Tenant provisioning/admin DTOs | Dev 1 | Dev 5 | `contracts/admin-api.md` |
| Role template/admin permission catalog DTOs | Dev 1 | Dev 5 | `contracts/admin-api.md` |
| Feature flag/admin config DTOs | Dev 1 | Dev 5 | `contracts/admin-api.md` |
| App catalog admin DTOs | Dev 1 | Dev 5 | `contracts/admin-api.md` |
| HR employee/leave/calendar APIs | Dev 2 | Dev 6, Dev 8 | `contracts/hr-employee.md` |
| Presence and time APIs | Dev 2 | Dev 6, Dev 8 | `contracts/workforce-presence.md` |
| WorkSync project/task/board APIs | Dev 3 | Dev 7, Dev 8 | `contracts/worksync-core.md` |
| Chat APIs and SignalR events | Dev 3 | Dev 7, Dev 8 | `contracts/signalr-events.md` |
| IDE entitlements and tag execution | Dev 3 | Dev 8 | `contracts/ide-entitlements.md` |
| Agent install request/status APIs | Dev 4 | Dev 8 | `contracts/agent-gateway.md` |
| Agent health and activity APIs | Dev 4 | Dev 6 | `contracts/agent-gateway.md` |
| Agent version release/ring DTOs | Dev 4 | Dev 5 | `contracts/admin-api.md` |

---

## Parallel Execution Schedule

Tasks do not flow in a single line across all 8 developers. Use this schedule to maximise simultaneous progress. Rows with the same window run at the same time.

| Window | Dev | Task | Note |
|---|---|---|---|
| **Day 0** | Dev 1 | DEV1.T0 — Backend CQRS Folder Structure Cleanup | First Dev 1 task; must run before all other backend foundation/Auth work |
| **After DEV1.T0** | Dev 1 | DEV1.T1 — Backend Foundation | Critical path start after structure cleanup |
| **Day 0** | Dev 5 | DEV5.T1 — Vite App Foundation | No backend dependency |
| **Day 0** | Dev 8 | DEV8.T1 — Extension Foundation | MSW stubs; no backend dependency |
| **After DEV1.T1** | Dev 1 | DEV1.T2 — Auth + RBAC | Sequential on T1 |
| **After DEV1.T1** | Dev 2 | DEV2.T1 — Org Structure + Core HR | Parallel with DEV1.T2 |
| **After DEV1.T1** | Dev 4 | **DEV1.T4 — Audit Foundation (pickup)** | Dev 4 is idle waiting for T2; T4 only needs T1 |
| **After DEV5.T1** | Dev 5 | DEV5.T2 — API Client + State Layer | Sequential |
| **After DEV1.T2 + T4** | Dev 1 | DEV1.T3 — Tenant + Entitlement | Dev 1 critical chain; T4 done by Dev 4 |
| **After DEV1.T2 + T4** | **Dev 3 (pickup)** | **DEV1.T7 — Dev Platform Admin API** | Dev 3 is idle (blocked until T3); T7 only needs T1+T2+T4 |
| **After DEV1.T2** | Dev 4 | DEV4.T1 — Agent Gateway Enrollment | Now unblocked (needed T1+T2) |
| **After DEV5.T2** | Dev 5 | DEV5.T3 + DEV5.T4 — Auth Screens + Shared Components | **Parallel pair** |
| **After DEV1.T3** | Dev 3 | DEV3.T1 — WorkSync Foundation | Now unblocked (may still be finishing T7 — fine to wrap) |
| **After DEV5.T1–T4** | Dev 6 | DEV6.T1 — HR Employee Screens | First gating task |
| **After DEV5.T1–T4** | Dev 7 | DEV7.T1 — WorkSync Shell + Projects | First gating task |
| **After DEV8.T1** | Dev 8 | DEV8.T2 + T3 + T4 + T5 | **All four parallel** |
| **After DEV2.T1** | Dev 2 | DEV2.T2 + T3 + T4 + T5 | **All four parallel** |
| **After DEV3.T1** | Dev 3 | DEV3.T2 + T3 + T5 (parallel); T4 after T2+T3 | T2/T3/T5 parallel; T4 gates on T2+T3 |
| **After DEV4.T1** | Dev 4 | DEV4.T2 — Monitoring Agent Client | Sequential |
| **After DEV4.T3** | Dev 4 | DEV4.T4 + T5 — Identity Verification + Exception Engine | **Parallel pair** |
| **After DEV6.T1** | Dev 6 | DEV6.T2 + T3 + T4 | **All three parallel** |
| **After DEV7.T1** | Dev 7 | DEV7.T2 + T3 + T4 | **All three parallel** |
| **After DEV5.T5** | Dev 5 | DEV5.T6 + T7 — Dev Platform Console UIs | **Parallel pair** |
| **After DEV1.T3+T5+T7** | Dev 2 (overflow) | DEV1.T8 — Tenant Console Backend | Dev 2 picks up after their track is done |
| **After DEV1.T4+T5+T7** | Dev 3 (overflow) | DEV1.T9 — Dev Platform Operations Backend | Dev 3 picks up after their track is done |

**Dev 1 critical chain (irreducible):** T0 → T1 → T2 → T3 → T5 → T6. Everything else flows around it.

---

## Integration Checkpoints

Explicit team sync moments. At each checkpoint the named developers confirm the contract is live and consuming devs switch from MSW stubs to real endpoints. Missing a checkpoint is a team call decision, not a solo one.

| Checkpoint | Trigger | Who syncs | What switches |
|---|---|---|---|
| **CP1** | DEV1.T2 complete | Dev 1 + Dev 4 + Dev 5 | Auth contracts live. Dev 4 starts DEV4.T1. Dev 5 wires real auth into DEV5.T3. |
| **CP2** | DEV5.T2 complete | Dev 5 + Dev 6 + Dev 7 | Frontend API client live. Dev 6 and Dev 7 build screens against real client shape. |
| **CP3** | DEV1.T3 + DEV2.T1 complete | Dev 1 + Dev 2 + Dev 6 | Tenant entitlement and Core HR live. Dev 6 switches HR screens from MSW to real APIs. |
| **CP4** | DEV3.T1 complete | Dev 3 + Dev 7 | WorkSync foundation live. Dev 7 switches from MSW to real DEV3 endpoints. |
| **CP5** | DEV4.T1 complete | Dev 4 + Dev 6 + Dev 8 | Agent contracts live. Dev 6 agent UI and Dev 8 install flow switch from MSW. |
| **CP6** | DEV1.T5 complete | Dev 1 + Dev 2 | Workflow engine live. Dev 2 finishes leave approval and notifications wiring. |
| **CP7** | DEV3.T4 complete | Dev 3 + Dev 8 | IDE backend APIs live. Dev 8 switches tag engine and context panels from MSW. |

---

## Backend Module Reference Map

Use these module folders when implementing backend tasks:

| Area | Backend Feature Folder | Wiki References |
|---|---|---|
| Auth | `Features/Auth` | [[modules/auth/overview|Auth]] (modules/auth/overview.md), [[security/auth-architecture|Auth Architecture]] (security/auth-architecture.md) |
| Infrastructure | `Features/InfrastructureModule` | [[modules/infrastructure/overview|Infrastructure]] (modules/infrastructure/overview.md), [[backend/shared-kernel|Shared Kernel]] (backend/shared-kernel.md) |
| Shared Platform | `Features/SharedPlatform` | [[modules/shared-platform/overview|Shared Platform]] (modules/shared-platform/overview.md) |
| Configuration | `Features/Configuration` | [[modules/configuration/overview|Configuration]] (modules/configuration/overview.md) |
| Core HR | `Features/CoreHR` | [[modules/core-hr/overview|Core HR]] (modules/core-hr/overview.md) |
| Leave | `Features/Leave` | [[modules/leave/overview|Leave]] (modules/leave/overview.md) |
| Calendar | `Features/Calendar` | [[modules/calendar/overview|Calendar]] (modules/calendar/overview.md) |
| Workforce Presence | `Features/WorkforcePresence` | [[modules/workforce-presence/overview|Workforce Presence]] (modules/workforce-presence/overview.md) |
| Notifications | `Features/Notifications` | [[modules/notifications/overview|Notifications]] (modules/notifications/overview.md) |
| WorkSync Foundation | `Features/WorkSync/Foundation` | [[modules/work-management/foundation/overview|WorkSync Foundation]] (modules/work-management/foundation/overview.md) |
| WorkSync Tasks | `Features/WorkSync/TaskManagement` | [[modules/work-management/tasks/overview|Tasks]] (modules/work-management/tasks/overview.md) |
| WorkSync Planning | `Features/WorkSync/SprintPlanning` | [[modules/work-management/planning/overview|Planning]] (modules/work-management/planning/overview.md) |
| WorkSync Chat | `Features/WorkSync/Chat` | [[modules/work-management/chat/overview|Chat]] (modules/work-management/chat/overview.md) |
| WorkSync Chat AI | `Features/WorkSync/ChatAI` | [[modules/work-management/chat-ai/overview|Chat AI]] (modules/work-management/chat-ai/overview.md) |
| WorkSync Collaboration | `Features/WorkSync/Collaboration` | [[modules/work-management/collaboration/overview|Collaboration]] (modules/work-management/collaboration/overview.md) |
| IDE Extension | `Features/IDEExtension` | [[modules/ide-extension/overview|IDE Extension]] (modules/ide-extension/overview.md) |
| Agent Gateway | `Features/AgentGateway` | [[modules/agent-gateway/overview|Agent Gateway]] (modules/agent-gateway/overview.md) |
| Activity Monitoring | `Features/ActivityMonitoring` | [[modules/activity-monitoring/overview|Activity Monitoring]] (modules/activity-monitoring/overview.md) |
| Dev Platform | `Features/DevPlatform` served by `ONEVO.Api` `/admin/v1/*` | [[modules/dev-platform/overview|Dev Platform]] (modules/dev-platform/overview.md), [[developer-platform/backend/admin-api-layer|Admin API Layer]] (developer-platform/backend/admin-api-layer.md) |

---

## In-Scope Module Assignment Matrix

This matrix is the coverage check. If ADE is asked to build an unfinished task, every module below must map back to one canonical developer file.

| Module / Feature | Backend Owner | Frontend Owner | Canonical Build Pack |
|---|---|---|---|
| Infrastructure | Dev 1 | Dev 5 | [[current-focus/DEV1|DEV1]] (current-focus/DEV1.md), [[current-focus/DEV5|DEV5]] (current-focus/DEV5.md) |
| Auth & Security | Dev 1 | Dev 5 | [[current-focus/DEV1|DEV1]] (current-focus/DEV1.md), [[current-focus/DEV5|DEV5]] (current-focus/DEV5.md) |
| Shared Platform: SSO, billing, feature flags, workflow engine, notification infrastructure, compliance, hardware terminals, real-time integrations | Dev 1 | Dev 6 *(Phase 2 frontend) | [[current-focus/DEV1|DEV1]] (current-focus/DEV1.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Configuration: tenant settings, monitoring toggles, employee overrides, app allowlist, integrations, retention | Dev 1 | Dev 6 (monitoring toggles only in Phase 1 - see DEV6 Task 3) | [[current-focus/DEV1|DEV1]] (current-focus/DEV1.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Developer Platform Admin API | Dev 1 | Dev 5 | [[current-focus/DEV1|DEV1]] (current-focus/DEV1.md), [[current-focus/DEV5|DEV5]] (current-focus/DEV5.md) |
| Org Structure | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Core HR + Employee Lifecycle | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Skills Core | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| HR Import / Data Import | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Leave + Calendar, country holidays, Google/Outlook calendar sync | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Workforce Presence | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Notifications | Dev 2 | Dev 6, Dev 8 | [[current-focus/DEV2|DEV2]] (current-focus/DEV2.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md), [[current-focus/DEV8|DEV8]] (current-focus/DEV8.md) |
| WorkSync Foundation, Projects, Tasks, Boards, Planning, OKR, Time, Resources | Dev 3 | Dev 7, Dev 8 | [[current-focus/DEV3|DEV3]] (current-focus/DEV3.md), [[current-focus/DEV7|DEV7]] (current-focus/DEV7.md), [[current-focus/DEV8|DEV8]] (current-focus/DEV8.md) |
| WorkSync Chat + Chat AI | Dev 3 | Dev 7, Dev 8 | [[current-focus/DEV3|DEV3]] (current-focus/DEV3.md), [[current-focus/DEV7|DEV7]] (current-focus/DEV7.md), [[current-focus/DEV8|DEV8]] (current-focus/DEV8.md) |
| WorkSync Collaboration, Docs/Wiki, Integrations, Analytics | Dev 3 | Dev 7, Dev 8 | [[current-focus/DEV3|DEV3]] (current-focus/DEV3.md), [[current-focus/DEV7|DEV7]] (current-focus/DEV7.md), [[current-focus/DEV8|DEV8]] (current-focus/DEV8.md) |
| IDE Extension backend APIs | Dev 3 | Dev 8 | [[current-focus/DEV3|DEV3]] (current-focus/DEV3.md), [[current-focus/DEV8|DEV8]] (current-focus/DEV8.md) |
| Agent Gateway + Windows monitoring agent | Dev 4 | Dev 6, Dev 8 | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md), [[current-focus/DEV8|DEV8]] (current-focus/DEV8.md) |
| Activity Monitoring | Dev 4 | Dev 6 | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Identity Verification + Biometric Device Backend | Dev 4 | Dev 6 *(Phase 2 frontend) | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Exception Engine | Dev 4 | Dev 6 *(Phase 2 frontend) | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md) |
| Discrepancy Engine | Dev 4 | Dev 6, Dev 7 *(Phase 2 frontend) | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md), [[current-focus/DEV7|DEV7]] (current-focus/DEV7.md) |
| Productivity Analytics | Dev 4 | Dev 6, Dev 7 *(Phase 2 frontend) | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md), [[current-focus/DEV6|DEV6]] (current-focus/DEV6.md), [[current-focus/DEV7|DEV7]] (current-focus/DEV7.md) |
| Agent Version Manager backend | Dev 4 | Dev 5 | [[current-focus/DEV4|DEV4]] (current-focus/DEV4.md), [[current-focus/DEV5|DEV5]] (current-focus/DEV5.md) |

* Frontend for this module is not in the current build pack. Backend is Phase 1; frontend UI is deferred. ADE should not attempt to build these frontend screens.

---

## Shared Verification Expectations

Backend tasks should usually finish with:

```bash
dotnet test ONEVO.sln
```

Frontend app tasks should usually finish with:

```bash
npm run lint
npm run test
npm run build
```

IDE extension tasks should usually finish with:

```bash
npm run lint
npm run compile
npm test
npm run test:vscode
```

Use the closest available command if the repo has different scripts.


