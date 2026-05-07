# DEV8: Frontend VS Code IDE Extension

**Track:** Frontend
**Primary ownership:** VS Code IDE extension
**Current Unfinished Task:** Task 1 - Extension foundation
**Blocked By:** DEV3 IDE backend contract for live mode; DEV4 agent install contract for install flow

---

## ADE Instructions

When Dev 8 asks to continue, start with the first unchecked item in **Current Unfinished Task**. The extension owns the developer experience only. Permissions, entitlement, tag execution, and monitoring agent install decisions come from the backend.

---

## Task 1: Extension Foundation

**Goal:** scaffold the VS Code extension and connect it to OneVo auth and IDE session APIs.

**Contract:** `current-focus/contracts/auth-session.md` - `current-focus/contracts/ide-entitlements.md` (use MSW stubs; no structural prerequisite for scaffolding)

### Acceptance Criteria

- [ ] Extension project exists with TypeScript, webpack, lint, compile, test, and package scripts.
- [ ] `extension.ts` activates without blocking VS Code startup.
- [ ] Auth service supports login and token refresh.
- [ ] Tokens are stored in VS Code `SecretStorage`.
- [ ] Workspace config reader loads `.onevo` from repo root.
- [ ] API client attaches auth and handles 401, 403, 429, and validation errors.
- [ ] Extension registers install and starts IDE session after auth.
- [ ] Unit tests cover config load, auth storage, and API error mapping.

### References

- [[modules/ide-extension/overview|IDE Extension Spec]] (modules/ide-extension/overview.md)
- [[Userflow/IDE-Extension/ide-install-flow|IDE Install Flow]] (Userflow/IDE-Extension/ide-install-flow.md)
- [[frontend/data-layer/api-integration|API Integration]] (frontend/data-layer/api-integration.md)

### Verification

```bash
npm run lint
npm run compile
npm test
```

---

> **Parallel group** — Tasks 2, 3, 4, and 5 all require only Task 1 and are independent of each other. Run all four simultaneously.

## Task 2: Chat, Tasks, and Notifications Panels

**Goal:** provide the main IDE sidebar surfaces.

**Requires:** DEV8 Task 1 complete  
**Live integration:** DEV3 Tasks 3-4 (use MSW until ready) - Contract: `current-focus/contracts/signalr-events.md`

### Acceptance Criteria

- [ ] Activity bar container exists for OneVo.
- [ ] Chat panel lists channels and opens selected channel messages.
- [ ] Composer sends messages through backend API.
- [ ] SignalR appends new messages without refresh.
- [ ] Tasks panel lists assigned tasks from `GET /api/v1/ide/tasks/assigned`.
- [ ] Task detail webview opens from task click.
- [ ] Notifications panel lists notifications and unread count.
- [ ] Tests cover panel registration, mocked message load, task load, and notification update.

### References

- [[Userflow/IDE-Extension/context-detection-flow|Context Detection Flow]] (Userflow/IDE-Extension/context-detection-flow.md)
- [[Userflow/Chat/chat-overview|Chat Overview]] (Userflow/Chat/chat-overview.md)
- [[backend/real-time|Real-Time Architecture]] (backend/real-time.md)

### Verification

```bash
npm run test:vscode
npm run compile
```

---

## Task 3: Tag Engine + Picker

**Goal:** build the permission-filtered `@entity:action` launcher.

**Requires:** DEV8 Task 1 complete  
**Live integration:** DEV3 Task 4 (use MSW until ready) - Contract: `current-focus/contracts/ide-entitlements.md`

### Acceptance Criteria

- [ ] `TagParser` parses action name, named params, mentions, and quoted values.
- [ ] `TagExecutor` calls `POST /api/v1/ide/tags/execute`.
- [ ] Tag picker is built from `permitted_tag_actions`.
- [ ] HR group appears only when `active_modules` contains `hr_management`.
- [ ] Missing actions are hidden.
- [ ] Instant actions execute immediately.
- [ ] Form actions open mini forms.
- [ ] Undoable actions show countdown and call undo endpoint.
- [ ] Denied backend response shows inline error.
- [ ] Unit tests cover parser, picker filtering, HR gating, execute success, denied action, and undo.

### References

