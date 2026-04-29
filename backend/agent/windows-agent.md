# ONEVO Windows Agent

**Last Updated:** 2026-04-27
**Platform:** Windows 10/11

## Capture capabilities

| Capability | Windows API | Frequency |
|---|---|---|
| Screenshot | GDI+ `Graphics.CopyFromScreen` / `PrintWindow` | Configurable via AgentPolicy |
| Active app | `GetForegroundWindow` + `Process.GetProcessById` | Every 30s (default) |
| Browser activity | Chrome/Edge DevTools Protocol or extension | On navigation |
| Keyboard/mouse activity | Low-level hooks (presence only, no keylogging) | Continuous |

## Tray app

`ONEVO.Agent.Windows/Tray/SystemTrayIcon.cs` — uses `System.Windows.Forms.NotifyIcon`

Context menu items:
- Status (Connected / Offline)
- Pause monitoring (requires manager approval token)
- About / version
- Exit (requires IT PIN)

## Offline queue

`SQLiteOfflineQueue.cs` — SQLite database at `%APPDATA%\ONEVO\Agent\queue.db`

- Stores `ActivitySnapshot` records when network is unavailable
- Replays on reconnect in chronological order
- Max queue size: 72 hours of data (configurable)

## Auto-update

`AgentUpdater.cs` polls `AgentGateway` on startup and every 4 hours:
1. Calls `GET /api/v1/agent/version-check` with current version
2. If new version available in assigned deployment ring → downloads installer
3. Applies update on next Windows restart (MSI silent install)

Deployment rings: `Canary → Beta → Stable` — managed via DevPlatform admin console.

## Machine token storage

```csharp
// Stored in Windows Credential Manager
CredentialManager.WriteCredential(
    "ONEVO-Agent",
    Environment.MachineName,
    machineToken);

// Read on startup
var token = CredentialManager.ReadCredential("ONEVO-Agent")?.Password;
```

## Host setup (Program.cs)

```csharp
var host = Host.CreateDefaultBuilder(args)
    .UseWindowsService()           // runs as Windows Service
    .ConfigureServices(services =>
    {
        services.AddSingleton<IScreenshotCapture, WindowsScreenshotCapture>();
        services.AddSingleton<IAppUsageCapture, WindowsAppUsageCapture>();
        services.AddSingleton<IOfflineQueue, SQLiteOfflineQueue>();
        services.AddSingleton<IAgentApiClient, AgentApiClient>();
        services.AddHostedService<CaptureSchedulerService>();
        services.AddHostedService<SyncService>();
        services.AddHostedService<PolicySyncService>();
    })
    .Build();

await host.RunAsync();
```
