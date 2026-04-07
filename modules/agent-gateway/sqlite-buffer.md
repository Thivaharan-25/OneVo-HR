# SQLite Buffer — Local Data Store

## Purpose

The SQLite buffer provides **offline resilience** and **batch optimization** for the desktop agent. All collected data is written to SQLite immediately, then synced to the server in batches. If the network is unavailable, data accumulates locally and syncs when connectivity returns.

Key benefits:
- **Zero data loss** — data is persisted before any network call
- **Batch efficiency** — multiple snapshots are sent in a single HTTP request
- **Offline operation** — the agent continues collecting even without internet
- **Crash recovery** — data survives service restarts

---

## Database Location

```
%LOCALAPPDATA%\ONEVO\Agent\agent_buffer.db
```

The database file is created on first run. If it does not exist, `SqliteBuffer` creates it with the schema below.

---

## Schema

### `activity_buffer`

Primary data table. All collector output is stored here as JSON.

```sql
CREATE TABLE IF NOT EXISTS activity_buffer (
    id TEXT PRIMARY KEY,                    -- UUID v7 (time-ordered)
    data_type TEXT NOT NULL,                -- 'snapshot', 'app_usage', 'meeting', 'device_session', 'verification_photo'
    employee_id TEXT,                       -- NULL if no employee logged in (device-only data)
    payload TEXT NOT NULL,                  -- JSON blob matching the ingest batch item schema
    captured_at TEXT NOT NULL,              -- ISO 8601 UTC timestamp
    sent INTEGER DEFAULT 0,                -- 0 = unsent, 1 = sent successfully
    sent_at TEXT,                           -- ISO 8601 UTC timestamp when sent
    retry_count INTEGER DEFAULT 0,         -- Number of failed send attempts
    last_error TEXT                         -- Last error message if send failed
);

CREATE INDEX IF NOT EXISTS idx_buffer_unsent 
    ON activity_buffer (sent, captured_at);

CREATE INDEX IF NOT EXISTS idx_buffer_type 
    ON activity_buffer (data_type, sent);

CREATE INDEX IF NOT EXISTS idx_buffer_cleanup 
    ON activity_buffer (sent, sent_at);
```

### `agent_config`

Stores device registration and cached policy. Survives service restarts.

```sql
CREATE TABLE IF NOT EXISTS agent_config (
    key TEXT PRIMARY KEY,       -- Config key name
    value TEXT NOT NULL,        -- JSON or plain string
    updated_at TEXT NOT NULL    -- ISO 8601 UTC timestamp
);

-- Stored keys:
-- 'device_id'          → UUID generated at first run
-- 'device_token'       → Encrypted device JWT (DPAPI-wrapped)
-- 'agent_id'           → UUID returned from server registration
-- 'employee_id'        → UUID of currently logged-in employee (NULL when logged out)
-- 'employee_name'      → Display name of logged-in employee
-- 'policy'             → JSON of current monitoring policy
-- 'last_policy_sync'   → ISO 8601 timestamp of last policy fetch
```

### `sync_state`

Tracks sync progress to enable reliable batch sending.

```sql
CREATE TABLE IF NOT EXISTS sync_state (
    id TEXT PRIMARY KEY,           -- Always 'current' (single row)
    last_sync_at TEXT,             -- ISO 8601 UTC timestamp of last successful sync
    last_heartbeat_at TEXT,        -- ISO 8601 UTC timestamp of last heartbeat
    consecutive_failures INTEGER DEFAULT 0,  -- For exponential backoff
    circuit_open_until TEXT,       -- ISO 8601 UTC timestamp if circuit breaker is open
    updated_at TEXT NOT NULL
);
```

---

## CRUD Operations

### Insert on Capture

Every collector writes to the buffer after each capture cycle.

```csharp
// ONEVO.Agent.Service/Buffer/SqliteBuffer.cs

public class SqliteBuffer : IDisposable
{
    private readonly SqliteConnection _connection;
    private readonly ILogger<SqliteBuffer> _logger;

    public SqliteBuffer(ILogger<SqliteBuffer> logger)
    {
        _logger = logger;
        var dbPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "ONEVO", "Agent", "agent_buffer.db");

        Directory.CreateDirectory(Path.GetDirectoryName(dbPath)!);

        _connection = new SqliteConnection($"Data Source={dbPath}");
        _connection.Open();
        InitializeSchema();
    }

    public async Task InsertAsync(string dataType, string? employeeId, object payload, CancellationToken ct)
    {
        var id = Guid.CreateVersion7().ToString();
        var json = JsonSerializer.Serialize(payload, IpcJsonOptions.Default);
        var now = DateTimeOffset.UtcNow.ToString("O");

        const string sql = """
            INSERT INTO activity_buffer (id, data_type, employee_id, payload, captured_at)
            VALUES (@id, @dataType, @employeeId, @payload, @capturedAt)
            """;

        await using var cmd = _connection.CreateCommand();
        cmd.CommandText = sql;
        cmd.Parameters.AddWithValue("@id", id);
        cmd.Parameters.AddWithValue("@dataType", dataType);
        cmd.Parameters.AddWithValue("@employeeId", (object?)employeeId ?? DBNull.Value);
        cmd.Parameters.AddWithValue("@payload", json);
        cmd.Parameters.AddWithValue("@capturedAt", now);

        await cmd.ExecuteNonQueryAsync(ct);
        _logger.LogDebug("Buffered {DataType} record {Id}", dataType, id);
    }
}
```