- [[Userflow/IDE-Extension/tag-engine-flow|Tag Engine Flow]] (Userflow/IDE-Extension/tag-engine-flow.md)
- [[modules/ide-extension/overview|IDE Extension Spec]] (modules/ide-extension/overview.md)

### Verification

```bash
npm test -- TagParser
npm test -- TagExecutor
npm run test:vscode
```

---

## Task 4: Context Engine + Time Tracking

**Goal:** connect branch/file context to tasks and time tracking.

**Requires:** DEV8 Task 1 complete  
**Live integration:** DEV3 Task 4 (use MSW until ready)

### Acceptance Criteria

- [ ] Branch detector uses VS Code Git API to read repo URL and branch.
- [ ] Branch context calls `GET /api/v1/ide/context/branch`.
- [ ] File context calls `GET /api/v1/ide/context/file`.
- [ ] Status bar shows linked task when branch or file has context.
- [ ] Time tracker supports start, stop, and elapsed display.
- [ ] `#task:current` resolves from active branch context.
- [ ] Tests cover branch detector with mocked Git API and time tracker state.

### References

- [[Userflow/IDE-Extension/context-detection-flow|Context Detection Flow]] (Userflow/IDE-Extension/context-detection-flow.md)
- [[modules/ide-extension/overview|IDE Extension Spec]] (modules/ide-extension/overview.md)

### Verification

```bash
npm test -- BranchDetector
npm test -- TimeTracker
npm run compile
```

---

## Task 5: Agent Install Prompt

**Goal:** trigger the monitoring agent install flow only after backend entitlement and explicit user consent.

**Requires:** DEV8 Task 1 complete  
**Live integration:** DEV4 Task 7 (use MSW until ready) - Contract: `current-focus/contracts/agent-gateway.md`

### Acceptance Criteria

- [ ] Extension reads `has_monitoring_entitlement` and installed status from IDE entitlements.
- [ ] No prompt appears when monitoring entitlement is false.
- [ ] Prompt offers Set Up, Not Now, and Do Not Ask Again.
- [ ] Set Up calls `POST /api/v1/ide/agent-install/request`.
- [ ] Installer downloads from backend-provided URL.
- [ ] SHA256 hash is verified before installer runs.
- [ ] Bad hash aborts install and shows error.
- [ ] Extension polls install status until installed or failed.
- [ ] Extension never reuses user JWT as an agent device credential.
- [ ] Tests cover no entitlement, prompt, do-not-ask flag, bad hash, and status polling.

### References

- [[Userflow/IDE-Extension/agent-install-flow|IDE Agent Install Flow]] (Userflow/IDE-Extension/agent-install-flow.md)
- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]] (Userflow/Workforce-Intelligence/agent-deployment.md)
- [[modules/agent-gateway/agent-installer|Agent Installer]] (modules/agent-gateway/agent-installer.md)

### Verification

```bash
npm test -- AgentInstaller
npm run test:vscode
npm run compile
```

---

## IDE Extension Full Test Checklist

- [ ] Install packaged `.vsix` in a clean VS Code profile.
- [ ] Sign in successfully.
- [ ] Restart VS Code and confirm token persists.
- [ ] Open repo with `.onevo` config.
- [ ] Open chat and send a message.
- [ ] Type `@` and confirm picker opens.
- [ ] Confirm forbidden actions are hidden.
- [ ] Execute `@task:view`.
- [ ] Execute `@time:start` and `@time:stop`.
- [ ] Test HR user with `@leave:request` and `@clockin`.
- [ ] Test non-HR user and confirm HR actions are absent.
- [ ] Test monitoring-entitled user and confirm install requires explicit consent.
- [ ] Cancel install and confirm nothing runs.
- [ ] Test bad hash and confirm install aborts.

### Final Verification

```bash
npm run lint
npm run compile
npm test
npm run test:vscode
vsce package
```

---

## Open Backend Contracts

- [x] `IDEEntitlementsDto` shape -> `current-focus/contracts/ide-entitlements.md`
- [x] `tag:executed` SignalR payload -> `current-focus/contracts/signalr-events.md`
- [x] Agent install job and status DTOs -> `current-focus/contracts/agent-gateway.md`
- [x] Auth session and token shapes -> `current-focus/contracts/auth-session.md`


