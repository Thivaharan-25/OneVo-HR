# Monitoring Snapshots - Testing

**Module:** Productivity Analytics
**Feature:** Monitoring Snapshots
**Location:** `tests/ONEVO.Tests.Unit/Modules/ProductivityAnalytics/MonitoringSnapshotServiceTests.cs`

---

## Unit Tests

```csharp
public class MonitoringSnapshotServiceTests
{
    private readonly Mock<IMonitoringSnapshotRepository> _repoMock = new();
    private readonly MonitoringSnapshotService _sut;

    [Fact]
    public async Task Snapshot_includes_all_active_employees()
    {
        // Arrange
        // ... setup mocks for snapshot includes all active employees

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Count matches
    }

    [Fact]
    public async Task Department_breakdown_computed()
    {
        // Arrange
        // ... setup mocks for department breakdown computed

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Per-department metrics
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Snapshot includes all active employees | Unit | Count matches |
| Department breakdown computed | Unit | Per-department metrics |

## Related

- [[frontend/architecture/overview|Monitoring Snapshots Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
