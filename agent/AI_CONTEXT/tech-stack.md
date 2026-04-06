# Technology Stack: ONEVO Desktop Agent

## Core Technologies

| Category | Technology | Version | Notes |
|:---------|:-----------|:--------|:------|
| Background Service | .NET Windows Service | 9.0 | `Microsoft.Extensions.Hosting.WindowsServices` |
| Tray App UI | .NET MAUI | 9.0 | System tray icon, photo capture, employee login |
| Language | C# | 13 | Same as backend |
| Local Storage | SQLite | via `Microsoft.Data.Sqlite` | Offline buffer for activity data |
| HTTP Client | HttpClient + Polly | Built-in | Retry + circuit breaker for Agent Gateway |
| IPC | Named Pipes | `System.IO.Pipes` | Service ↔ MAUI tray app communication |
| Installer | MSIX | Windows SDK | Silent install, auto-update |

## Win32 APIs (P/Invoke)

| API | DLL | Purpose |
|:----|:----|:--------|
| `SetWindowsHookEx` | user32.dll | Keyboard/mouse event COUNTING (not keylogging) |
| `GetForegroundWindow` | user32.dll | Active window detection |
| `GetWindowText` | user32.dll | Window title capture (hashed before storage) |
| `GetLastInputInfo` | user32.dll | Idle detection (time since last input) |
| `EnumProcesses` / `Process.GetProcesses()` | kernel32.dll / .NET | Process enumeration for meeting detection |

## NuGet Dependencies

| Package | Purpose |
|:--------|:--------|
| `Microsoft.Extensions.Hosting.WindowsServices` | Windows Service hosting |
| `Microsoft.Data.Sqlite` | SQLite local buffer |
| `Polly` | HTTP resilience (retry, circuit breaker, timeout) |
| `System.Text.Json` | JSON serialization |
| `Serilog` + `Serilog.Sinks.File` | Local logging (rolling file) |
| `CommunityToolkit.Maui` | MAUI helpers (tray icon, notifications) |

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
│   └── Program.cs                 # Service entry point
│
├── ONEVO.Agent.TrayApp/           # MAUI tray app
│   ├── Views/
│   │   ├── LoginWindow.xaml       # Employee login
│   │   ├── StatusPopup.xaml       # Status display
│   │   └── PhotoCaptureWindow.xaml # Verification photo capture
│   ├── Services/
│   │   ├── NamedPipeClient.cs     # Connect to Service
│   │   ├── CameraService.cs       # Camera access for verification
│   │   └── TrayIconService.cs     # System tray management
│   └── App.xaml.cs
│
├── ONEVO.Agent.Shared/            # Shared types between Service and TrayApp
│   ├── Models/
│   │   ├── ActivitySnapshot.cs
│   │   ├── AppUsageRecord.cs
│   │   ├── DeviceSession.cs
│   │   └── AgentPolicy.cs
│   ├── IPC/
│   │   └── IpcMessages.cs         # Named pipe message types
│   └── Constants.cs
│
└── ONEVO.Agent.Installer/         # MSIX packaging
    └── Package.appxmanifest
```
