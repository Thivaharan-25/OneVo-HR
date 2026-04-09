# Agent Installer — MSIX Packaging & Deployment

## Overview

The ONEVO Desktop Agent is packaged as an **MSIX bundle** containing both the Windows Service and the MAUI Tray App. MSIX provides clean install/uninstall, auto-update support, and a signed package identity.

---

## MSIX Package Structure

```
ONEVO.Agent.msixbundle
├── ONEVO.Agent.Service.exe        # Windows Service binary
├── ONEVO.Agent.TrayApp.exe        # MAUI tray app binary
├── ONEVO.Agent.Shared.dll         # Shared types library
├── appsettings.json               # Default configuration
├── Assets/
│   ├── tray-icon-default.ico
│   ├── tray-icon-connected.ico
│   ├── tray-icon-error.ico
│   └── logo.png
├── Package.appxmanifest            # Package identity, capabilities
└── [.NET runtime files]            # Self-contained or framework-dependent
```

### Package.appxmanifest — Key Settings

```xml
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:desktop="http://schemas.microsoft.com/appx/manifest/desktop/windows10"
         xmlns:desktop6="http://schemas.microsoft.com/appx/manifest/desktop/windows10/6">

  <Identity Name="ONEVO.Agent"
            Publisher="CN=ONEVO"
            Version="1.0.0.0"
            ProcessorArchitecture="x64" />

  <Properties>
    <DisplayName>ONEVO Desktop Agent</DisplayName>
    <PublisherDisplayName>ONEVO</PublisherDisplayName>
  </Properties>

  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
  </Capabilities>

  <Applications>
    <!-- Tray App — user-facing, starts on login -->
    <Application Id="TrayApp"
                 Executable="ONEVO.Agent.TrayApp.exe"
                 EntryPoint="Windows.FullTrustApplication">
      <desktop:Extension Category="windows.startupTask">
        <desktop:StartupTask TaskId="ONEVOTrayApp" Enabled="true"
                             DisplayName="ONEVO Agent" />
      </desktop:Extension>
    </Application>

    <!-- Windows Service — background, runs always -->
    <Application Id="Service"
                 Executable="ONEVO.Agent.Service.exe"
                 EntryPoint="Windows.FullTrustApplication">
      <desktop6:Extension Category="windows.service">
        <desktop6:Service Name="ONEVO.Agent.Service"
                          StartupType="auto"
                          StartAccount="localSystem" />
      </desktop6:Extension>
    </Application>
  </Applications>
</Package>
```

---

## Installation

### Silent Install (IT Admin Deployment)

```powershell
# Install via PowerShell (no user interaction)
Add-AppxPackage -Path "\\fileserver\agents\ONEVO.Agent.msixbundle" -ForceApplicationShutdown

# Or via command line
powershell -Command "Add-AppxPackage -Path 'C:\Deploy\ONEVO.Agent.msixbundle'"
```

### MDM / Group Policy Deployment

For enterprise deployment via Microsoft Intune, SCCM, or Group Policy:

1. Upload the `.msixbundle` to the MDM console
2. Assign to device groups
3. The package installs silently — no user interaction required
4. The Windows Service starts automatically
5. The Tray App starts on next user login (via startup task)

### Prerequisites

| Requirement | Details |
|:------------|:--------|
| Windows version | Windows 10 (1809+) or Windows 11 |
| .NET Runtime | .NET 9 Desktop Runtime (bundled in self-contained package, or pre-installed for framework-dependent) |
| Architecture | x64 only (no ARM64 in Phase 1) |
| Permissions | Admin rights for install (or MDM-pushed) |
| Network | HTTPS access to `agent.onevo.app` (Agent Gateway) |

---

## First-Run Flow

```
Install completes
  → Windows Service starts automatically
  → Service generates device_id (UUID v7)
  → Service reads tenant API key from appsettings.json or registry
  → Service calls POST /api/v1/agent/register
  → Server returns device JWT + agent_id
  → Service stores device JWT via DPAPI (see [[modules/agent-gateway/sqlite-buffer|Sqlite Buffer]] agent_config table)
  → Service begins heartbeat loop (every 60s)
  → User logs in to Windows
  → Tray App starts (startup task)
  → Tray App connects to Service via Named Pipe (see [[modules/agent-gateway/ipc-protocol|Ipc Protocol]])
  → Tray App shows login prompt
  → Employee enters email + password
  → Service calls POST /api/v1/agent/login
  → Collectors start based on received policy
```

### Tenant API Key Provisioning

The tenant API key must be provided during installation. Options:

1. **Baked into appsettings.json** — pre-configured package per tenant
2. **Registry key** — set by MDM/GPO before install: `HKLM\SOFTWARE\ONEVO\Agent\TenantApiKey`
3. **Command-line parameter** — via provisioning script after install

```csharp
// Reading tenant API key (priority order)
var tenantApiKey = 
    Environment.GetEnvironmentVariable("ONEVO_TENANT_API_KEY")
    ?? Registry.GetValue(@"HKEY_LOCAL_MACHINE\SOFTWARE\ONEVO\Agent", "TenantApiKey", null) as string
    ?? _configuration["TenantApiKey"]
    ?? throw new InvalidOperationException("No tenant API key configured");
```

---

## Windows Service Registration

