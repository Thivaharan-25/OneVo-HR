# Agent Development Rules

## 1. Privacy & Security — NON-NEGOTIABLE

### What We Collect
- Keyboard **event counts** (how many key presses) — NOT keystrokes/content
- Mouse **event counts** — NOT coordinates or click targets
- Foreground application **name** — e.g., "Google Chrome"
- Window title — **hashed (SHA-256) before storage or transmission**
- Idle time (seconds since last input)
- Meeting app process detection (Teams.exe, zoom.exe)
- Camera/mic **active status** (boolean) — NOT audio/video content
- Device active/idle cycles

### What We NEVER Collect
- Keystroke content (what was typed)
- Mouse coordinates or click targets
- Window title plaintext (always hash)
- Screen content (unless screenshot feature is policy-enabled)
- Audio or video content
- File contents or file system browsing
- Network traffic content
- Browser history or URLs
- Clipboard content
- Email content

### Security Rules
1. **Device JWT stored via DPAPI** (Windows Data Protection API) — never plaintext
2. **All HTTP communication over HTTPS** — certificate pinning in production
3. **Local SQLite is encrypted** (SQLCipher or similar) — data at rest protection
4. **Log files never contain activity content** — only counts, statuses, errors
5. **Photo captures stored temporarily** — sent to server immediately, deleted locally after confirmation
6. **Tamper detection** — if service is stopped unexpectedly, report on next startup

## 2. Performance Rules

- **CPU usage < 2%** sustained (< 5% during batch send)
- **Memory < 50MB** working set
- **Network < 10KB per sync** (compressed JSON batches)
- **SQLite buffer max 100MB** — older unsent data dropped if buffer is full
- **No UI thread blocking** in MAUI app — all I/O on background threads

## 3. Network Resilience

```csharp
// HTTP client with Polly resilience
services.AddHttpClient<IAgentGatewayClient>("AgentGateway")
    .AddPolicyHandler(Policy
        .Handle<HttpRequestException>()
        .OrResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode && r.StatusCode != HttpStatusCode.Unauthorized)
        .WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt))))
    .AddPolicyHandler(Policy
        .Handle<HttpRequestException>()
        .CircuitBreakerAsync(5, TimeSpan.FromMinutes(2)));
```

- **Offline mode:** If server unreachable, keep buffering to SQLite. Sync when back online.
- **401 Unauthorized:** Stop syncing, show "re-registration needed" in tray app. Do NOT retry.
- **429 Too Many Requests:** Honor `Retry-After` header.
- **Server errors (5xx):** Exponential backoff with jitter (2s, 4s, 8s, max 30s).

## 4. Coding Standards

Follow the same conventions as the backend:
- **Async everywhere** with CancellationToken
- **Structured logging** via Serilog (file sink, rolling daily, max 7 days)
- **Dependency injection** via `Microsoft.Extensions.DependencyInjection`
- **Configuration** via `appsettings.json` + environment variables
- **No hardcoded values** — all thresholds come from server policy or local config

## 5. Policy Enforcement

```csharp
// Before collecting any data type, check policy
if (!_policy.ActivityMonitoring)
{
    _logger.LogDebug("Activity monitoring disabled by policy, skipping collection");
    return;
}
```

- **Check policy before every collection cycle** — not just at startup
- **Policy refresh:** On employee login + every 60 minutes
- **If policy fetch fails:** Use last known policy from SQLite cache
- **If no policy exists:** Collect NOTHING. Default is off.

## 6. IPC Protocol (Named Pipes)

Message format between Service and MAUI app:

```json
// Service → MAUI: Request photo capture
{"type": "capture_photo", "reason": "scheduled_verification", "requestId": "uuid"}

// MAUI → Service: Photo captured
{"type": "photo_captured", "requestId": "uuid", "photoPath": "C:\\temp\\verify.jpg"}

// MAUI → Service: Employee logged in
{"type": "employee_login", "employeeId": "uuid", "email": "user@company.com"}

// Service → MAUI: Status update
{"type": "status_update", "connected": true, "lastSync": "2026-04-05T10:30:00Z", "bufferedCount": 42}
```
