# Report Definitions — Testing

**Module:** Reporting Engine
**Feature:** Report Definitions
**Location:** `tests/ONEVO.Tests.Unit/Modules/ReportingEngine/ReportDefinitionServiceTests.cs`

---

## Unit Tests

```csharp
public class ReportDefinitionServiceTests
{
    private readonly Mock<IReportDefinitionRepository> _repoMock = new();
    private readonly ReportDefinitionService _sut;

    [Fact]
    public async Task Create_with_cron_registers_Hangfire_job()
    {
        // Arrange
        // ... setup mocks for create with cron registers hangfire job

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Job scheduled
    }

    [Fact]
    public async Task Invalid_cron_rejected()
    {
        // Arrange
        // ... setup mocks for invalid cron rejected

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Validation error
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create with cron registers Hangfire job | Unit | Job scheduled |
| Invalid cron rejected | Unit | Validation error |

## Related

- [[frontend/architecture/overview|Report Definitions Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
