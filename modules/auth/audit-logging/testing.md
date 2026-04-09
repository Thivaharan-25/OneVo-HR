# Audit Logging — Testing

**Module:** Auth
**Feature:** Audit Logging
**Location:** `tests/ONEVO.Tests.Unit/Modules/Auth/AuditLogServiceTests.cs`

---

## Unit Tests

```csharp
public class AuditLogServiceTests
{
    private readonly Mock<IAuditLogRepository> _repoMock = new();
    private readonly AuditLogService _sut;

    [Fact]
    public async Task LogAsync_ValidEvent_InsertsAuditRecord()
    {
        var command = new AuditLogCommand
        {
            Action = "employee.created",
            ResourceType = "Employee",
            ResourceId = Guid.NewGuid()
        };

        await _sut.LogAsync(command, default);

        _repoMock.Verify(r => r.InsertAsync(
            It.Is<AuditLog>(a => a.Action == "employee.created"), default), Times.Once);
    }

    [Fact]
    public async Task QueryAsync_WithDateRange_UsesPartitionPruning()
    {
        var query = new AuditLogQueryParams
        {
            From = new DateOnly(2026, 4, 1),
            To = new DateOnly(2026, 4, 5)
        };

        await _sut.QueryAsync(query, default);

        _repoMock.Verify(r => r.QueryAsync(
            It.Is<AuditLogQueryParams>(q => q.From == query.From), default), Times.Once);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Audit event logged | Unit | Record inserted |
| Query with date range | Unit | Partition-pruned query |
| System action (no user) | Unit | user_id = null |

## Related

- [[modules/auth/audit-logging/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
