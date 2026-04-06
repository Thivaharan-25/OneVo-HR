# Agent Brain — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a desktop agent secondary brain at `agent/` that guides the .NET MAUI + Windows Service team in building the ONEVO desktop monitoring agent.

**Architecture:** Two-component agent — a Windows Service (background activity collection) and a MAUI tray app (employee login, photo verification, status indicator). Communicates with ONEVO backend via Agent Gateway API.

**Tech Stack:** .NET 9, Windows Service, .NET MAUI, Win32 APIs (user32.dll), HttpClient + Polly, MSIX packaging

**Spec:** `docs/superpowers/specs/2026-04-05-onevo-monitoring-redesign.md` (Section 8)

---

### Task 1: Create agent/README.md

**Files:**
- Create: `agent/README.md`

- [ ] **Step 1: Create README**

```markdown
# ONEVO — Desktop Agent Secondary Brain

The AI-optimized knowledge base for the ONEVO desktop agent development team (.NET MAUI + Windows Service). This agent is installed on employee work laptops to capture activity data for the Workforce Intelligence pillar.

## Quick Start

1. Open in Cursor — `.cursor/rules/` auto-inject AI context
2. Read `AI_CONTEXT/project-context.md` for agent overview
3. Read `AI_CONTEXT/tech-stack.md` for technology details
4. Check `AI_CONTEXT/known-issues.md` before writing any code

## What This Agent Does

1. Captures keyboard/mouse activity counts (NOT keystrokes)
2. Tracks foreground application name and category
3. Detects idle periods (no input for configurable threshold)
4. Detects meeting applications (Teams, Zoom, Meet)
5. Captures photos for identity verification (when policy requires)
6. Batches and sends data to ONEVO backend every 2-3 minutes
7. Reads monitoring policy from server (per-employee feature toggles)
8. Runs as Windows Service — auto-starts on boot, tamper-resistant

## Two Components

| Component | Technology | Purpose |
|:----------|:-----------|:--------|
| **Background Service** | .NET 9 Windows Service | Always-on data collection, batching, sending |
| **Tray App** | .NET MAUI | Employee login, photo capture, status indicator, settings |

## Structure

```
agent/
├── AI_CONTEXT/              # AI reads these FIRST
│   ├── project-context.md   # What the agent does, architecture
│   ├── tech-stack.md        # .NET 9, MAUI, Win32 APIs
│   ├── rules.md             # Code generation rules
│   └── known-issues.md      # Agent-specific gotchas
├── .cursor/rules/           # Cursor AI auto-injected context
├── docs/
│   ├── architecture/
│   │   ├── README.md        # Agent architecture overview
│   │   ├── data-collection.md   # What data is captured and how
│   │   ├── agent-server-protocol.md  # API contract with backend
│   │   ├── tamper-resistance.md      # Anti-tamper measures
│   │   └── photo-capture.md          # Identity verification flow
│   └── guides/
│       └── coding-standards.md
└── decisions/               # Agent architecture decisions
```

## Key Principles

1. **Lightweight** — minimal CPU/memory footprint (target: <2% CPU, <50MB RAM)
2. **Non-intrusive** — no visible UI except tray icon (unless photo prompt)
3. **Tamper-resistant** — runs as Windows Service, monitors its own process
4. **Privacy-aware** — only captures what's enabled in employee's policy
5. **Offline-resilient** — buffers data locally if server is unreachable
6. **Policy-driven** — every feature controlled by server-pushed policy
```

- [ ] **Step 2: Commit**

```bash
git add agent/README.md
git commit -m "docs: create agent brain README"
```

---

### Task 2: Create agent/AI_CONTEXT/ files

**Files:**
- Create: `agent/AI_CONTEXT/project-context.md`
- Create: `agent/AI_CONTEXT/tech-stack.md`
- Create: `agent/AI_CONTEXT/rules.md`
- Create: `agent/AI_CONTEXT/known-issues.md`

- [ ] **Step 1: Create project-context.md**

