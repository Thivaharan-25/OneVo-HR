# IPC Protocol — Named Pipes

## Overview

The Windows Service (`ONEVO.Agent.Service`) and the MAUI Tray App (`ONEVO.Agent.TrayApp`) are separate processes that communicate via **Named Pipes** using `System.IO.Pipes`.

- **Pipe name:** `onevo-agent-ipc`
- **Transport:** JSON-encoded messages over a named pipe stream
- **Direction:** Bidirectional — both sides can send messages
- **Architecture:** The Service hosts the `NamedPipeServerStream`. The TrayApp connects as a `NamedPipeClientStream`.

---

## Message Format

All IPC messages are JSON objects with a `type` field discriminator, followed by a newline (`\n`) delimiter. Messages are defined in `ONEVO.Agent.Shared/IPC/IpcMessages.cs`.

```csharp
// ONEVO.Agent.Shared/IPC/IpcMessages.cs

public abstract record IpcMessage
{
    public abstract string Type { get; }
    public string MessageId { get; init; } = Guid.NewGuid().ToString();
    public DateTimeOffset Timestamp { get; init; } = DateTimeOffset.UtcNow;
}
```

### Serialization

```csharp
// Serialize
var json = JsonSerializer.Serialize<IpcMessage>(message, IpcJsonOptions.Default);

// Deserialize (type discriminator)
var doc = JsonDocument.Parse(line);
var type = doc.RootElement.GetProperty("type").GetString();
IpcMessage message = type switch
{
    "employee_login"      => JsonSerializer.Deserialize<EmployeeLoginMessage>(line)!,
    "employee_logout"     => JsonSerializer.Deserialize<EmployeeLogoutMessage>(line)!,
    "photo_captured"      => JsonSerializer.Deserialize<PhotoCapturedMessage>(line)!,
    "get_status"          => JsonSerializer.Deserialize<GetStatusMessage>(line)!,
    "capture_photo"       => JsonSerializer.Deserialize<CapturePhotoMessage>(line)!,
    "status_update"       => JsonSerializer.Deserialize<StatusUpdateMessage>(line)!,
    "policy_updated"      => JsonSerializer.Deserialize<PolicyUpdatedMessage>(line)!,
    "verification_result" => JsonSerializer.Deserialize<VerificationResultMessage>(line)!,
    _ => throw new InvalidOperationException($"Unknown IPC message type: {type}")
};

// JSON options — camelCase, enums as strings
public static class IpcJsonOptions
{
    public static readonly JsonSerializerOptions Default = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        Converters = { new JsonStringEnumConverter() },
        WriteIndented = false
    };
}
```

---

## Messages: TrayApp to Service

### `employee_login`

Sent when employee enters credentials in the login window.

```json
{
  "type": "employee_login",
  "messageId": "uuid",
  "timestamp": "2026-04-05T10:00:00Z",
  "email": "user@company.com",
  "password": "..."
}
```

**What the Service does after receiving this:**
1. Authenticates the employee against ONEVO (`POST /api/v1/auth/login`)
2. Calls `POST /api/v1/agent/session/login` with the Device JWT to create a server-side `agent_sessions` record (`device_id → employee_id`)
3. Stores the employee context locally (for ingest payload construction)
4. Sends `status_update` back to TrayApp with the result (success or error message)

This server-side session record is what the ingest endpoint uses to validate `employee_id` in payloads. See [[modules/agent-gateway/data-collection|Data Collection — Employee-Device Binding]].

```csharp
public record EmployeeLoginMessage : IpcMessage
{
    public override string Type => "employee_login";
    public required string Email { get; init; }
    public required string Password { get; init; }
}
```

**Service action:** Calls `POST /api/v1/agent/login` with the credentials. On success, starts collectors based on the received policy. Sends `status_update` back to TrayApp.

**Security:** Password is transmitted over the local named pipe (same machine, same user session). The Service sends it to the server over HTTPS and does NOT persist it locally.

### `employee_logout`

Sent when employee clicks logout in the tray app.

```json
{
  "type": "employee_logout",
  "messageId": "uuid",
  "timestamp": "2026-04-05T18:00:00Z"
}
```

