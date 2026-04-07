# Report Execution — Testing

**Module:** Reporting Engine
**Feature:** Report Execution
**Location:** `tests/ONEVO.Tests.Unit/Modules/ReportingEngine/ReportExecutionServiceTests.cs`

---

## Unit Tests

```csharp
public class ReportExecutionServiceTests
{
    private readonly Mock<IReportExecutionRepository> _repoMock = new();
    private readonly ReportExecutionService _sut;

    [Fact]
    public async Task Execute_generates_CSV_file()
    {
        // Arrange
        // ... setup mocks for execute generates csv file

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // File uploaded, status completed
    }

    [Fact]
    public async Task Data_source_failure_sets_status_failed()
    {
        // Arrange
        // ... setup mocks for data source failure sets status failed

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Error message logged
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Execute generates CSV file | Unit | File uploaded, status completed |
| Data source failure sets status failed | Unit | Error message logged |

## Related

- [[reporting-engine/report-execution/overview|Report Execution Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