```markdown
# Agent Project Context: ONEVO Desktop Agent

## 1. Overview

- **Project:** ONEVO Desktop Monitoring Agent
- **Purpose:** Capture employee work activity data from designated laptops and send it to the ONEVO backend for the Workforce Intelligence pillar
- **Platform:** Windows 10/11 (64-bit)
- **Technology:** .NET 9 Windows Service + .NET MAUI tray application
- **Backend:** Communicates with ONEVO Agent Gateway API (see `../../docs/architecture/module-catalog.md`)

## 2. Architecture

### Two-Component Design

```
┌─────────────────────────────────────────────────────┐
│                  Employee Laptop                     │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         MAUI Tray Application               │   │
│  │  • System tray icon (status indicator)      │   │
│  │  • Employee login/logout                    │   │
│  │  • Photo capture dialog                     │   │
│  │  • Settings viewer (what's being tracked)   │   │
│  │  • About / version info                     │   │
│  └────────────────┬────────────────────────────┘   │
│                   │ IPC (named pipe)                │
│  ┌────────────────▼────────────────────────────┐   │
│  │         Windows Service                      │   │
│  │  • Activity collector (keyboard/mouse counts)│   │
│  │  • App tracker (foreground window monitor)  │   │
│  │  • Idle detector                            │   │
│  │  • Meeting detector                         │   │
│  │  • Data batcher (aggregates every 2-3 min)  │   │
│  │  • HTTP sender (to Agent Gateway)           │   │
│  │  • Local buffer (SQLite for offline mode)   │   │
│  │  • Heartbeat sender (every 60 seconds)      │   │
│  │  • Policy syncer (every 30 minutes)         │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Communication: Service ↔ MAUI via Named Pipes      │
│  Communication: Service → Backend via HTTPS          │
└─────────────────────────────────────────────────────┘
```

### Data Collection Modules (inside Windows Service)

| Module | What It Captures | How | Frequency |
|:-------|:-----------------|:----|:----------|
| Activity Collector | Keyboard event count, mouse event count, mouse distance | Win32 `SetWindowsHookEx` (low-level hooks, counts only) | Continuous, aggregated per snapshot |
| App Tracker | Foreground app name, window title (hashed) | `GetForegroundWindow()` + `GetWindowText()` | Poll every 5 seconds |
| Idle Detector | Idle duration | `GetLastInputInfo()` | Check every 30 seconds |
| Meeting Detector | Meeting app active, camera status, mic status | Process enumeration + media device status | Check every 30 seconds |
| Screenshot Capturer | Screen capture | `Graphics.CopyFromScreen()` | Per policy (disabled by default) |

### Data Flow

```
Collectors → In-Memory Aggregator → Snapshot (every 2-3 min) → Batch Queue
                                                                    │
                                                              ┌─────▼──────┐
                                                              │ Online?    │
                                                              ├─ Yes ──────┤
                                                              │ POST to    │
                                                              │ Agent GW   │
                                                              ├─ No ───────┤
                                                              │ Store in   │
                                                              │ SQLite     │
                                                              └────────────┘
```

## 3. Key Business Rules

1. **Policy-first:** Before capturing ANY data, check the employee's monitoring policy. If a feature is OFF, the collector does not run.
2. **Counts, not content:** Keyboard monitoring captures EVENT COUNTS, not keystrokes. This is critical for privacy and compliance.
3. **Window titles are hashed:** The agent captures `SHA256(windowTitle)` — the backend can match known patterns but cannot read actual content.
4. **Local buffer for offline:** When the server is unreachable, data is stored in a local SQLite database. When connectivity resumes, buffered data is sent in chronological order.
5. **Heartbeat is mandatory:** Even if all monitoring features are OFF, the agent sends heartbeats. This tells the server the agent is installed and running.
6. **Auto-update:** The agent checks for updates on startup and periodically. Updates are applied silently via MSIX.

## 4. Employee Experience

1. Agent is pre-installed on company laptop (via MSIX or MDM push)
2. On first boot, Windows Service starts automatically
3. Employee sees tray icon (gray = not logged in)
4. Employee clicks tray icon → login dialog (email + password, or SSO)
5. On login → tray icon turns green, agent starts capturing per policy
6. If photo verification is enabled → dialog prompts camera capture at configured intervals
7. At end of day → employee clicks "Log Out" or simply shuts down laptop
8. Service continues running (heartbeat only, no activity capture without logged-in employee)
```

- [ ] **Step 2: Create tech-stack.md**

```markdown
# Agent Tech Stack: ONEVO Desktop Agent

## Core

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Runtime | .NET | 9.0 | Same as backend — shared C# expertise |
| Background Service | Windows Service | .NET 9 Worker Service template | `Microsoft.Extensions.Hosting.WindowsServices` |
| UI | .NET MAUI | 9.0 | System tray app, photo capture dialog |
| Local Storage | SQLite | via `Microsoft.Data.Sqlite` | Offline buffer for activity data |
| HTTP Client | HttpClient + Polly | Built-in | Retry, circuit breaker for server communication |
| IPC | Named Pipes | `System.IO.Pipes` | Service ↔ MAUI communication |
| Installer | MSIX | Windows SDK | Silent install, auto-update |

## Win32 APIs Used

| API | Purpose | DLL |
|:----|:--------|:----|
| `SetWindowsHookEx` (WH_KEYBOARD_LL) | Count keyboard events | user32.dll |
| `SetWindowsHookEx` (WH_MOUSE_LL) | Count mouse events | user32.dll |
| `GetForegroundWindow` | Get active window handle | user32.dll |
| `GetWindowText` | Get window title (for hashing) | user32.dll |
| `GetWindowThreadProcessId` | Get process from window | user32.dll |
| `GetLastInputInfo` | Detect idle time | user32.dll |
| `Process.GetProcesses()` | Enumerate running processes | .NET BCL |

## Communication

| Direction | Protocol | Endpoint | Auth |
|:----------|:---------|:---------|:-----|
| Agent → Backend | HTTPS POST | `/api/v1/agent/ingest` | Device JWT |
| Agent → Backend | HTTPS GET | `/api/v1/agent/heartbeat` | Device JWT |
| Agent → Backend | HTTPS GET | `/api/v1/agent/policy` | Device JWT |
| Agent → Backend | HTTPS POST | `/api/v1/agent/register` | Tenant API key |
| Employee → Agent | Named Pipe | Local IPC | N/A (same machine) |

## Testing

| Type | Technology |
|:-----|:-----------|
| Unit | xUnit + Moq |
| Integration | xUnit + WireMock (mock Agent Gateway) |
| Manual | Windows VM with agent installed |

## NOT Using

| Technology | Reason |
|:-----------|:-------|
| Electron | Heavy runtime, unnecessary for background agent |
| Rust/Tauri | Team doesn't know Rust, .NET 9 is sufficient |
| WPF | MAUI is cross-platform ready for future Mac support |
| gRPC | REST is simpler for periodic batch uploads |
| RabbitMQ | Agent communicates directly via HTTPS, no message queue needed |
```

- [ ] **Step 3: Create rules.md**

```markdown
# Agent AI Rules: ONEVO Desktop Agent

## 1. General Rules

- **Source of Truth:** Agent brain files in `agent/AI_CONTEXT/`. Backend context in `../../AI_CONTEXT/`.
- **Windows-only (Phase 1):** All Win32 API calls target Windows. Do not use cross-platform alternatives that don't work on Windows.
- **Hallucination Prevention:** Do not guess Agent Gateway API contracts. Check `../../docs/architecture/external-integrations.md`.

## 2. C# / .NET Rules

### Naming Conventions

Same as backend — see `../../AI_CONTEXT/rules.md` for full naming table.

### Architecture Patterns

```csharp
// ALWAYS: Use IHostedService for background collectors
public class ActivityCollector : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var snapshot = _aggregator.CreateSnapshot();
            _batchQueue.Enqueue(snapshot);
            await Task.Delay(TimeSpan.FromMinutes(2), ct);
        }
    }
}

