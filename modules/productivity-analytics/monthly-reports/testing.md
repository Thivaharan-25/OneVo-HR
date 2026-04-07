# Monthly Reports — Testing

**Module:** Productivity Analytics
**Feature:** Monthly Reports
**Location:** `tests/ONEVO.Tests.Unit/Modules/ProductivityAnalytics/MonthlyReportServiceTests.cs`

---

## Unit Tests

```csharp
public class MonthlyReportServiceTests
{
    private readonly Mock<IMonthlyReportRepository> _repoMock = new();
    private readonly MonthlyReportService _sut;

    [Fact]
    public async Task Monthly_report_includes_department_rank()
    {
        // Arrange
        // ... setup mocks for monthly report includes department rank

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Rank computed
    }

    [Fact]
    public async Task Pattern_analysis_identifies_peak_hours()
    {
        // Arrange
        // ... setup mocks for pattern analysis identifies peak hours

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // performance_pattern_json populated
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Monthly report includes department rank | Unit | Rank computed |
| Pattern analysis identifies peak hours | Unit | performance_pattern_json populated |

## Related

- [[productivity-analytics/monthly-reports/overview|Monthly Reports Overview]]
- [[testing/README|Testing Standards]]
