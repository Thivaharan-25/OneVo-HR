# Current Focus: ONEVO Build Packs

**Team size:** 8 developers
**Build model:** 4 backend developers + 4 frontend developers
**ADE rule:** when a developer asks to continue their work, open that developer's canonical file and start from the first unchecked item.

---

## Canonical Developer Files

Use these files as the active source of truth:

| Developer | Track | Canonical File | Owns |
|---|---|---|---|
| Dev 1 | Backend | [[current-focus/DEV1|DEV1]] | Platform foundation, auth/RBAC, tenant context, audit, Developer Platform Admin API |
| Dev 2 | Backend | [[current-focus/DEV2|DEV2]] | HR core, leave, calendar, workforce presence, notifications |
| Dev 3 | Backend | [[current-focus/DEV3|DEV3]] | WorkSync backend, chat, Chat AI, IDE backend APIs, tag execution |
| Dev 4 | Backend | [[current-focus/DEV4|DEV4]] | Monitoring agent, Agent Gateway, activity ingestion, IDE install jobs, agent version rollout |
| Dev 5 | Frontend | [[current-focus/DEV5|DEV5]] | Main app foundation, auth UI, shared components, standalone Developer Platform console |
| Dev 6 | Frontend | [[current-focus/DEV6|DEV6]] | HR, leave, calendar, presence, agent management UI |
| Dev 7 | Frontend | [[current-focus/DEV7|DEV7]] | WorkSync web UI, projects, tasks, boards, docs, time, analytics |
| Dev 8 | Frontend | [[current-focus/DEV8|DEV8]] | VS Code IDE extension |

Only these eight developer files are active in this folder. Supporting architecture, schema, module, and userflow references live outside `current-focus`.

---

## ADE Start Protocol

When a developer says "build my unfinished task" or "continue Dev N":

1. Open `current-focus/DEVN.md`.
2. Read the **Current Unfinished Task** section.
3. Check the **Blocked By** line.
4. Read only the linked wiki references needed for that task.
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

## Developer Platform Ownership

The Developer Platform is a standalone internal control plane. It is not part of the main customer frontend and is not part of the IDE extension.

| Layer | Owner | Scope | Required Wiki References |
|---|---|---|---|
| Admin API host | Dev 1 | `ONEVO.Admin.Api`, `/admin/v1/*`, platform-admin auth, issuer isolation | [[developer-platform/system-design|Developer Platform System Design]], [[developer-platform/backend/admin-api-layer|Admin API Layer]] |
| DevPlatform backend feature | Dev 1 | `dev_platform_accounts`, `dev_platform_sessions`, admin auth/session CQRS | [[modules/dev-platform/overview|Dev Platform Feature]], [[developer-platform/database/schema|Developer Platform Schema]] |
| Tenant Console backend | Dev 1 | tenant list/detail/status/provisioning/subscription/impersonation APIs | [[developer-platform/modules/tenant-console/overview|Tenant Console]], [[developer-platform/userflow/provisioning-flow|Provisioning Flow]] |
| Feature Flag backend | Dev 1 | global flags, per-tenant overrides, module toggles | [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]], [[developer-platform/userflow/feature-flags|Feature Flag Flows]] |
| Audit/System/App Catalog backend | Dev 1 | cross-tenant audit query, global config, catalog management contracts | [[developer-platform/modules/audit-console/overview|Audit Console]], [[developer-platform/modules/system-config/overview|System Config]], [[developer-platform/modules/app-catalog-manager/overview|App Catalog Manager]] |
| Agent release backend | Dev 4 | agent versions, deployment rings, tenant ring assignments, force-update dispatch via Agent Gateway | [[developer-platform/modules/agent-version-manager/overview|Agent Version Manager]], [[developer-platform/userflow/agent-versions|Agent Version Flows]] |
| Dev Console frontend | Dev 5 | standalone Next.js console at `console.onevo.io` | [[developer-platform/frontend/overview|Developer Platform Frontend]], [[developer-platform/frontend/app-structure|Developer Platform App Structure]] |

Required boundary:

