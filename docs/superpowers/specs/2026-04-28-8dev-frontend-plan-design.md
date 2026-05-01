# 8-Developer Phase 1 Build Plan

**Date:** 2026-05-01
**Status:** Updated
**Scope:** OneVo backend, monitoring agent, main frontend, and VS Code IDE extension

---

## 1. Team Structure

The team is split into two parallel groups:

| Group | Size | Primary Ownership |
|---|---:|---|
| Backend Team | 4 members | .NET backend, database, APIs, SignalR, monitoring agent, auth, entitlements |
| Frontend Team | 4 members | Vite React app, shared UI, WorkSync/HR screens, VS Code IDE extension |

The backend team owns the monitoring agent and all server-side policy, entitlement, ingestion, and audit logic.

The frontend team owns the web frontend and the VS Code IDE extension experience. The extension must call backend APIs for auth, permissions, tag execution, monitoring entitlement checks, and agent install jobs.

---

## 2. Core Decisions

### Backend
- **Runtime:** .NET 9, C# 13
- **Architecture:** Clean Architecture + CQRS
- **Database:** PostgreSQL with one `ApplicationDbContext`
- **Realtime:** SignalR for web app, IDE extension, and agent status updates
- **Background jobs:** Hangfire where needed
- **Monitoring agent:** Windows desktop agent owned by backend team
- **Authorization:** Backend validates every action; clients only show what the backend permits

### Frontend
- **Main app:** Vite + React 19 + TypeScript
- **Router:** React Router v7
- **Styling:** Tailwind CSS v4 + shadcn/ui + Radix
- **Server state:** TanStack Query v5
- **Client state:** Zustand
- **Realtime:** `@microsoft/signalr`
- **Forms:** React Hook Form + Zod
- **Testing:** Vitest, React Testing Library, Playwright, MSW
- **IDE extension:** VS Code Extension API + TypeScript + webpack

---

## 3. Backend Team Assignments

### Backend Member 1: Platform Foundation + Auth

| Task | Deliverables | Blocks |
|---|---|---|
| Backend foundation | Solution structure, shared kernel, API conventions, OpenAPI, health checks | All backend work |
| Auth + RBAC | Login, MFA, refresh token rotation, password reset, permission keys | All protected APIs |
| Tenant foundation | Tenant provisioning, subscription/module gates, tenant context | Entitlements, app access |
| Audit foundation | Audit log service used by security, agent, and IDE actions | Compliance flows |

### Backend Member 2: HR + Workforce Core

| Task | Deliverables | Blocks |
|---|---|---|
| Core HR | Employees, lifecycle, org structure dependencies | Leave, presence, permissions |
| Leave + calendar | Leave requests, approvals, balances, holidays, shifts | IDE HR tags |
| Workforce presence | Presence sessions, breaks, overtime, schedule links | Monitoring lifecycle |
| Notifications | In-app/email notifications, SignalR notification events | IDE and web alerts |

### Backend Member 3: WorkSync Backend + IDE APIs

| Task | Deliverables | Blocks |
|---|---|---|
| WorkSync foundation | Workspaces, workspace members, roles | Tasks, chat, IDE context |
| Projects/tasks/boards | Projects, tasks, boards, sprints, roadmaps | IDE task panels, context engine |
| Chat + Chat AI | Channels, messages, AI action jobs, undo flow | IDE chat sidebar |
| IDE backend APIs | `/api/v1/ide/*`, tag execution, entitlements, sessions, context links | IDE extension |

### Backend Member 4: Monitoring Agent + Agent Gateway

| Task | Deliverables | Blocks |
|---|---|---|
| Agent Gateway | Agent enrollment, device credentials, policy fetch, heartbeat | Monitoring data flow |
| Windows monitoring agent | Installer, TrayApp login, collectors, local policy handling | Activity monitoring |
| Activity ingestion | Batch ingest, buffering contract, screenshots/process/window events | Analytics |
| IDE agent install jobs | Entitlement check, install job creation, installer metadata, install status | IDE install prompt |

Backend Member 4 owns the monitoring agent. The IDE extension may start the install flow, but it must never own device enrollment, policy decisions, or telemetry collection.

---

## 4. Frontend Team Assignments

