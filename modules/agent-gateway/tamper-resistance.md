# Tamper Resistance

## Detection Strategy

The agent detects and reports attempts to disable or manipulate the monitoring service.

### What We Detect

| Tamper Type | Detection Method | Severity |
|:------------|:----------------|:---------|
| Service stopped | Service recovery + startup detection | Critical |
| Service uninstalled | Missing heartbeat (server-side) | Critical |
| Process killed | Windows Service recovery (restart on failure) | High |
| Clock manipulation | Server timestamp comparison | Medium |
| Network blocking | Heartbeat failure pattern | Medium |

### Service Recovery

Windows Service configured with automatic recovery:

```csharp
// Configured in installer
sc.exe failure "ONEVO.Agent.Service" reset= 86400 actions= restart/5000/restart/10000/restart/30000
```

- 1st failure: Restart after 5 seconds
- 2nd failure: Restart after 10 seconds
- 3rd failure: Restart after 30 seconds
- Reset failure count after 24 hours

### Startup Tamper Check

On service startup, check if the last shutdown was clean:

```csharp
public class TamperDetector
{
    private const string CleanShutdownFile = "clean_shutdown.flag";
    
    public async Task<TamperReport> CheckOnStartupAsync()
    {
        var report = new TamperReport();
        
        // Check if clean shutdown flag exists
        if (!File.Exists(CleanShutdownFile))
        {
            report.UncleanShutdown = true;
            report.LastKnownTime = await GetLastBufferedTimestampAsync();
        }
        
        // Check for time manipulation
        var serverTime = await _gatewayClient.GetServerTimeAsync();
        var localTime = DateTimeOffset.UtcNow;
        if (Math.Abs((serverTime - localTime).TotalMinutes) > 5)
        {
            report.ClockSkew = true;
            report.SkewMinutes = (serverTime - localTime).TotalMinutes;
        }
        
        return report;
    }
    
    public void MarkCleanShutdown()
    {
        File.WriteAllText(CleanShutdownFile, DateTimeOffset.UtcNow.ToString("O"));
    }
}
```

### Reporting

Tamper events are included in the heartbeat payload:

```json
{
  "device_id": "uuid",
  "tamper_detected": true,
  "tamper_details": {
    "unclean_shutdown": true,
    "last_known_time": "2026-04-05T10:25:00Z",
    "restart_time": "2026-04-05T10:30:00Z",
    "gap_minutes": 5
  }
}
```

Server-side, the `AgentHeartbeatLost` event + tamper report triggers an exception alert via [[exception-engine]].

## What We Do NOT Do

- **No rootkit-style hiding** — the agent is visible in Task Manager and Services
- **No anti-uninstall** — admins can uninstall via MSIX. Missing heartbeat alerts the server.
- **No kernel-level protection** — user-mode service only
- **No BIOS/firmware anchoring** — MSIX packaging is sufficient

The goal is **detection and reporting**, not prevention. If someone disables the agent, the server knows about it.