- `ONEVO.Admin.Api` is a separate host inside `ONEVO.sln`, not a separate microservice.
- Admin data access goes through module interfaces. Admin controllers must not bypass feature modules.
- Platform-admin JWTs are rejected at `/api/v1/*`.
- Tenant JWTs are rejected at `/admin/v1/*`.
- DevPlatform entities have no `TenantId` and are excluded from tenant query filters.

---

## Cross-Team Contracts

| Contract | Backend Owner | Frontend Consumer |
|---|---|---|
| Auth session + refresh | Dev 1 | Dev 5, Dev 8 |
| Permissions and module entitlements | Dev 1 | Dev 5, Dev 6, Dev 7, Dev 8 |
| Developer Platform Admin API `/admin/v1/*` | Dev 1 | Dev 5 |
| Platform-admin JWT exchange | Dev 1 | Dev 5 |
| Tenant provisioning/admin DTOs | Dev 1 | Dev 5 |
| Feature flag/admin config DTOs | Dev 1 | Dev 5 |
| App catalog admin DTOs | Dev 1 | Dev 5 |
| HR employee/leave/calendar APIs | Dev 2 | Dev 6, Dev 8 |
| Presence and time APIs | Dev 2 | Dev 6, Dev 8 |
| WorkSync project/task/board APIs | Dev 3 | Dev 7, Dev 8 |
| Chat APIs and SignalR events | Dev 3 | Dev 7, Dev 8 |
| IDE entitlements and tag execution | Dev 3 | Dev 8 |
| Agent install request/status APIs | Dev 4 | Dev 8 |
| Agent health and activity APIs | Dev 4 | Dev 6 |
| Agent version release/ring DTOs | Dev 4 | Dev 5 |

---

## Backend Module Reference Map

Use these module folders when implementing backend tasks:

| Area | Backend Feature Folder | Wiki References |
|---|---|---|
| Auth | `Features/Auth` | [[modules/auth/overview|Auth]], [[security/auth-architecture|Auth Architecture]] |
| Infrastructure | `Features/InfrastructureModule` | [[modules/infrastructure/overview|Infrastructure]], [[backend/shared-kernel|Shared Kernel]] |
| Shared Platform | `Features/SharedPlatform` | [[modules/shared-platform/overview|Shared Platform]] |
| Configuration | `Features/Configuration` | [[modules/configuration/overview|Configuration]] |
| Core HR | `Features/CoreHR` | [[modules/core-hr/overview|Core HR]] |
| Leave | `Features/Leave` | [[modules/leave/overview|Leave]] |
| Calendar | `Features/Calendar` | [[modules/calendar/overview|Calendar]] |
| Workforce Presence | `Features/WorkforcePresence` | [[modules/workforce-presence/overview|Workforce Presence]] |
| Notifications | `Features/Notifications` | [[modules/notifications/overview|Notifications]] |
| WorkSync Foundation | `Features/WorkSync/Foundation` | [[modules/work-management/foundation/overview|WorkSync Foundation]] |
| WorkSync Tasks | `Features/WorkSync/TaskManagement` | [[modules/work-management/tasks/overview|Tasks]] |
| WorkSync Planning | `Features/WorkSync/SprintPlanning` | [[modules/work-management/planning/overview|Planning]] |
| WorkSync Chat | `Features/WorkSync/Chat` | [[modules/work-management/chat/overview|Chat]] |
| WorkSync Chat AI | `Features/WorkSync/ChatAI` | [[modules/work-management/chat-ai/overview|Chat AI]] |
| WorkSync Collaboration | `Features/WorkSync/Collaboration` | [[modules/work-management/collaboration/overview|Collaboration]] |
| IDE Extension | `Features/IDEExtension` | [[modules/ide-extension/overview|IDE Extension]] |
| Agent Gateway | `Features/AgentGateway` | [[modules/agent-gateway/overview|Agent Gateway]] |
| Activity Monitoring | `Features/ActivityMonitoring` | [[modules/activity-monitoring/overview|Activity Monitoring]] |
| Dev Platform | `Features/DevPlatform` served by `ONEVO.Admin.Api` | [[modules/dev-platform/overview|Dev Platform]], [[developer-platform/backend/admin-api-layer|Admin API Layer]] |

---

## In-Scope Module Assignment Matrix

This matrix is the coverage check. If ADE is asked to build an unfinished task, every module below must map back to one canonical developer file.