// ALWAYS: Check policy before collecting
if (!_policy.IsFeatureEnabled(MonitoringFeature.ActivityTracking))
    return; // Skip collection

// ALWAYS: Use Polly for HTTP resilience
services.AddHttpClient<IAgentGatewayClient>()
    .AddTransientHttpErrorPolicy(p => p.WaitAndRetryAsync(3, attempt =>
        TimeSpan.FromSeconds(Math.Pow(2, attempt))))
    .AddTransientHttpErrorPolicy(p => p.CircuitBreakerAsync(5, TimeSpan.FromMinutes(2)));

// ALWAYS: Buffer locally when offline
try
{
    await _client.SendBatchAsync(batch, ct);
}
catch (HttpRequestException)
{
    await _localBuffer.StoreAsync(batch, ct); // SQLite fallback
}
```

### Patterns to AVOID

```csharp
// NEVER: Capture actual keystrokes
var key = (Keys)lParam->vkCode; // BAD — this logs what the user types
// Instead: just increment a counter
_keyboardEventCount++; // GOOD — counts only

// NEVER: Store raw window titles
var title = GetWindowText(hwnd); // BAD — may contain sensitive content
// Instead: hash them
var titleHash = SHA256.HashData(Encoding.UTF8.GetBytes(title)); // GOOD

