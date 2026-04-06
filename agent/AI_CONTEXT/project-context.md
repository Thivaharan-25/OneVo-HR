# Project Context: ONEVO Desktop Agent

## What It Is

The ONEVO Desktop Agent is a Windows application that runs on employee laptops to capture workforce activity data. It's part of the **Workforce Intelligence** pillar of the ONEVO platform.

## Two Components

### 1. Background Service (Windows Service)

Always-on data collector. Runs as a Windows Service (`Microsoft.Extensions.Hosting.WindowsServices`) — starts on boot, survives logoff, tamper-resistant.

**Captures:**
- Keyboard event counts (NOT keystrokes — just how many key presses)
- Mouse event counts
- Foreground application name + window title (hashed before sending)
- Idle periods (no input for configurable threshold)
- Meeting detection (Teams, Zoom, Meet process detection)
- Device active/idle cycles
- Camera/microphone activity status

### 2. Tray App (MAUI)

Minimal UI in the system tray. Provides:
- Employee login/logout (links employee identity to device)
- Photo capture for identity verification (when policy requires)
- Status indicator (connected/disconnected/syncing)
- "What's being tracked" transparency display (per privacy mode)
- Policy display (which features are active)

### IPC Between Components

Named Pipes (`System.IO.Pipes`) for communication between the Service and MAUI app:
- Service → MAUI: "capture photo now" (verification trigger), status updates
- MAUI → Service: employee login context, manual break start/end

## Data Flow

```
Capture → Local Buffer (SQLite) → Batch & Send → Agent Gateway
```

1. **Capture:** Win32 APIs collect raw activity data continuously
2. **Local Buffer:** SQLite stores data locally (handles offline/network issues)
3. **Batch:** Every 2-3 minutes (configurable via policy), batch buffered data
4. **Send:** POST to `/api/v1/agent/ingest` with Device JWT
5. **Server responds 202 Accepted** — processing is async on server side

## Policy-Driven Behavior

The agent does NOT decide what to track. It fetches its monitoring policy from the server:

```json
{
  "activity_monitoring": true,
  "application_tracking": true,
  "screenshot_capture": false,
  "meeting_detection": true,
  "device_tracking": true,
  "identity_verification": true,
  "verification_on_login": true,
  "verification_interval_minutes": 60,
  "idle_threshold_seconds": 300,
  "snapshot_interval_seconds": 150,
  "heartbeat_interval_seconds": 60
}
```

Policy is fetched on employee login and refreshed hourly. If a feature is `false`, the agent does NOT collect that data type.

## Authentication

The agent uses **Device JWT** — separate from user JWT:
- Issued at registration (`POST /api/v1/agent/register`)
- Contains `device_id` + `tenant_id` + `type: "agent"`
- NO user permissions — agent cannot access HR data
- Employee context is added when employee logs in via tray app

## Key Constraints

1. **Minimal resource footprint** — < 2% CPU, < 50MB RAM
2. **Network resilience** — buffer locally, retry with exponential backoff
3. **Privacy first** — only collect what policy allows, hash window titles
4. **Tamper resistant** — detect service stops, report to server
5. **Silent install** — MSIX package, no user interaction required
