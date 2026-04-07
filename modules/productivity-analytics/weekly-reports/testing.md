# Weekly Reports — Testing

**Module:** Productivity Analytics
**Feature:** Weekly Reports
**Location:** `tests/ONEVO.Tests.Unit/Modules/ProductivityAnalytics/WeeklyReportServiceTests.cs`

---

## Unit Tests

```csharp
public class WeeklyReportServiceTests
{
    private readonly Mock<IWeeklyReportRepository> _repoMock = new();
    private readonly WeeklyReportService _sut;

    [Fact]
    public async Task Weekly_aggregates_from_daily_reports()
    {
        // Arrange
        // ... setup mocks for weekly aggregates from daily reports

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Correct weekly totals
    }

    [Fact]
    public async Task Trend_comparison_computed()
    {
        // Arrange
        // ... setup mocks for trend comparison computed

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Week-over-week change
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Weekly aggregates from daily reports | Unit | Correct weekly totals |
| Trend comparison computed | Unit | Week-over-week change |

## Related

- [[productivity-analytics/weekly-reports/overview|Weekly Reports Overview]]
- [[testing/README|Testing Standards]]