The MSIX package handles service registration automatically via the `desktop6:Service` extension in the manifest. For development or non-MSIX scenarios:

```powershell
# Register the service manually (development only)
sc.exe create "ONEVO.Agent.Service" binPath="C:\path\to\ONEVO.Agent.Service.exe" start=auto

# Configure service recovery (restart on failure)
sc.exe failure "ONEVO.Agent.Service" reset= 86400 actions= restart/5000/restart/10000/restart/30000

# Start the service
sc.exe start "ONEVO.Agent.Service"
```

See [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] for the recovery configuration details (1st failure: 5s, 2nd: 10s, 3rd: 30s).

---

## Auto-Update Strategy

The agent checks for updates via the heartbeat response from the server.

### How It Works

1. Agent sends heartbeat every 60 seconds (see [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]])
2. Server compares `agent_version` in heartbeat with the latest available version
3. If an update is available, the heartbeat response includes:

```json
{
  "status": "ok",
  "update_available": true,
  "update_url": "https://agent.onevo.app/updates/ONEVO.Agent.1.1.0.msixbundle",
  "update_version": "1.1.0",
  "update_required": false
}
```

4. Agent downloads the update package in the background
5. Agent applies the update at the next idle period (or immediately if `update_required` is true)

### Update Application

```csharp
public class AutoUpdateService
{
    public async Task CheckAndApplyUpdateAsync(HeartbeatResponse response, CancellationToken ct)
    {
        if (!response.UpdateAvailable || response.UpdateUrl == null)
            return;

        _logger.LogInformation("Update available: v{Version}", response.UpdateVersion);

        // Download to temp location
        var tempPath = Path.Combine(Path.GetTempPath(), $"onevo_update_{response.UpdateVersion}.msixbundle");
        await _httpClient.DownloadFileAsync(response.UpdateUrl, tempPath, ct);

        // Verify package signature before installing
        // MSIX packages must be signed with the ONEVO certificate

        if (response.UpdateRequired)
        {
            // Critical update — apply immediately
            await ApplyUpdateAsync(tempPath, ct);
        }
        else
        {
            // Non-critical — schedule for next idle period
            _pendingUpdatePath = tempPath;
        }
    }

    private async Task ApplyUpdateAsync(string msixPath, CancellationToken ct)
    {
        // Flush buffer before update
        await _syncService.FlushBufferAsync(ct);

        // Install update (MSIX handles in-place upgrade)
        var process = Process.Start(new ProcessStartInfo
        {
            FileName = "powershell",
            Arguments = $"-Command \"Add-AppxPackage -Path '{msixPath}' -ForceApplicationShutdown\"",
            UseShellExecute = false,
            CreateNoWindow = true
        });

        await process!.WaitForExitAsync(ct);
    }
}
```

### Update Safety Rules

- Always flush the SQLite buffer before applying an update
- Verify MSIX package signature before installing
- If update fails, continue running the current version
- Report update failures in the next heartbeat

---

## Uninstall Behavior

### Clean Uninstall

```powershell
# Uninstall via PowerShell
Get-AppxPackage "ONEVO.Agent" | Remove-AppxPackage

# Or via Windows Settings → Apps → ONEVO Desktop Agent → Uninstall
```

### What Happens on Uninstall

1. MSIX triggers pre-uninstall — Service receives shutdown signal
2. Service marks a clean shutdown (see [[modules/agent-gateway/tamper-resistance|Tamper Resistance]])
3. Service flushes remaining buffer to server (best-effort)
4. Service sends a final heartbeat with `"uninstalling": true`
5. MSIX removes all application files
6. Local data (`%LOCALAPPDATA%\ONEVO\Agent\`) is removed by MSIX
7. Server detects missing heartbeat after 5 minutes, fires `AgentHeartbeatLost` event
8. Admin sees "Agent Offline" status in the ONEVO dashboard

### Data After Uninstall

- All local data (SQLite buffer, config, logs) is deleted with the MSIX package
- Any unsent data in the buffer is lost (best-effort flush before uninstall)
- Server-side data (activity records already synced) is retained per [[modules/configuration/retention-policies/overview|Retention Policies]]

---

## Build & Package

```bash
# Build the MSIX package (from the solution root)
dotnet publish ONEVO.Agent.Service -c Release -r win-x64
dotnet publish ONEVO.Agent.TrayApp -c Release -r win-x64

# Create MSIX package (Visual Studio or makeappx)
makeappx pack /d .\publish\ /p ONEVO.Agent.msixbundle

# Sign the package (required for installation)
signtool sign /fd SHA256 /a /f certificate.pfx /p password ONEVO.Agent.msixbundle
```

---

## Related

- [[modules/agent-gateway/agent-overview|Agent Overview]] — Architecture overview and first-run flow
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — Registration endpoint and heartbeat (update_available)
- [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] — Service recovery configuration and clean shutdown
- [[modules/agent-gateway/sqlite-buffer|Sqlite Buffer]] — Local data that is cleaned up on uninstall
- [[modules/agent-gateway/ipc-protocol|Ipc Protocol]] — Service-TrayApp communication
- [[modules/agent-gateway/tray-app-ui|Tray App Ui]] — TrayApp that starts on login
- [[AI_CONTEXT/rules|Rules]] — Desktop Agent rules (Section 10)
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — Implementation task