### Frontend Member 1: App Foundation + Auth UI

| Task | Deliverables | Blocks |
|---|---|---|
| Vite foundation | TypeScript setup, routing, providers, app shell, layout system | All frontend work |
| API client | Auth interceptor, tenant header, error handling, cursor pagination helpers | All data screens |
| Auth screens | Login, MFA, reset password, forced password change | Protected app flow |
| Shared components | Data table, forms, status badges, permission guard, empty/error states | Feature screens |

### Frontend Member 2: HR + Workforce UI

| Task | Deliverables | Blocks |
|---|---|---|
| HR screens | Employee list/detail/create/edit, onboarding, offboarding | HR workflows |
| Leave/calendar | Leave request/approval/balance, calendar, shifts, holidays | IDE HR parity checks |
| Presence/admin | Live presence, attendance, overtime, monitoring settings | Agent status flows |
| Agent management UI | Agent fleet table, agent detail, policy/status display | Monitoring operations |

### Frontend Member 3: WorkSync Web UI

| Task | Deliverables | Blocks |
|---|---|---|
| WorkSync shell | Workspace switcher, project navigation, member views | WorkSync screens |
| Projects/tasks/boards | Project list/detail, task detail, kanban, backlog, sprint planning | IDE task parity |
| Time/analytics | Time logs, timesheets, reports, productivity cards | IDE time tags |
| Documents/Git UI | Docs/wiki, repo linking, PR/CI status surfaces | IDE context views |

### Frontend Member 4: VS Code IDE Extension

| Task | Deliverables | Blocks |
|---|---|---|
| Extension foundation | Scaffold, activation, auth, SecretStorage, config, API client | All extension work |
| Chat/sidebar | Chat panel, tasks panel, notifications panel, SignalR events | Tag execution UX |
| Tag engine | `@entity:action` parser, picker, autocomplete, undo handling | HR/WMS actions |
| Context engine | Branch-to-task, file-to-task, status bar timer, task detail webview | Time and task tags |
| Agent install prompt | Entitlement check, user consent prompt, installer download/hash verification | Backend install jobs |

Frontend Member 4 owns the IDE extension. The extension must treat the backend as source of truth for permissions, entitlement, tag execution, and monitoring agent installation status.

---

## 5. Delivery Order

### Week 1: Shared Foundation

Backend:
- Platform foundation, shared kernel, auth/RBAC skeleton
- Tenant/module entitlement model
- Agent Gateway contract and first enrollment endpoints
- WorkSync workspace/task/chat data contracts

Frontend:
- Vite foundation, app shell, auth UI
- Shared API client and permission guard
- IDE extension scaffold, activation flow, basic auth shell
- MSW/mock contracts for screens waiting on APIs

### Week 2: Core Product Flows

Backend:
- HR employee, leave, calendar, presence APIs
- WorkSync projects/tasks/boards/chat APIs
- Agent heartbeat, policy fetch, and ingest contracts
- IDE sessions and entitlements endpoint

Frontend:
- HR employee and leave screens
- WorkSync project/task/board screens
- IDE chat panel and tasks panel
- Agent management UI with mock/early API data

### Week 3: Monitoring + IDE Actions

Backend:
- Monitoring agent installer and TrayApp login-based enrollment
- Activity ingestion and processing
- IDE tag execution endpoint with audit logging
- Chat AI action job and undo state machine

Frontend:
- Presence, activity, productivity, and agent fleet screens
- IDE tag picker and autocomplete
- IDE HR/WorkSync tag flows
- IDE task detail and notification panels

### Week 4: Integration + Release Hardening

Backend:
- End-to-end monitoring lifecycle validation
- SignalR event polish across web, IDE, and agent status
- Security and audit review
- Performance smoke testing for ingest and chat/tag execution

Frontend:
- Cross-browser frontend testing
- IDE extension packaging and install testing
- End-to-end user-flow testing
- Accessibility and responsive UI pass

---

## 6. Main Integration Contracts