```csharp
public record EmployeeLogoutMessage : IpcMessage
{
    public override string Type => "employee_logout";
}
```

**Service action:** Stops collectors, flushes remaining buffer to server, calls `POST /api/v1/agent/logout`. Sends `status_update` back.

### `photo_captured`

Sent after the MAUI app captures a verification photo.

```json
{
  "type": "photo_captured",
  "messageId": "uuid",
  "timestamp": "2026-04-05T10:15:00Z",
  "requestId": "original-capture-request-uuid",
  "photoPath": "C:\\Users\\user\\AppData\\Local\\Temp\\onevo_verify_abc123.jpg",
  "skipped": false
}
```

```csharp
public record PhotoCapturedMessage : IpcMessage
{
    public override string Type => "photo_captured";
    public required string RequestId { get; init; }
    public string? PhotoPath { get; init; }
    public bool Skipped { get; init; }
}
```

**Service action:** If `skipped == false`, reads the photo file, uploads it to the server via the ingest endpoint with `type: "verification_photo"`. Deletes the local file after successful upload. If `skipped == true`, reports the skip to the server.

See [[modules/identity-verification/photo-capture|Photo Capture]] for the full verification flow.

### `get_status`

Sent when the user opens the status popup in the tray app.

```json
{
  "type": "get_status",
  "messageId": "uuid",
  "timestamp": "2026-04-05T10:30:00Z"
}
```

```csharp
public record GetStatusMessage : IpcMessage
{
    public override string Type => "get_status";
}
```

**Service action:** Responds with a `status_update` message containing current state.

---

## Messages: Service to TrayApp

### `capture_photo`

Sent when the policy triggers identity verification (on login, on interval, or on logout).

```json
{
  "type": "capture_photo",
  "messageId": "uuid",
  "timestamp": "2026-04-05T10:15:00Z",
  "requestId": "uuid",
  "reason": "scheduled_verification"
}
```

```csharp
public record CapturePhotoMessage : IpcMessage
{
    public override string Type => "capture_photo";
    public required string RequestId { get; init; }
    public required string Reason { get; init; } // "login_verification", "scheduled_verification", "logout_verification"
}
```

**TrayApp action:** Opens the photo capture window. After capture (or skip/timeout), sends `photo_captured` back with the matching `requestId`.

### `status_update`

Sent in response to `get_status`, after login/logout, or periodically when state changes.

```json
{
  "type": "status_update",
  "messageId": "uuid",
  "timestamp": "2026-04-05T10:30:00Z",
  "connected": true,
  "employeeLoggedIn": true,
  "employeeName": "John Doe",
  "lastSync": "2026-04-05T10:28:00Z",
  "bufferedCount": 42,
  "collectors": {
    "activity": "running",
    "appTracker": "running",
    "idle": "running",
    "meeting": "running",
    "device": "running"
  },
  "errors": []
}
```

```csharp
public record StatusUpdateMessage : IpcMessage
{
    public override string Type => "status_update";
    public bool Connected { get; init; }
    public bool EmployeeLoggedIn { get; init; }
    public string? EmployeeName { get; init; }
    public DateTimeOffset? LastSync { get; init; }
    public int BufferedCount { get; init; }
    public Dictionary<string, string> Collectors { get; init; } = new();
    public List<string> Errors { get; init; } = new();
}
```

**TrayApp action:** Updates the status popup UI and tray icon state.

### `policy_updated`

Sent when the Service receives a new policy from the server (on login or periodic policy sync).

```json
{
  "type": "policy_updated",
  "messageId": "uuid",
  "timestamp": "2026-04-05T10:00:00Z",
  "policy": {
    "activity_monitoring": true,
    "application_tracking": true,
    "screenshot_capture": false,
    "meeting_detection": true,
    "device_tracking": true,
    "identity_verification": true,
    "verification_interval_minutes": 60,
    "idle_threshold_seconds": 300,
    "snapshot_interval_seconds": 150
  }
}
```

```csharp
public record PolicyUpdatedMessage : IpcMessage
{
    public override string Type => "policy_updated";
    public required AgentPolicy Policy { get; init; }
}
```

