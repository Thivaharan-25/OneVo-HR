# Mock Mode — Development Without a Backend

## Purpose

Mock mode lets you develop, test, and debug the desktop agent without needing the ONEVO backend server running. A `MockGatewayClient` replaces the real HTTP client and returns fake responses for all 6 Agent Gateway endpoints.

This is essential for:
- Frontend-first development of the TrayApp UI
- Testing collector logic in isolation
- Running the full agent flow on a dev machine
- CI/CD pipeline testing

---

## Configuration

### Enable Mock Mode

In `appsettings.Development.json`:

```json
{
  "AgentGateway": {
    "BaseUrl": "https://agent.onevo.app",
    "UseMockGateway": true
  },
  "Logging": {
    "LogLevel": {
      "Default": "Debug"
    }
  }
}
```

### DI Registration

```csharp
// ONEVO.Agent.Service/Program.cs

var builder = Host.CreateDefaultBuilder(args)
    .UseWindowsService()
    .ConfigureServices((context, services) =>
    {
        var useMock = context.Configuration.GetValue<bool>("AgentGateway:UseMockGateway");

        if (useMock)
        {
            services.AddSingleton<IAgentGatewayClient, MockGatewayClient>();
            Log.Information("Using MockGatewayClient — no backend required");
        }
        else
        {
            services.AddHttpClient<IAgentGatewayClient, AgentGatewayClient>(client =>
            {
                client.BaseAddress = new Uri(
                    context.Configuration["AgentGateway:BaseUrl"]!);
            })
            .AddPolicyHandler(/* Polly policies — see [[rules]] Section 10 */);
        }

        // All other services remain the same
        services.AddSingleton<SqliteBuffer>();
        services.AddHostedService<DataSyncService>();
        services.AddHostedService<HeartbeatService>();
        // ...
    });
```

---

## IAgentGatewayClient Interface

Both the real and mock clients implement this interface:

```csharp
// ONEVO.Agent.Shared/IAgentGatewayClient.cs

public interface IAgentGatewayClient
{
    Task<Result<RegisterResponse>> RegisterAsync(RegisterRequest request, CancellationToken ct);
    Task<Result<LoginResponse>> LoginAsync(LoginRequest request, CancellationToken ct);
    Task<Result<AgentPolicy>> GetPolicyAsync(CancellationToken ct);
    Task<Result<HeartbeatResponse>> HeartbeatAsync(HeartbeatRequest request, CancellationToken ct);
    Task<Result<bool>> IngestAsync(IngestPayload payload, CancellationToken ct);
    Task<Result<bool>> LogoutAsync(CancellationToken ct);
}
```

---

## MockGatewayClient

```csharp
// ONEVO.Agent.Service/Mock/MockGatewayClient.cs

public class MockGatewayClient : IAgentGatewayClient
{
    private readonly ILogger<MockGatewayClient> _logger;
    private bool _isRegistered = false;
    private bool _isLoggedIn = false;
    private int _ingestCount = 0;

    public MockGatewayClient(ILogger<MockGatewayClient> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Simulates POST /api/v1/agent/register
    /// Returns a fake device JWT and agent ID.
    /// </summary>
    public Task<Result<RegisterResponse>> RegisterAsync(RegisterRequest request, CancellationToken ct)
    {
        _logger.LogInformation("[MOCK] Register: device={DeviceName}, os={OsVersion}",
            request.DeviceName, request.OsVersion);

        _isRegistered = true;

        return Task.FromResult(Result<RegisterResponse>.Success(new RegisterResponse
        {
            AgentId = Guid.CreateVersion7(),
            DeviceToken = "mock-device-jwt-token-for-development",
            TokenExpiresAt = DateTimeOffset.UtcNow.AddDays(30)
        }));
    }

    /// <summary>
    /// Simulates POST /api/v1/agent/login
    /// Accepts any email/password. Returns a mock employee and full policy.
    /// </summary>
    public Task<Result<LoginResponse>> LoginAsync(LoginRequest request, CancellationToken ct)
    {
        _logger.LogInformation("[MOCK] Login: email={Email}", request.Email);

        _isLoggedIn = true;

        return Task.FromResult(Result<LoginResponse>.Success(new LoginResponse
        {
            EmployeeId = Guid.CreateVersion7(),
            EmployeeName = "Mock Employee",
            Policy = GetMockPolicy()
        }));
    }

    /// <summary>
    /// Simulates GET /api/v1/agent/policy
    /// Returns a fully-enabled monitoring policy.
    /// </summary>
    public Task<Result<AgentPolicy>> GetPolicyAsync(CancellationToken ct)
    {
        _logger.LogInformation("[MOCK] Policy fetch");

        return Task.FromResult(Result<AgentPolicy>.Success(GetMockPolicy()));
    }

    /// <summary>
    /// Simulates POST /api/v1/agent/heartbeat
    /// Always returns OK, no updates available.
    /// </summary>
    public Task<Result<HeartbeatResponse>> HeartbeatAsync(HeartbeatRequest request, CancellationToken ct)
    {
        _logger.LogDebug("[MOCK] Heartbeat: cpu={Cpu}%, mem={Mem}MB, buffer={Buffer}",
            request.CpuUsage, request.MemoryMb, request.BufferCount);

        return Task.FromResult(Result<HeartbeatResponse>.Success(new HeartbeatResponse
        {
            Status = "ok",
            UpdateAvailable = false,
            UpdateUrl = null
        }));
    }

    /// <summary>
    /// Simulates POST /api/v1/agent/ingest
    /// Accepts all data, logs batch size. Returns 202 equivalent.
    /// </summary>
    public Task<Result<bool>> IngestAsync(IngestPayload payload, CancellationToken ct)
    {
        _ingestCount++;
        _logger.LogInformation("[MOCK] Ingest #{Count}: {BatchSize} items for employee {EmployeeId}",
            _ingestCount, payload.Batch.Count, payload.EmployeeId);

        foreach (var item in payload.Batch)
        {
            _logger.LogDebug("[MOCK]   - {Type}: {Data}",
                item.Type, JsonSerializer.Serialize(item.Data));
        }

        return Task.FromResult(Result<bool>.Success(true));
    }

    /// <summary>
    /// Simulates POST /api/v1/agent/logout
    /// Always succeeds.
    /// </summary>
    public Task<Result<bool>> LogoutAsync(CancellationToken ct)
    {
        _logger.LogInformation("[MOCK] Logout");
        _isLoggedIn = false;

        return Task.FromResult(Result<bool>.Success(true));
    }

    private static AgentPolicy GetMockPolicy()
    {
        return new AgentPolicy
        {
            ActivityMonitoring = true,
            ApplicationTracking = true,
            ScreenshotCapture = false,
            MeetingDetection = true,
            DeviceTracking = true,
            IdentityVerification = true,
            VerificationOnLogin = true,
            VerificationOnLogout = false,
            VerificationIntervalMinutes = 60,
            IdleThresholdSeconds = 300,
            SnapshotIntervalSeconds = 30,    // Shorter for dev — see faster sync cycles
            HeartbeatIntervalSeconds = 15     // Shorter for dev — see faster heartbeats
        };
    }
}
```