| Contract | Backend Owner | Frontend Consumer |
|---|---|---|
| `GET /api/v1/ide/entitlements` | Backend Member 3 | IDE extension |
| `POST /api/v1/ide/tags/execute` | Backend Member 3 | IDE extension |
| `GET /api/v1/ide/tasks/assigned` | Backend Member 3 | IDE tasks panel |
| `GET /api/v1/ide/context/branch` | Backend Member 3 | IDE context engine |
| `POST /api/v1/ide/agent-install/request` | Backend Member 4 | IDE agent prompt |
| `GET /api/v1/ide/agent-install/status/{jobId}` | Backend Member 4 | IDE agent prompt |
| `POST /api/v1/agent/enroll/start` | Backend Member 4 | Monitoring agent TrayApp |
| `POST /api/v1/agent/heartbeat` | Backend Member 4 | Monitoring agent |
| `POST /api/v1/agent/ingest` | Backend Member 4 | Monitoring agent |

---

## 7. IDE Extension Testing Plan

### Unit Tests

Use Mocha, sinon, and the VS Code extension test runner.

Test these extension modules first:
- `TagParser`: parses `@task:new #title:"Fix login" #priority:high`
- `TagExecutor`: sends parsed tags to `POST /api/v1/ide/tags/execute`
- `OneVoApiClient`: attaches auth headers, handles 401/403/429, maps API errors
- `AuthService`: stores tokens in VS Code `SecretStorage`, never localStorage
- `BranchDetector`: resolves branch context from mocked Git API
- `AgentInstaller`: prompts only when entitled, verifies SHA256 before running installer

### Webview Tests

Use `@vscode/test-electron` with mocked backend responses.

Cover:
- Chat panel loads channels and messages
- Typing `@` opens the picker
- Picker hides actions not returned by `permitted_tag_actions`
- HR section appears only when `active_modules` contains `hr_management`
- Clicking instant actions calls the tag executor
- Mini forms validate required fields before submit

### Contract Tests With Backend

Run the extension against a local backend seeded with test users:

| Scenario | Expected Result |
|---|---|
| User has `tasks:write` | `@task:new` appears and executes |
| User lacks `tasks:write` | `@task:new` is hidden; direct API call returns 403 |
| User has monitoring entitlement | Agent install prompt appears |
| User has no monitoring entitlement | No prompt appears |
| Backend revokes permission during session | Re-fetch hides action; execute returns 403 |
| Tag executes successfully | `ide_tag_executions` row is created |
| Undoable tag executes | Undo works before expiry and fails after expiry |

### Manual QA Checklist

1. Install the `.vsix` into a clean VS Code profile.
2. Sign in through the extension.
3. Confirm token persists after VS Code restart.
4. Open a repo with a `.onevo` config file.
5. Switch to a task-linked branch and confirm the status bar updates.
6. Open the chat sidebar and send a message.
7. Execute `@task:view`, `@time:start`, and `@time:stop`.
8. Test an HR user with `@leave:request` and `@clockin`.
9. Test a non-HR user and confirm HR actions are absent.
10. Test monitoring-entitled user and confirm install requires explicit consent.
11. Cancel install and confirm no installer runs.
12. Run install with a bad hash and confirm it aborts.

### CI Checks

Required commands for the IDE extension:

```bash
npm run lint
npm run compile
npm test
npm run test:vscode
vsce package
```

Required integration checks:

```bash
dotnet test ONEVO.sln
npm run test:contracts
```

### Release Gate

The IDE extension is ready only when:
- All unit and VS Code integration tests pass
- `.vsix` installs into a clean VS Code profile
- Extension connects to local backend with SignalR
- Permission-filtered picker works for at least three seeded roles
- Agent install prompt is consent-based and hash-verified
- No action succeeds without backend authorization

---

## 8. Working Rules

- Backend permissions are final. The frontend and IDE extension never decide authorization locally.
- The monitoring agent is a backend-owned deliverable with its own installer, enrollment, policy, telemetry, and health lifecycle.
- The IDE extension can request an agent install job only after backend entitlement approval and explicit user consent.
- The IDE extension never installs the monitoring agent silently.
- The IDE extension reads development context such as branch, repo URL, and file path; it must not collect keystrokes or file contents.
- All tag execution attempts are audit logged by the backend.
- Mock APIs are allowed for early frontend progress, but every screen and extension feature must move to real contract tests before release.