| Module / Feature | Backend Owner | Frontend Owner | Canonical Build Pack |
|---|---|---|---|
| Infrastructure | Dev 1 | Dev 5 | [[current-focus/DEV1|DEV1]], [[current-focus/DEV5|DEV5]] |
| Auth & Security | Dev 1 | Dev 5 | [[current-focus/DEV1|DEV1]], [[current-focus/DEV5|DEV5]] |
| Shared Platform: SSO, billing, feature flags, workflow engine, notification infrastructure, compliance, hardware terminals, real-time integrations | Dev 1 | Dev 6 | [[current-focus/DEV1|DEV1]], [[current-focus/DEV6|DEV6]] |
| Configuration: tenant settings, monitoring toggles, employee overrides, app allowlist, integrations, retention | Dev 1 | Dev 6 | [[current-focus/DEV1|DEV1]], [[current-focus/DEV6|DEV6]] |
| Developer Platform Admin API | Dev 1 | Dev 5 | [[current-focus/DEV1|DEV1]], [[current-focus/DEV5|DEV5]] |
| Org Structure | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]], [[current-focus/DEV6|DEV6]] |
| Core HR + Employee Lifecycle | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]], [[current-focus/DEV6|DEV6]] |
| Skills Core | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]], [[current-focus/DEV6|DEV6]] |
| HR Import / Data Import | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]], [[current-focus/DEV6|DEV6]] |
| Leave + Calendar, country holidays, Google/Outlook calendar sync | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]], [[current-focus/DEV6|DEV6]] |
| Workforce Presence | Dev 2 | Dev 6 | [[current-focus/DEV2|DEV2]], [[current-focus/DEV6|DEV6]] |
| Notifications | Dev 2 | Dev 6, Dev 8 | [[current-focus/DEV2|DEV2]], [[current-focus/DEV6|DEV6]], [[current-focus/DEV8|DEV8]] |
| WorkSync Foundation, Projects, Tasks, Boards, Planning, OKR, Time, Resources | Dev 3 | Dev 7, Dev 8 | [[current-focus/DEV3|DEV3]], [[current-focus/DEV7|DEV7]], [[current-focus/DEV8|DEV8]] |
| WorkSync Chat + Chat AI | Dev 3 | Dev 7, Dev 8 | [[current-focus/DEV3|DEV3]], [[current-focus/DEV7|DEV7]], [[current-focus/DEV8|DEV8]] |
| WorkSync Collaboration, Docs/Wiki, Integrations, Analytics | Dev 3 | Dev 7, Dev 8 | [[current-focus/DEV3|DEV3]], [[current-focus/DEV7|DEV7]], [[current-focus/DEV8|DEV8]] |
| IDE Extension backend APIs | Dev 3 | Dev 8 | [[current-focus/DEV3|DEV3]], [[current-focus/DEV8|DEV8]] |
| Agent Gateway + Windows monitoring agent | Dev 4 | Dev 6, Dev 8 | [[current-focus/DEV4|DEV4]], [[current-focus/DEV6|DEV6]], [[current-focus/DEV8|DEV8]] |
| Activity Monitoring | Dev 4 | Dev 6 | [[current-focus/DEV4|DEV4]], [[current-focus/DEV6|DEV6]] |
| Identity Verification + Biometric Device Backend | Dev 4 | Dev 6 | [[current-focus/DEV4|DEV4]], [[current-focus/DEV6|DEV6]] |
| Exception Engine | Dev 4 | Dev 6 | [[current-focus/DEV4|DEV4]], [[current-focus/DEV6|DEV6]] |
| Discrepancy Engine | Dev 4 | Dev 6, Dev 7 | [[current-focus/DEV4|DEV4]], [[current-focus/DEV6|DEV6]], [[current-focus/DEV7|DEV7]] |
| Productivity Analytics | Dev 4 | Dev 6, Dev 7 | [[current-focus/DEV4|DEV4]], [[current-focus/DEV6|DEV6]], [[current-focus/DEV7|DEV7]] |
| Agent Version Manager backend | Dev 4 | Dev 5 | [[current-focus/DEV4|DEV4]], [[current-focus/DEV5|DEV5]] |

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
