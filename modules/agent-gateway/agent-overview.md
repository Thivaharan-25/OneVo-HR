# Desktop Agent — Start Here

## What Is the ONEVO Desktop Agent?

The ONEVO Desktop Agent is a Windows application that monitors employee activity on company devices. It consists of three components:

| Component | Project | Purpose |
|:----------|:--------|:--------|
| **Windows Service** | `ONEVO.Agent.Service` | Always-on background data collector. Runs as a Windows Service. Captures activity data, buffers locally, syncs to server. |
| **MAUI Tray App** | `ONEVO.Agent.TrayApp` | System tray UI. Handles employee login/logout, photo capture for identity verification, status display. |
| **Shared Library** | `ONEVO.Agent.Shared` | Shared types (IPC messages, models, constants) used by both Service and TrayApp. |

The Service and TrayApp are separate processes that communicate via **Named Pipes** (IPC). See [[ipc-protocol]] for the full message contract.

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

1. **Install** — MSIX package installs the Service + TrayApp. Service registers with the server via `POST /api/v1/agent/register`, receives a device JWT. See [[agent-installer]].
2. **Employee Login** — Employee opens tray app, enters email + password. TrayApp sends `employee_login` IPC message to Service. Service calls `POST /api/v1/agent/login`, receives monitoring policy. See [[agent-server-protocol]].
3. **Collectors Start** — Based on the received policy, the Service starts the enabled collectors (activity, app tracking, idle, meeting, device). See [[data-collection]].
4. **Buffer Locally** — Collected data is written to the local SQLite buffer immediately. See [[sqlite-buffer]].
5. **Sync to Server** — Every `snapshot_interval_seconds` (default 150s), the Sync Service reads unsent rows from the buffer, batches them, and sends via `POST /api/v1/agent/ingest`. Server returns 202 Accepted.
6. **Heartbeat** — Every 60 seconds, the Service sends a heartbeat to `POST /api/v1/agent/heartbeat` with CPU usage, memory, buffer count, and any errors.
7. **Identity Verification** — When the policy triggers a verification (login, interval, or logout), the Service sends `capture_photo` via IPC to the TrayApp. See [[photo-capture]].
8. **Employee Logout** — Employee clicks logout in TrayApp. Service calls `POST /api/v1/agent/logout`. Collectors stop. Service continues heartbeating.

---

## Reading Order

Read these docs in this order to understand the full agent system:

| # | Document | What You Learn |
|:--|:---------|:---------------|
| 1 | **This file** (`agent-overview`) | Architecture, data flow, setup |
| 2 | [[agent-server-protocol]] | All 6 API endpoints (register, login, policy, heartbeat, ingest, logout) |
| 3 | [[data-collection]] | 5 collectors with Win32 P/Invoke code samples |
| 4 | [[ipc-protocol]] | Named Pipes messages between Service and TrayApp |
| 5 | [[sqlite-buffer]] | Local SQLite schema, offline resilience, encryption |
| 6 | [[tamper-resistance]] | Detection and reporting of service manipulation |
| 7 | [[photo-capture]] | Camera capture and identity verification flow |
| 8 | [[tray-app-ui]] | MAUI tray app UI: login, status, photo capture, notifications |
| 9 | [[agent-installer]] | MSIX packaging, silent install, auto-update |
| 10 | [[mock-mode]] | Development without a backend server |

Also read:
- [[rules]] (Section 10) — Privacy rules, performance budgets, coding standards
- [[tech-stack]] (Section 4) — NuGet packages, Win32 APIs, project structure

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

Full structure also documented in [[tech-stack]] Section 4.

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

Use [[mock-mode]] to develop the agent without needing the ONEVO backend server running. Set `"UseMockGateway": true` in `appsettings.Development.json`.

### Key Configuration Files

| File | Location | Purpose |
|:-----|:---------|:--------|
| `appsettings.json` | Service root | Production config (gateway URL, intervals) |
| `appsettings.Development.json` | Service root | Dev overrides (mock mode, verbose logging) |
| `Package.appxmanifest` | Installer project | MSIX identity, capabilities, version |

---

## Performance Budget

From [[rules]] Section 10:

| Metric | Limit |
|:-------|:------|
| CPU usage | < 2% sustained (< 5% during batch send) |
| Memory | < 50MB working set |
| Network | < 10KB per sync (compressed JSON) |
| SQLite buffer | Max 100MB |
| UI thread | Never blocked — all I/O on background threads |

---

## Related

- [[agent-server-protocol]] — Full API contract (6 endpoints)
- [[data-collection]] — 5 collectors with code samples
- [[tamper-resistance]] — Detection and reporting
- [[photo-capture]] — Camera and identity verification flow
- [[ipc-protocol]] — Named Pipes IPC between Service and TrayApp
- [[sqlite-buffer]] — Local SQLite buffer schema and operations
- [[agent-installer]] — MSIX packaging and deployment
- [[mock-mode]] — Development without a backend
- [[tray-app-ui]] — MAUI tray app UI
- [[tech-stack]] — Full technology stack (Section 4: Desktop Agent)
- [[rules]] — Desktop Agent rules (Section 10)
- [[WEEK1-shared-platform]] — Implementation task
- [[agent-gateway|Agent Gateway Module]] — Server-side module
