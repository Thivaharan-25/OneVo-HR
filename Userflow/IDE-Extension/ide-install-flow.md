# User Flow: IDE Extension Installation & Authentication

**Module:** IDE Extension (Week 5)
**Pillar:** Cross-Pillar (HR + WorkSync)
**Phase:** Phase 1
**Owner:** Dev 7 (IDE Extension Core)

---

## Overview

The IDE Extension (VS Code) connects a developer's editor to ONEVO WorkSync. Before any tag execution or context detection can work, the extension must be installed and authenticated via PKCE OAuth. Monitoring-agent installation is optional and only appears when the tenant has an active `agent_install_entitlement`.

IDE authentication and desktop-agent enrollment are intentionally separate:
- IDE authentication creates the developer's editor session and stores the user token in VS Code SecretStorage.
- TrayApp enrollment creates the Windows device session and stores a separate device credential with DPAPI / Windows Credential Manager.

If the user already authenticated in the browser for the IDE PKCE flow, the TrayApp should reuse that SSO session where possible. The user may still see a second approval/sign-in screen, but they should not need to manually enter API keys, tenant keys, or tenant IDs.

---

## Flow 1: Extension Installation & First Launch

```
Developer installs ONEVO extension from VS Code Marketplace
        │
        ▼
Extension activates — sidebar panels appear (Tasks, Chat, Time Tracker)
        │
        ▼
Extension checks for stored JWT in VS Code SecretStorage
        │
        ├─ JWT found + valid ──────────────────────────────► Skip to sidebar/context loading
        │
        └─ No JWT / expired
                │
                ▼
        "Sign in to ONEVO" prompt shown in sidebar
                │
                ▼
        Developer clicks "Sign In"
                │
                ▼
        Extension initiates PKCE OAuth flow
        (opens browser to ONEVO auth endpoint)
                │
                ▼
        Flow 2: PKCE Authentication
```

---

## Flow 2: PKCE OAuth Authentication

```
Browser opens: https://app.onevo.io/oauth/authorize
        │  (with code_challenge, redirect_uri = vscode://onevo/auth)
        ▼
User logs in (or already has session)
        │
        ▼
Authorization code returned via redirect to VS Code URI handler
        │
        ▼
Extension exchanges code + code_verifier for JWT at /oauth/token
        │
        ▼
JWT stored in VS Code SecretStorage
        │
        ▼
ide_extension_installs row created/updated:
  - install_id (UUID)
  - user_id, tenant_id
  - device_fingerprint (OS + hardware hash — not PII)
  - vscode_version, extension_version
        │
        ▼
ide_sessions row created:
  - install_id FK
  - started_at = now()
  - ended_at = null (open session)
        │
        ▼
Sidebar panels load with authenticated user data
```

---

## Flow 3: Agent Install Entitlement Check

This flow runs when the user attempts to install the desktop monitoring agent from within VS Code.

```
User clicks "Install ONEVO Agent" in VS Code sidebar
        │
        ▼
Extension calls POST /api/v1/ide/agent-install/request
        │
        ▼
Server checks agent_install_entitlements:
  WHERE tenant_id = ? AND is_active = true
        │
        ├─ No row / is_active = false
        │       │
        │       ▼
        │   403 returned — "Agent not enabled for your organisation"
        │   Extension shows: "Your admin hasn't enabled agent install"
        │   STOP — no install proceeds
        │
        └─ Entitlement active
                │
                ▼
        Extension shows explicit disclosure dialog:
        "ONEVO Agent will monitor activity on this device.
         This requires your approval. [Approve] [Cancel]"
        (NEVER silent install — user must explicitly approve)
                │
                ├─ User cancels ──────────────────────────► STOP
                │
                └─ User approves
                        │
                        ▼
                POST /api/v1/ide/agent-install/request
                agent_install_jobs row created:
                  - status = pending
                  - install_id FK → ide_extension_installs
                  - tenant_id, user_id
                        │
                        ▼
                Extension downloads signed installer and verifies SHA256
                        │
                        ▼
                TrayApp starts and opens Sign in
                        â”‚
                        â–¼
                User completes TrayApp/browser SSO enrollment
                        â”‚
                        â–¼
                Agent enrolls through Agent Gateway
                Extension calls PUT /api/v1/ide/agent-install/{id}/installed
                        │
                        ▼
                Extension sidebar shows "Agent active" status
```

---

## Flow 4: Session End

```
Developer closes VS Code / deactivates extension
        │
        ▼
Extension lifecycle: deactivate() called
        │
        ▼
PATCH /api/v1/ide/sessions/{sessionId}
  ended_at = now()
        │
        ▼
ide_sessions.ended_at set — session closed
```

---

## Key Invariants

| Rule | Enforcement |
|:-----|:------------|
| JWT stored in SecretStorage only — never in settings or disk | Extension (client) |
| device_fingerprint is OS + hardware hash, not PII | Server — strip PII before storing |
| Agent install always requires explicit user approval | Server + Extension UI |
| IDE login does not replace TrayApp enrollment | Separate user token and device credential |
| Entitlement check always server-side | Never trust client-side feature flag |
| One active session per install (ended_at = null) | Application layer |
| Entitlement is tenant-level — any user in tenant can approve | Server |

---

## Tables Involved

- `ide_extension_installs` — tracks each VS Code install (device + user)
- `ide_sessions` — open/closed session lifecycle
- `agent_install_entitlements` — tenant-level entitlement gate
- `agent_install_jobs` — entitlement-checked install job and status record
- `registered_agents` — post-install agent record (Agent Gateway)

---

## Related

- [[Userflow/IDE-Extension/tag-engine-flow|Tag Engine Flow]] — @entity:action execution
- [[Userflow/IDE-Extension/context-detection-flow|Context Detection Flow]] — branch→task detection
- [[modules/ide-extension/overview|IDE Extension Module Overview]]
- [[database/schemas/ide-extension|IDE Extension Schema]]
- [[database/schemas/agent-gateway|Agent Gateway Schema]]
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task 4]] — IDE Extension Core implementation
- [[current-focus/DEV8-documents-github-ide|DEV8 Task 5]] — IDE Agent Entitlement implementation