// NEVER: Send data without checking policy
await SendSnapshot(snapshot); // BAD — feature might be disabled
// Instead: always check
if (_policy.IsFeatureEnabled(MonitoringFeature.ActivityTracking))
    await SendSnapshot(snapshot);

// NEVER: Block the UI thread in MAUI
var photo = CapturePhoto(); // BAD if synchronous
// Instead: async
var photo = await CapturePhotoAsync(ct); // GOOD

// NEVER: Store device JWT in plain text
File.WriteAllText("token.txt", jwt); // BAD
// Instead: use Windows DPAPI
ProtectedData.Protect(jwtBytes, null, DataProtectionScope.CurrentUser); // GOOD
```

## 3. Security Rules

- Device JWT stored via Windows DPAPI (`ProtectedData.Protect`)
- All server communication over HTTPS (TLS 1.2+)
- Certificate pinning for Agent Gateway endpoint
- No admin credentials stored on device
- Employee password is used for login only — never stored
- SQLite buffer is encrypted at rest (SQLCipher or DPAPI)

## 4. Performance Rules

- Target: <2% CPU average, <50MB RAM
- Keyboard/mouse hooks must be lightweight — just increment counters
- App tracking polls every 5 seconds (not continuous)
- Batch data every 2-3 minutes (not every event)
- Use `System.Threading.Timer` not `Task.Delay` in tight loops
- Profile with dotnet-counters before release

## 5. Testing Rules

- Unit test all collectors with mocked Win32 APIs
- Unit test batch queue and offline buffer
- Integration test HTTP client with WireMock
- Test policy enforcement (feature OFF = no data captured)
- Test offline mode (disconnect → buffer → reconnect → send)
```

- [ ] **Step 4: Create known-issues.md**

```markdown
# Agent Known Issues & Gotchas

**Last Updated:** 2026-04-05

## Gotchas

- **Low-Level Keyboard Hooks Require Message Pump:** `SetWindowsHookEx` with `WH_KEYBOARD_LL` requires a message loop (`Application.Run()` or equivalent). In a Windows Service, you must create a dedicated thread with a message pump. The MAUI app has one naturally.

- **Windows Service Cannot Access Desktop:** Windows Services run in Session 0 (no desktop). Camera access, screen capture, and window title reading require the MAUI tray app (running in the user's session). Data flows from MAUI → Service via Named Pipes.

- **GetForegroundWindow from Service:** This Win32 call returns NULL from Session 0. Foreground window tracking MUST run in the MAUI tray app process, not the service. The tray app sends app tracking data to the service via IPC.

- **Camera Access in MAUI:** MAUI's `MediaPicker.CapturePhotoAsync()` works for identity verification. However, it requires user consent on first use (Windows camera permission dialog). Handle the case where the user denies camera access.

- **MSIX Auto-Update:** MSIX supports auto-update via `PackageManager.AddPackageAsync()`. However, updates require the app to restart. Schedule updates during non-work hours or when the employee logs out.

- **SQLite in Windows Service:** SQLite works fine in a Windows Service, but ensure the database file is in a writable location (`ProgramData/ONEVO/agent.db`), not `Program Files`.

- **Multiple Monitors:** `GetForegroundWindow` tracks the active window across all monitors. Screenshot capture should only capture the primary monitor (or the monitor with the active window). Clarify with product which behavior is expected.

- **Antivirus False Positives:** Low-level keyboard hooks and process enumeration may trigger antivirus warnings. Ensure the MSIX is signed with an EV certificate. Provide IT administrators with whitelisting guidance.

- **VPN / Proxy:** Some companies route all traffic through VPN/proxy. The agent's HTTP client must support proxy configuration (via system proxy settings). Polly circuit breaker prevents the agent from hammering a blocked endpoint.

## Active Bugs

| ID | Description | Severity | Status |
|:---|:------------|:---------|:-------|
| - | No active bugs yet (agent in initial development) | - | - |
```

- [ ] **Step 5: Commit**

```bash
git add agent/AI_CONTEXT/
git commit -m "docs: create agent brain AI context files"
```

---

### Task 3: Create agent/.cursor/rules/

**Files:**
- Create: `agent/.cursor/rules/project-context.mdc`
- Create: `agent/.cursor/rules/coding-standards.mdc`