**TrayApp action:** Updates local display of what is being monitored (used in transparency mode to inform the user).

### `verification_result`

Sent after the server processes a photo verification.

```json
{
  "type": "verification_result",
  "messageId": "uuid",
  "timestamp": "2026-04-05T10:16:00Z",
  "requestId": "original-capture-request-uuid",
  "result": "verified",
  "message": "Identity verified successfully"
}
```

```csharp
public record VerificationResultMessage : IpcMessage
{
    public override string Type => "verification_result";
    public required string RequestId { get; init; }
    public required string Result { get; init; } // "verified", "failed", "error"
    public string? Message { get; init; }
}
```

**TrayApp action:** Shows a toast notification with the result. If `failed`, may prompt for re-capture depending on policy.

---

## NamedPipeServer — Service Side

```csharp
// ONEVO.Agent.Service/IPC/NamedPipeServer.cs

public class NamedPipeServer : BackgroundService
{
    private const string PipeName = "onevo-agent-ipc";
    private readonly ILogger<NamedPipeServer> _logger;
    private readonly IServiceProvider _serviceProvider;

    public NamedPipeServer(ILogger<NamedPipeServer> logger, IServiceProvider serviceProvider)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await using var pipeServer = new NamedPipeServerStream(
                    PipeName,
                    PipeDirection.InOut,
                    maxNumberOfServerInstances: 1,
                    PipeTransmissionMode.Byte,
                    PipeOptions.Asynchronous);

                _logger.LogDebug("Waiting for TrayApp connection on pipe {PipeName}", PipeName);
                await pipeServer.WaitForConnectionAsync(stoppingToken);
                _logger.LogInformation("TrayApp connected via named pipe");

                await HandleConnectionAsync(pipeServer, stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (IOException ex)
            {
                _logger.LogWarning(ex, "Pipe connection lost, waiting for reconnection");
                await Task.Delay(1000, stoppingToken); // Brief delay before re-listening
            }
        }
    }

    private async Task HandleConnectionAsync(NamedPipeServerStream pipe, CancellationToken ct)
    {
        using var reader = new StreamReader(pipe, leaveOpen: true);
        using var writer = new StreamWriter(pipe, leaveOpen: true) { AutoFlush = true };

        try
        {
            while (pipe.IsConnected && !ct.IsCancellationRequested)
            {
                var line = await reader.ReadLineAsync(ct);
                if (line == null) break; // Client disconnected

                var message = IpcMessageSerializer.Deserialize(line);
                var response = await ProcessMessageAsync(message, ct);

                if (response != null)
                {
                    var json = IpcMessageSerializer.Serialize(response);
                    await writer.WriteLineAsync(json);
                }
            }
        }
        catch (IOException)
        {
            _logger.LogWarning("TrayApp disconnected");
        }
    }

    private async Task<IpcMessage?> ProcessMessageAsync(IpcMessage message, CancellationToken ct)
    {
        return message switch
        {
            EmployeeLoginMessage login => await HandleLoginAsync(login, ct),
            EmployeeLogoutMessage logout => await HandleLogoutAsync(logout, ct),
            PhotoCapturedMessage photo => await HandlePhotoCapturedAsync(photo, ct),
            GetStatusMessage => await GetCurrentStatusAsync(ct),
            _ => null
        };
    }

    // Send a message to TrayApp (e.g., capture_photo) — call from other services
    public async Task SendToTrayAppAsync(IpcMessage message, CancellationToken ct)
    {
        // Implementation: write to the active pipe connection's writer
        // Store the StreamWriter reference when connection is established
    }
}
```

---

## NamedPipeClient — TrayApp Side

