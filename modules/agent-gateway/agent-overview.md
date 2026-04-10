# Desktop Agent — Start Here

## What Is the ONEVO Desktop Agent?

The ONEVO Desktop Agent is a Windows application that monitors employee activity on company devices. It consists of three components:

| Component | Project | Purpose |
|:----------|:--------|:--------|
| **Windows Service** | `ONEVO.Agent.Service` | Always-on background data collector. Runs as a Windows Service. Captures activity data, buffers locally, syncs to server. |
| **MAUI Tray App** | `ONEVO.Agent.TrayApp` | System tray UI. Handles employee login/logout, photo capture for identity verification, status display. |
| **Shared Library** | `ONEVO.Agent.Shared` | Shared types (IPC messages, models, constants) used by both Service and TrayApp. |

The Service and TrayApp are separate processes that communicate via **Named Pipes** (IPC). See [[modules/agent-gateway/ipc-protocol|Ipc Protocol]] for the full message contract.

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        DESKTOP MACHINE                          │
│                                                                 │
│  ┌──────────────────────┐    Named Pipes    ┌────────────────┐  │
│  │  ONEVO.Agent.Service │◄────────────────►│ MAUI Tray App  │  │
│  │                      │   (IPC messages)  │                │  │
│  │  ┌────────────────┐  │                   │  - Login UI    │  │
│  │  │  Collectors    │  │                   │  - Status      │  │
│  │  │  - Activity    │  │                   │  - Photo       │  │
│  │  │  - App Tracker │  │                   │    Capture     │  │
│  │  │  - Idle        │  │                   └────────────────┘  │
│  │  │  - Meeting     │  │                                       │
│  │  │  - Device      │  │                                       │
│  │  └───────┬────────┘  │                                       │
│  │          │            │                                       │
│  │  ┌───────▼────────┐  │                                       │
│  │  │ SQLite Buffer  │  │                                       │
│  │  │ (offline-safe) │  │                                       │
│  │  └───────┬────────┘  │                                       │
│  │          │            │                                       │
│  │  ┌───────▼────────┐  │                                       │
│  │  │  Sync Service  │──┼──── HTTPS ────► Agent Gateway API     │
│  │  │  + Heartbeat   │  │                 /api/v1/agent/*       │
│  │  └────────────────┘  │                                       │
│  └──────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Flow

1. **Install** — MSIX package installs the Service + TrayApp. Service registers with the server via `POST /api/v1/agent/register`, receives a device JWT. See [[modules/agent-gateway/agent-installer|Agent Installer]].
2. **Employee Login** — Employee opens tray app, enters email + password. TrayApp sends `employee_login` IPC message to Service. Service calls `POST /api/v1/agent/login`, receives monitoring policy. See [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]].
3. **Collectors Start** — Based on the received policy, the Service starts the enabled collectors (activity, app tracking, idle, meeting, device). See [[modules/agent-gateway/data-collection|Data Collection]].
4. **Buffer Locally** — Collected data is written to the local SQLite buffer immediately. See [[modules/agent-gateway/sqlite-buffer|Sqlite Buffer]].
5. **Sync to Server** — Every `snapshot_interval_seconds` (default 150s), the Sync Service reads unsent rows from the buffer, batches them, and sends via `POST /api/v1/agent/ingest`. Server returns 202 Accepted.
6. **Heartbeat** — Every 60 seconds, the Service sends a heartbeat to `POST /api/v1/agent/heartbeat` with CPU usage, memory, buffer count, and any errors.
7. **Identity Verification** — When the policy triggers a verification (login, interval, or logout), the Service sends `capture_photo` via IPC to the TrayApp. See [[modules/identity-verification/photo-capture|Photo Capture]].
8. **Employee Logout** — Employee clicks logout in TrayApp. Service calls `POST /api/v1/agent/logout`. Collectors stop. Service continues heartbeating.

---

## Reading Order

Read these docs in this order to understand the full agent system:

| # | Document | What You Learn |
|:--|:---------|:---------------|
| 1 | **This file** (`agent-overview`) | Architecture, data flow, setup |
| 2 | [[modules/agent-gateway/agent-server-protocol\|Agent Server Protocol]] | All 6 API endpoints (register, login, policy, heartbeat, ingest, logout) |
| 3 | [[modules/agent-gateway/data-collection\|Data Collection]] | 5 collectors with Win32 P/Invoke code samples |
| 4 | [[modules/agent-gateway/ipc-protocol\|Ipc Protocol]] | Named Pipes messages between Service and TrayApp |
| 5 | [[modules/agent-gateway/sqlite-buffer\|Sqlite Buffer]] | Local SQLite schema, offline resilience, encryption |
| 6 | [[modules/agent-gateway/tamper-resistance\|Tamper Resistance]] | Detection and reporting of service manipulation |
| 7 | [[modules/identity-verification/photo-capture\|Photo Capture]] | Camera capture and identity verification flow |
| 8 | [[modules/agent-gateway/tray-app-ui\|Tray App Ui]] | MAUI tray app UI: login, status, photo capture, notifications |
| 9 | [[modules/agent-gateway/agent-installer\|Agent Installer]] | MSIX packaging, silent install, auto-update |
| 10 | [[modules/agent-gateway/mock-mode\|Mock Mode]] | Development without a backend server |

Also read:
- [[AI_CONTEXT/rules|Rules]] (Section 10) — Privacy rules, performance budgets, coding standards
- [[AI_CONTEXT/tech-stack|Tech Stack]] (Section 4) — NuGet packages, Win32 APIs, project structure

---

## Project Structure

```
ONEVO.Agent/
├── ONEVO.Agent.Service/           # Windows Service (background collector)
│   ├── Collectors/
│   │   ├── ActivityCollector.cs    # Keyboard/mouse event counting
│   │   ├── AppTracker.cs          # Foreground app detection
│   │   ├── IdleDetector.cs        # Idle period detection
│   │   ├── MeetingDetector.cs     # Meeting app process detection
│   │   └── DeviceTracker.cs       # Device active/idle cycle tracking
│   ├── Buffer/
│   │   ├── SqliteBuffer.cs        # Local SQLite storage
│   │   └── BufferCleanup.cs       # Purge sent data
│   ├── Sync/
│   │   ├── DataSyncService.cs     # Batch & send to Agent Gateway
│   │   ├── HeartbeatService.cs    # 60-second heartbeat
│   │   └── PolicySyncService.cs   # Fetch monitoring policy
│   ├── Security/
│   │   ├── DeviceTokenStore.cs    # Secure Device JWT storage (DPAPI)
│   │   └── TamperDetector.cs      # Detect service manipulation
│   ├── IPC/
│   │   └── NamedPipeServer.cs     # Listen for MAUI app commands
│   └── Program.cs
│
├── ONEVO.Agent.TrayApp/           # MAUI tray app
│   ├── Views/
│   │   ├── LoginWindow.xaml
│   │   ├── StatusPopup.xaml
│   │   └── PhotoCaptureWindow.xaml
│   ├── Services/
│   │   ├── NamedPipeClient.cs
│   │   ├── CameraService.cs
│   │   └── TrayIconService.cs
│   └── App.xaml.cs
│
├── ONEVO.Agent.Shared/            # Shared types between Service and TrayApp
│   ├── Models/
│   │   ├── ActivitySnapshot.cs
│   │   ├── AppUsageRecord.cs
│   │   ├── DeviceSession.cs
│   │   └── AgentPolicy.cs
│   ├── IPC/
│   │   └── IpcMessages.cs
│   └── Constants.cs
│
└── ONEVO.Agent.Installer/         # MSIX packaging
    └── Package.appxmanifest
```

Full structure also documented in [[AI_CONTEXT/tech-stack|Tech Stack]] Section 4.

---

## NuGet Dependencies

| Package | Purpose |
|:--------|:--------|
| `Microsoft.Extensions.Hosting.WindowsServices` | Windows Service hosting (`Host.CreateDefaultBuilder().UseWindowsService()`) |
| `Microsoft.Data.Sqlite` | SQLite local buffer for offline resilience |
| `Polly` | HTTP resilience — retry, circuit breaker, timeout |
| `System.Text.Json` | JSON serialization for API payloads and IPC messages |
| `Serilog` + `Serilog.Sinks.File` | Local logging (rolling file, max 7 days) |
| `CommunityToolkit.Maui` | MAUI helpers — tray icon, notifications |

---

## Development Setup

### Prerequisites

| Requirement | Version | Notes |
|:------------|:--------|:------|
| Windows | 10 (1809+) or 11 | Agent targets Windows desktop only |
| .NET SDK | 9.0 | Download from https://dotnet.microsoft.com |
| .NET MAUI workload | 9.0 | `dotnet workload install maui` |
| Visual Studio | 2022 17.8+ | Recommended. Needed for XAML designer + MSIX packaging tools |
| SQLite | Bundled | Comes with `Microsoft.Data.Sqlite` NuGet |
| Windows SDK | 10.0.19041+ | For MSIX packaging |

### Getting Started

```bash
# Clone the repo
git clone <repo-url>

# Restore NuGet packages
cd ONEVO.Agent
dotnet restore

# Build all projects
dotnet build

# Run the service (in development, runs as console app)
cd ONEVO.Agent.Service
dotnet run

# Run the tray app (separate terminal)
cd ONEVO.Agent.TrayApp
dotnet run
```

### Development Without Backend

Use [[modules/agent-gateway/mock-mode|Mock Mode]] to develop the agent without needing the ONEVO backend server running. Set `"UseMockGateway": true` in `appsettings.Development.json`.

### Key Configuration Files

| File | Location | Purpose |
|:-----|:---------|:--------|
| `appsettings.json` | Service root | Production config (gateway URL, intervals) |
| `appsettings.Development.json` | Service root | Dev overrides (mock mode, verbose logging) |
| `Package.appxmanifest` | Installer project | MSIX identity, capabilities, version |

---

## Performance Budget

From [[AI_CONTEXT/rules|Rules]] Section 10:

| Metric | Limit |
|:-------|:------|
| CPU usage | < 2% sustained (< 5% during batch send) |
| Memory | < 50MB working set |
| Network | < 10KB per sync (compressed JSON) |
| SQLite buffer | Max 100MB |
| UI thread | Never blocked — all I/O on background threads |

---

## Related

- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — Full API contract (6 endpoints)
- [[modules/agent-gateway/data-collection|Data Collection]] — 5 collectors with code samples
- [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] — Detection and reporting
- [[modules/identity-verification/photo-capture|Photo Capture]] — Camera and identity verification flow
- [[modules/agent-gateway/ipc-protocol|Ipc Protocol]] — Named Pipes IPC between Service and TrayApp
- [[modules/agent-gateway/sqlite-buffer|Sqlite Buffer]] — Local SQLite buffer schema and operations
- [[modules/agent-gateway/agent-installer|Agent Installer]] — MSIX packaging and deployment
- [[modules/agent-gateway/mock-mode|Mock Mode]] — Development without a backend
- [[modules/agent-gateway/tray-app-ui|Tray App Ui]] — MAUI tray app UI
- [[AI_CONTEXT/tech-stack|Tech Stack]] — Full technology stack (Section 4: Desktop Agent)
- [[AI_CONTEXT/rules|Rules]] — Desktop Agent rules (Section 10)
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — Implementation task
- [[modules/agent-gateway/overview|Agent Gateway Module]] — Server-side module