- [ ] **Step 1: Create project-context.mdc**

```markdown
---
description: ONEVO Desktop Agent — always-on project identity
globs: *
---

# ONEVO Desktop Agent

You are working on the ONEVO desktop monitoring agent — a .NET 9 Windows Service + MAUI tray app that captures employee work activity data.

## Key Facts
- Two components: Windows Service (background collection) + MAUI tray app (UI, camera, app tracking)
- Communicates with ONEVO backend via Agent Gateway API
- Auth: Device JWT (NOT user JWT)
- Privacy: counts only (not keystrokes), window titles hashed, policy-driven
- Offline: SQLite buffer when server unreachable
- Target: <2% CPU, <50MB RAM

## Before Writing Code
1. Read `agent/AI_CONTEXT/rules.md` for conventions
2. Read `agent/AI_CONTEXT/known-issues.md` — critical gotchas about Session 0, message pumps
3. Check `../../docs/architecture/external-integrations.md` for API contracts
4. ALWAYS check monitoring policy before capturing data
```

- [ ] **Step 2: Create coding-standards.mdc**

```markdown
---
description: ONEVO Agent coding standards
globs: **/*.cs
---

# Agent Coding Standards

- .NET 9 / C# 13 — same conventions as backend (see ../../AI_CONTEXT/rules.md)
- NEVER capture actual keystrokes — count events only
- NEVER store raw window titles — hash with SHA256
- ALWAYS check employee monitoring policy before any data collection
- ALWAYS use Polly for HTTP calls (retry + circuit breaker)
- ALWAYS fall back to SQLite buffer when server is unreachable
- Store device JWT via DPAPI — never plain text
- Win32 API calls go in a dedicated `NativeInterop/` folder with P/Invoke signatures
- Background collectors implement `BackgroundService` (IHostedService)
- IPC between Service and MAUI uses Named Pipes with serialized DTOs
```

- [ ] **Step 3: Commit**

```bash
git add agent/.cursor/rules/
git commit -m "docs: create agent Cursor rules"
```

---

### Task 4: Create agent/docs/architecture/

**Files:**
- Create: `agent/docs/architecture/README.md`
- Create: `agent/docs/architecture/data-collection.md`
- Create: `agent/docs/architecture/agent-server-protocol.md`
- Create: `agent/docs/architecture/tamper-resistance.md`
- Create: `agent/docs/architecture/photo-capture.md`

- [ ] **Step 1: Create README.md**