---

## Testing the Full Flow Locally

### Step 1: Start the Service

```bash
cd ONEVO.Agent.Service
dotnet run
```

Console output:
```
[INF] Using MockGatewayClient — no backend required
[INF] [MOCK] Register: device=DESKTOP-DEV, os=Windows 11
[INF] Registered successfully. Agent ID: abc123
[INF] Waiting for TrayApp connection on pipe onevo-agent-ipc
[DBG] [MOCK] Heartbeat: cpu=0.3%, mem=28MB, buffer=0
```

### Step 2: Start the TrayApp

```bash
cd ONEVO.Agent.TrayApp
dotnet run
```

### Step 3: Login

1. Click the ONEVO tray icon
2. Enter any email (e.g., `test@test.com`) and any password
3. Mock accepts all credentials

### Step 4: Observe Data Flow

Console output from the Service:
```
[INF] [MOCK] Login: email=test@test.com
[INF] Collectors started (policy: all enabled)
[INF] [MOCK] Ingest #1: 3 items for employee def456
[DBG] [MOCK]   - activity_snapshot: {"keyboard_events_count":42,"mouse_events_count":15,...}
[DBG] [MOCK]   - app_usage: {"application_name":"Code","window_title_hash":"a1b2c3",...}
[DBG] [MOCK]   - device_session: {"active_minutes":1,"idle_minutes":0}
```

### Step 5: Verify Buffer

The SQLite buffer works identically in mock mode. Check the buffer state:

```bash
sqlite3 "%LOCALAPPDATA%\ONEVO\Agent\agent_buffer.db" "SELECT COUNT(*) FROM activity_buffer WHERE sent = 0"
```

---

## Mock Variations

### Simulating Network Errors

Create a `MockGatewayClient` that fails intermittently to test resilience:

```csharp
// In a test variant: MockGatewayClientWithErrors.cs
public override Task<Result<bool>> IngestAsync(IngestPayload payload, CancellationToken ct)
{
    _ingestCount++;

    // Fail every 3rd ingest to test retry logic
    if (_ingestCount % 3 == 0)
    {
        _logger.LogWarning("[MOCK] Simulating 500 error on ingest #{Count}", _ingestCount);
        return Task.FromResult(Result<bool>.Failure("Simulated server error"));
    }

    return base.IngestAsync(payload, ct);
}
```

### Simulating Update Available

```csharp
public override Task<Result<HeartbeatResponse>> HeartbeatAsync(HeartbeatRequest request, CancellationToken ct)
{
    return Task.FromResult(Result<HeartbeatResponse>.Success(new HeartbeatResponse
    {
        Status = "ok",
        UpdateAvailable = true,
        UpdateUrl = "https://example.com/mock-update.msixbundle",
        UpdateVersion = "1.1.0",
        UpdateRequired = false
    }));
}
```

### Simulating Identity Verification

The mock policy has `VerificationOnLogin = true`, so the photo capture flow triggers automatically on login. The mock does not validate the photo — it accepts any file path from the `photo_captured` IPC message.

---

## Switching to Real Backend

When the ONEVO backend server is available:

1. Set `"UseMockGateway": false` in `appsettings.Development.json`
2. Set `"BaseUrl"` to your backend URL (e.g., `"https://localhost:5001"` or staging)
3. Ensure a valid tenant API key is configured
4. Restart the service

```json
{
  "AgentGateway": {
    "BaseUrl": "https://staging.onevo.app",
    "UseMockGateway": false
  },
  "TenantApiKey": "your-tenant-api-key-here"
}
```

The SQLite buffer, collectors, and IPC all work identically — only the HTTP client implementation changes.

---

## Related

- [[agent-overview]] — Architecture overview and development setup
- [[agent-server-protocol]] — Real API endpoints that the mock simulates
- [[sqlite-buffer]] — Buffer works the same in mock mode
- [[ipc-protocol]] — IPC works the same in mock mode
- [[data-collection]] — Collectors work the same in mock mode
- [[tray-app-ui]] — TrayApp works the same in mock mode
- [[rules]] — Polly resilience policies (Section 10)
- [[WEEK1-shared-platform]] — Implementation task
