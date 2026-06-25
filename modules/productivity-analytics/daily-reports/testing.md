# Daily Reports - Testing

**Module:** Productivity Analytics
**Feature:** Daily Reports
**Location:** `tests/ONEVO.Tests.Unit/Modules/ProductivityAnalytics/DailyReportServiceTests.cs`

---

## Unit Tests

```csharp
public class DailyReportServiceTests
{
    private readonly Mock<IDailyReportRepository> _repoMock = new();
    private readonly DailyReportService _sut;

    [Fact]
    public async Task Generate_aggregates_from_activity_and_presence()
    {
        // Arrange
        // ... setup mocks for generate aggregates from activity and presence

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Report with correct totals
    }

    [Fact]
    public async Task Monitoring_snapshot_includes_all_employees()
    {
        // Arrange
        // ... setup mocks for monitoring snapshot includes all employees

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Total count matches
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Generate aggregates from activity and presence | Unit | Report with correct totals |
| Monitoring snapshot includes all employees | Unit | Total count matches |

## Related

- [[frontend/architecture/overview|Daily Reports Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