### Read Unsent Batch

The sync service reads unsent rows in batches.

```csharp
public async Task<List<BufferedRecord>> GetUnsentBatchAsync(int maxBatchSize, CancellationToken ct)
{
    const string sql = """
        SELECT id, data_type, employee_id, payload, captured_at
        FROM activity_buffer
        WHERE sent = 0
        ORDER BY captured_at ASC
        LIMIT @limit
        """;

    await using var cmd = _connection.CreateCommand();
    cmd.CommandText = sql;
    cmd.Parameters.AddWithValue("@limit", maxBatchSize);

    var records = new List<BufferedRecord>();
    await using var reader = await cmd.ExecuteReaderAsync(ct);

    while (await reader.ReadAsync(ct))
    {
        records.Add(new BufferedRecord
        {
            Id = reader.GetString(0),
            DataType = reader.GetString(1),
            EmployeeId = reader.IsDBNull(2) ? null : reader.GetString(2),
            Payload = reader.GetString(3),
            CapturedAt = reader.GetString(4)
        });
    }

    return records;
}
```

### Mark as Sent

After successful server acknowledgment (202 Accepted), mark rows as sent.

```csharp
public async Task MarkAsSentAsync(IEnumerable<string> ids, CancellationToken ct)
{
    var now = DateTimeOffset.UtcNow.ToString("O");

    // Use a transaction for batch updates
    await using var transaction = _connection.BeginTransaction();

    foreach (var id in ids)
    {
        const string sql = """
            UPDATE activity_buffer 
            SET sent = 1, sent_at = @sentAt 
            WHERE id = @id
            """;

        await using var cmd = _connection.CreateCommand();
        cmd.Transaction = transaction;
        cmd.CommandText = sql;
        cmd.Parameters.AddWithValue("@sentAt", now);
        cmd.Parameters.AddWithValue("@id", id);
        await cmd.ExecuteNonQueryAsync(ct);
    }

    transaction.Commit();
    _logger.LogDebug("Marked {Count} records as sent", ids.Count());
}
```

### Mark Send Failure

If the server returns an error, increment retry count.

```csharp
public async Task MarkSendFailureAsync(IEnumerable<string> ids, string error, CancellationToken ct)
{
    await using var transaction = _connection.BeginTransaction();

    foreach (var id in ids)
    {
        const string sql = """
            UPDATE activity_buffer 
            SET retry_count = retry_count + 1, last_error = @error
            WHERE id = @id
            """;

        await using var cmd = _connection.CreateCommand();
        cmd.Transaction = transaction;
        cmd.CommandText = sql;
        cmd.Parameters.AddWithValue("@error", error);
        cmd.Parameters.AddWithValue("@id", id);
        await cmd.ExecuteNonQueryAsync(ct);
    }

    transaction.Commit();
}
```

---

## Buffer Cleanup

Handled by `BufferCleanup.cs`, runs after each successful sync.

```csharp
// ONEVO.Agent.Service/Buffer/BufferCleanup.cs

public class BufferCleanup
{
    private readonly SqliteBuffer _buffer;
    private readonly ILogger<BufferCleanup> _logger;

    // Cleanup thresholds
    private const int MaxBufferSizeMb = 100;
    private const int SentDataRetentionHours = 24;
    private const int MaxRetryCount = 10;

    public async Task CleanupAsync(CancellationToken ct)
    {
        // 1. Delete sent data older than 24 hours
        var cutoff = DateTimeOffset.UtcNow.AddHours(-SentDataRetentionHours).ToString("O");
        await _buffer.ExecuteAsync(
            "DELETE FROM activity_buffer WHERE sent = 1 AND sent_at < @cutoff",
            new { cutoff }, ct);

        // 2. Delete records that have exceeded max retry count
        await _buffer.ExecuteAsync(
            "DELETE FROM activity_buffer WHERE retry_count >= @maxRetry",
            new { maxRetry = MaxRetryCount }, ct);

        // 3. If buffer exceeds 100MB, drop oldest unsent records
        var dbSizeMb = await GetDatabaseSizeMbAsync(ct);
        if (dbSizeMb > MaxBufferSizeMb)
        {
            _logger.LogWarning("Buffer size {SizeMb}MB exceeds {MaxMb}MB limit, dropping oldest unsent records",
                dbSizeMb, MaxBufferSizeMb);

            await _buffer.ExecuteAsync("""
                DELETE FROM activity_buffer
                WHERE id IN (
                    SELECT id FROM activity_buffer
                    WHERE sent = 0
                    ORDER BY captured_at ASC
                    LIMIT 1000
                )
                """, ct);
        }

        // 4. VACUUM to reclaim space (run periodically, not every cleanup)
        // Only run if we deleted a significant number of rows
    }
}
```