```markdown
# Agent Architecture: ONEVO Desktop Agent

## Overview

Two-component agent running on employee Windows laptops:

| Component | Process | Session | Responsibilities |
|:----------|:--------|:--------|:----------------|
| Windows Service | `OnevoAgentService.exe` | Session 0 (system) | Heartbeat, batch sending, offline buffer, policy sync |
| MAUI Tray App | `OnevoAgent.exe` | User session | App tracking, keyboard/mouse hooks, photo capture, UI |

The service and tray app communicate via Named Pipes. The service is the only component that talks to the backend.

## Key Documents

| Document | Purpose |
|:---------|:--------|
| [Data Collection](data-collection.md) | What data is captured, how, and privacy controls |
| [Agent-Server Protocol](agent-server-protocol.md) | API contract with Agent Gateway |
| [Tamper Resistance](tamper-resistance.md) | Anti-tamper and integrity measures |
| [Photo Capture](photo-capture.md) | Identity verification camera flow |

## Solution Structure

```
OnevoAgent.sln
├── src/
│   ├── Onevo.Agent.Service/           # Windows Service (background)
│   │   ├── Workers/
│   │   │   ├── HeartbeatWorker.cs     # 60-second heartbeat
│   │   │   ├── BatchSenderWorker.cs   # Send queued snapshots to server
│   │   │   ├── PolicySyncWorker.cs    # Refresh policy every 30 min
│   │   │   └── BufferFlushWorker.cs   # Send offline-buffered data
│   │   ├── Communication/
│   │   │   ├── AgentGatewayClient.cs  # HTTP client for Agent Gateway
│   │   │   └── NamedPipeServer.cs     # IPC server for MAUI app
│   │   ├── Storage/
│   │   │   ├── LocalBuffer.cs         # SQLite offline buffer
│   │   │   └── PolicyStore.cs         # Cached monitoring policy
│   │   ├── Security/
│   │   │   └── TokenStore.cs          # DPAPI-protected JWT storage
│   │   └── Program.cs                 # Service entry point
│   ├── Onevo.Agent.TrayApp/           # MAUI tray application
│   │   ├── Collectors/
│   │   │   ├── ActivityCollector.cs   # Keyboard/mouse event counter
│   │   │   ├── AppTracker.cs          # Foreground window monitor
│   │   │   ├── IdleDetector.cs        # Idle time detection
│   │   │   ├── MeetingDetector.cs     # Meeting app detection
│   │   │   └── ScreenshotCapturer.cs  # Screen capture (if enabled)
│   │   ├── Verification/
│   │   │   └── PhotoCaptureService.cs # Camera photo capture
│   │   ├── Communication/
│   │   │   └── NamedPipeClient.cs     # IPC client to service
│   │   ├── NativeInterop/
│   │   │   ├── User32.cs             # P/Invoke for user32.dll
│   │   │   └── Kernel32.cs           # P/Invoke for kernel32.dll
│   │   ├── Views/
│   │   │   ├── LoginPage.xaml         # Employee login dialog
│   │   │   ├── PhotoCapturePage.xaml  # Camera capture prompt
│   │   │   └── StatusPage.xaml        # "What's being tracked" info
│   │   ├── Models/
│   │   │   ├── ActivitySnapshot.cs    # Snapshot data model
│   │   │   ├── AppUsageRecord.cs      # App tracking record
│   │   │   └── MonitoringPolicy.cs    # Policy from server
│   │   └── MauiProgram.cs
│   └── Onevo.Agent.Shared/            # Shared models between Service and TrayApp
│       ├── Dtos/
│       │   ├── IngestBatchDto.cs      # Batch payload to Agent Gateway
│       │   ├── HeartbeatDto.cs
│       │   └── PolicyDto.cs
│       └── IpcMessages/
│           ├── SnapshotMessage.cs     # TrayApp → Service: activity data
│           ├── LoginMessage.cs        # TrayApp → Service: employee linked
│           └── PolicyMessage.cs       # Service → TrayApp: updated policy
├── tests/
│   ├── Onevo.Agent.Tests.Unit/
│   └── Onevo.Agent.Tests.Integration/
└── installer/
    └── OnevoAgent.msixproj            # MSIX packaging
```
```

- [ ] **Step 2: Create data-collection.md**

Document each data collection module in detail:

**Activity Collector:**
- Win32 hook: `WH_KEYBOARD_LL` and `WH_MOUSE_LL`
- Captures: event count per interval (NOT keystrokes)
- Runs in MAUI tray app process (requires message pump)
- Sends counts to Service via Named Pipe every snapshot interval

**App Tracker:**
- `GetForegroundWindow()` → `GetWindowThreadProcessId()` → `Process.GetProcessById()`
- Captures: process name, window title (SHA256 hashed), category (lookup from policy)
- Polls every 5 seconds from MAUI tray app
- Window title hashing example:
  ```csharp
  var titleHash = Convert.ToHexString(SHA256.HashData(
      Encoding.UTF8.GetBytes(windowTitle)));
  ```

**Idle Detector:**
- `GetLastInputInfo()` returns milliseconds since last input
- If idle > threshold (configurable, default 5 min) → mark as idle
- Idle periods are included in activity snapshots

**Meeting Detector:**
- Check for known meeting processes: `Teams.exe`, `Zoom.exe`, `chrome.exe` (with Google Meet tab)
- Check camera/mic status via Windows Media Device APIs
- Captures: meeting platform, camera on/off, mic active/off

**Screenshot Capturer:**
- `Graphics.CopyFromScreen()` (primary monitor)
- Triggered by policy: scheduled (every N minutes), random, or manual
- Image compressed to JPEG (quality 60%), sent as part of batch
- Disabled by default — requires explicit tenant policy

**Data snapshot format:**
```json
{
  "employeeId": "uuid",
  "deviceId": "uuid",
  "capturedAt": "2026-04-05T14:30:00Z",
  "keyboardEventsCount": 342,
  "mouseEventsCount": 128,
  "mouseDistancePx": 4521,
  "activeSeconds": 145,
  "idleSeconds": 35,
  "foregroundApp": "Code",
  "windowTitleHash": "a1b2c3...",
  "appCategory": "development",
  "meetingActive": false,
  "meetingPlatform": null,
  "cameraOn": false,
  "micActive": false
}
```

- [ ] **Step 3: Create agent-server-protocol.md**

