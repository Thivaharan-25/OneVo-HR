# Report Templates — Testing

**Module:** Reporting Engine
**Feature:** Report Templates
**Location:** `tests/ONEVO.Tests.Unit/Modules/ReportingEngine/ReportTemplateServiceTests.cs`

---

## Unit Tests

```csharp
public class ReportTemplateServiceTests
{
    private readonly Mock<IReportTemplateRepository> _repoMock = new();
    private readonly ReportTemplateService _sut;

    [Fact]
    public async Task System_template_cannot_be_deleted()
    {
        // Arrange
        // ... setup mocks for system template cannot be deleted

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 400 returned
    }

    [Fact]
    public async Task Custom_template_created()
    {
        // Arrange
        // ... setup mocks for custom template created

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Template saved
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| System template cannot be deleted | Unit | 400 returned |
| Custom template created | Unit | Template saved |

## Related

- [[reporting-engine/report-templates/overview|Report Templates Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