### Cleanup Strategy Summary

| Rule | Action |
|:-----|:-------|
| Sent data > 24 hours old | Delete |
| Unsent data with 10+ retries | Delete (data is stale/corrupt) |
| Total DB size > 100MB | Drop oldest unsent records in batches of 1000 |
| After large deletions | VACUUM to reclaim disk space |

---

## Encryption at Rest

The SQLite database contains activity data classified as **CONFIDENTIAL** (see [[data-classification]]). It is protected using Windows DPAPI.

```csharp
// Approach: Encrypt the entire DB file path using DPAPI
// The DB is only accessible to the Windows user account running the service

// Option 1: DPAPI for the device token (most sensitive value)
public class DeviceTokenStore
{
    public void StoreToken(string token)
    {
        var encrypted = ProtectedData.Protect(
            Encoding.UTF8.GetBytes(token),
            entropy: null,
            DataProtectionScope.LocalMachine);

        // Store encrypted bytes in agent_config table as base64
        _buffer.SetConfig("device_token", Convert.ToBase64String(encrypted));
    }

    public string? GetToken()
    {
        var base64 = _buffer.GetConfig("device_token");
        if (base64 == null) return null;

        var encrypted = Convert.FromBase64String(base64);
        var decrypted = ProtectedData.Unprotect(
            encrypted,
            entropy: null,
            DataProtectionScope.LocalMachine);

        return Encoding.UTF8.GetString(decrypted);
    }
}
```

**Security notes:**
- The device JWT is the most sensitive value — always stored encrypted via DPAPI
- Activity data in the buffer is protected by Windows file-system ACLs (service runs as SYSTEM or the logged-in user)
- The `agent_buffer.db` file should be in `%LOCALAPPDATA%` which is per-user and not accessible to other users
- If stronger encryption is needed (Phase 2), consider SQLCipher for full database encryption

---

## Config Operations

```csharp
// Helper methods on SqliteBuffer for the agent_config table

public async Task SetConfigAsync(string key, string value, CancellationToken ct)
{
    var now = DateTimeOffset.UtcNow.ToString("O");
    const string sql = """
        INSERT INTO agent_config (key, value, updated_at)
        VALUES (@key, @value, @updatedAt)
        ON CONFLICT(key) DO UPDATE SET value = @value, updated_at = @updatedAt
        """;

    await using var cmd = _connection.CreateCommand();
    cmd.CommandText = sql;
    cmd.Parameters.AddWithValue("@key", key);
    cmd.Parameters.AddWithValue("@value", value);
    cmd.Parameters.AddWithValue("@updatedAt", now);
    await cmd.ExecuteNonQueryAsync(ct);
}

public async Task<string?> GetConfigAsync(string key, CancellationToken ct)
{
    const string sql = "SELECT value FROM agent_config WHERE key = @key";

    await using var cmd = _connection.CreateCommand();
    cmd.CommandText = sql;
    cmd.Parameters.AddWithValue("@key", key);

    var result = await cmd.ExecuteScalarAsync(ct);
    return result as string;
}
```

---

## Sync Service Integration

The `DataSyncService` orchestrates the buffer-to-server flow:

```csharp
// ONEVO.Agent.Service/Sync/DataSyncService.cs — simplified

public class DataSyncService : BackgroundService
{
    private readonly SqliteBuffer _buffer;
    private readonly IAgentGatewayClient _gatewayClient;
    private readonly BufferCleanup _cleanup;
    private int _snapshotIntervalSeconds = 150; // Default, updated by policy

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var batch = await _buffer.GetUnsentBatchAsync(maxBatchSize: 50, stoppingToken);

                if (batch.Count > 0)
                {
                    var payload = BuildIngestPayload(batch);
                    var result = await _gatewayClient.IngestAsync(payload, stoppingToken);

                    if (result.IsSuccess)
                    {
                        await _buffer.MarkAsSentAsync(batch.Select(b => b.Id), stoppingToken);
                        await _cleanup.CleanupAsync(stoppingToken);
                    }
                    else
                    {
                        await _buffer.MarkSendFailureAsync(
                            batch.Select(b => b.Id), result.Error, stoppingToken);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Sync cycle failed");
            }

            await Task.Delay(TimeSpan.FromSeconds(_snapshotIntervalSeconds), stoppingToken);
        }
    }
}
```

See [[agent-server-protocol]] for the ingest endpoint payload format and [[data-collection]] for what each collector writes to the buffer.

---

## Related

- [[agent-overview]] — Architecture overview and data flow
- [[data-collection]] — Collectors that write to the buffer (includes buffer schema)
- [[agent-server-protocol]] — Ingest endpoint that receives buffered data
- [[tamper-resistance]] — Uses buffer timestamps for gap detection
- [[mock-mode]] — Mock mode still uses the real SQLite buffer
- [[rules]] — Section 10: Buffer size limit (100MB), performance budgets
- [[data-classification]] — Activity data classification
- [[WEEK1-shared-platform]] — Implementation task