Document the complete API contract:

**Registration:**
```
POST /api/v1/agent/register
Headers: X-Tenant-Api-Key: {tenantApiKey}
Body: { deviceName, osVersion, agentVersion }
Response: { agentId, deviceId, deviceJwt, policyJson }
```

**Heartbeat:**
```
GET /api/v1/agent/heartbeat
Headers: Authorization: Bearer {deviceJwt}
Response: 200 OK { serverTime, policyVersion }
```

**Policy Sync:**
```
GET /api/v1/agent/policy
Headers: Authorization: Bearer {deviceJwt}
Query: ?employeeId={id}
Response: { features: { activityTracking: true, appTracking: true, ... }, verificationPolicy: { ... } }
```

**Data Ingestion:**
```
POST /api/v1/agent/ingest
Headers: Authorization: Bearer {deviceJwt}
Body: { employeeId, snapshots: [...], appUsage: [...], meetings: [...] }
Response: 202 Accepted
```

**Photo Upload (Identity Verification):**
```
POST /api/v1/agent/verify
Headers: Authorization: Bearer {deviceJwt}
Body: multipart/form-data { employeeId, photo, capturedAt, trigger }
Response: 200 { verificationId, status }
```

**Employee Login (via tray app):**
```
POST /api/v1/agent/employee-login
Headers: Authorization: Bearer {deviceJwt}
Body: { email, password }
Response: { employeeId, employeeName, policy }
```

Include error codes, rate limits (max 1 ingest per minute per device), and retry behavior.

- [ ] **Step 4: Create tamper-resistance.md**

Document anti-tamper measures:

1. **Windows Service auto-restart:** Service configured with `sc failure` to auto-restart on crash
2. **Process monitoring:** Service monitors MAUI tray app — restarts if killed
3. **Heartbeat detection:** Backend detects missing heartbeat after 5 min → fires `AgentHeartbeatLost` event
4. **Integrity checks:** Agent verifies its own binary hash on startup
5. **DPAPI for secrets:** Device JWT and local buffer encryption key stored via DPAPI
6. **Cannot uninstall without admin:** MSIX requires admin privileges to remove
7. **Service runs as LOCAL SYSTEM:** Cannot be stopped by non-admin users
8. **Audit logging:** All agent start/stop/error events sent to server in heartbeat payload

What this does NOT prevent (and is not intended to):
- Employee using a different device entirely (covered by device tracking)
- Employee physically covering the camera (verification fails gracefully)
- Network disconnection (offline buffer handles this)

- [ ] **Step 5: Create photo-capture.md**

Document identity verification flow:

```
Policy says "verify at intervals" (e.g., every 120 min)
  │
  ├─── Timer fires in Windows Service
  │    └─── Service sends "capture photo" IPC message to MAUI tray app
  │
  ├─── MAUI tray app receives message
  │    └─── Shows photo capture dialog (non-dismissible, 60-second timeout)
  │         ├── Employee clicks "Capture" → camera takes photo
  │         │   └── Photo sent to Service via IPC → Service uploads to Agent Gateway
  │         ├── Employee ignores (timeout) → recorded as "skipped"
  │         │   └── Status sent to server → may trigger exception alert
  │         └── Camera unavailable → recorded as "failed"
  │             └── Status sent to server → may trigger exception alert
  │
  └─── Login/Logout verification: same flow, triggered on login/logout instead of timer
```

Photo handling:
- Captured via MAUI `MediaPicker.CapturePhotoAsync()`
- Compressed to JPEG (quality 70%)
- Sent to server immediately (not batched)
- NOT stored locally after upload (deleted from temp)
- Server-side: stored in blob storage, matched against employee profile photo (if configured)
- Match confidence returned as 0-100 score

- [ ] **Step 6: Commit**

```bash
git add agent/docs/
git commit -m "docs: create agent architecture documentation"
```

---

### Task 5: Final review — Agent Brain consistency check

- [ ] **Step 1: Verify all cross-references**

Check that:
- API endpoints in agent-server-protocol.md match backend external-integrations.md
- Data snapshot format matches backend `activity_snapshots` table schema
- Policy features match `monitoring_feature_toggles` table columns
- Win32 API usage aligns with known-issues.md warnings
- Solution structure matches the two-component architecture

- [ ] **Step 2: Commit any fixes**

```bash
git add agent/
git commit -m "docs: agent brain consistency fixes"
```