```csharp
// ONEVO.Agent.TrayApp/Services/NamedPipeClient.cs

public class NamedPipeClient : IAsyncDisposable
{
    private const string PipeName = "onevo-agent-ipc";
    private const int ReconnectDelayMs = 2000;
    private readonly ILogger<NamedPipeClient> _logger;
    private NamedPipeClientStream? _pipeClient;
    private StreamReader? _reader;
    private StreamWriter? _writer;
    private CancellationTokenSource? _cts;

    public event Func<IpcMessage, Task>? OnMessageReceived;
    public bool IsConnected => _pipeClient?.IsConnected ?? false;

    public NamedPipeClient(ILogger<NamedPipeClient> logger)
    {
        _logger = logger;
    }

    public async Task ConnectAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            try
            {
                _pipeClient = new NamedPipeClientStream(
                    ".",
                    PipeName,
                    PipeDirection.InOut,
                    PipeOptions.Asynchronous);

                await _pipeClient.ConnectAsync(5000, ct); // 5 second timeout
                _reader = new StreamReader(_pipeClient, leaveOpen: true);
                _writer = new StreamWriter(_pipeClient, leaveOpen: true) { AutoFlush = true };

                _logger.LogInformation("Connected to Service via named pipe");
                _cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                _ = ListenForMessagesAsync(_cts.Token); // Fire and forget
                return;
            }
            catch (TimeoutException)
            {
                _logger.LogWarning("Service not available, retrying in {Delay}ms", ReconnectDelayMs);
                await Task.Delay(ReconnectDelayMs, ct);
            }
            catch (IOException ex)
            {
                _logger.LogWarning(ex, "Pipe connection failed, retrying in {Delay}ms", ReconnectDelayMs);
                await Task.Delay(ReconnectDelayMs, ct);
            }
        }
    }

    public async Task SendAsync(IpcMessage message, CancellationToken ct)
    {
        if (_writer == null || !IsConnected)
            throw new InvalidOperationException("Not connected to service");

        var json = IpcMessageSerializer.Serialize(message);
        await _writer.WriteLineAsync(json.AsMemory(), ct);
    }

    private async Task ListenForMessagesAsync(CancellationToken ct)
    {
        try
        {
            while (!ct.IsCancellationRequested && _reader != null)
            {
                var line = await _reader.ReadLineAsync(ct);
                if (line == null) break;

                var message = IpcMessageSerializer.Deserialize(line);
                if (OnMessageReceived != null)
                    await OnMessageReceived.Invoke(message);
            }
        }
        catch (IOException)
        {
            _logger.LogWarning("Lost connection to Service, attempting reconnect");
        }

        // Auto-reconnect
        if (!ct.IsCancellationRequested)
        {
            await Task.Delay(ReconnectDelayMs, ct);
            await ConnectAsync(ct);
        }
    }

    public async ValueTask DisposeAsync()
    {
        _cts?.Cancel();
        _reader?.Dispose();
        _writer?.Dispose();
        if (_pipeClient != null)
            await _pipeClient.DisposeAsync();
    }
}
```

---

## Error Handling

### Pipe Disconnection

| Scenario | Behavior |
|:---------|:---------|
| TrayApp closes | Service detects `ReadLine` returns null, re-enters `WaitForConnectionAsync` |
| Service stops | TrayApp detects disconnect, retries every 2 seconds with `ConnectAsync` |
| TrayApp crashes | Same as TrayApp closes — pipe read returns null |
| Service crashes | TrayApp gets `IOException`, enters reconnect loop |

### Reconnection Strategy

- TrayApp reconnects automatically with a 2-second delay between attempts
- Service always re-listens after a client disconnects
- No message queuing during disconnection — messages sent while disconnected are lost
- The TrayApp should request a fresh `get_status` after reconnecting to resync state

### Pipe Security

- Named pipe is created with default security (same-user access only)
- No cross-user or cross-session access is possible
- The pipe name `onevo-agent-ipc` is defined in `ONEVO.Agent.Shared/Constants.cs`

---

## Related

- [[modules/agent-gateway/agent-overview|Agent Overview]] — Architecture overview and data flow
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — Server API endpoints that the Service calls
- [[modules/identity-verification/photo-capture|Photo Capture]] — Photo capture flow triggered via IPC
- [[modules/agent-gateway/tray-app-ui|Tray App Ui]] — TrayApp UI that sends/receives IPC messages
- [[modules/agent-gateway/data-collection|Data Collection]] — Collectors that run in the Service
- [[AI_CONTEXT/rules|Rules]] — Section 10: Desktop Agent Rules (IPC message samples)
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — Implementation task
