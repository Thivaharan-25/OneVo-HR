# Alert Generation — Testing

**Module:** Exception Engine
**Feature:** Alert Generation
**Location:** `tests/ONEVO.Tests.Unit/Modules/ExceptionEngine/ExceptionEvaluationServiceTests.cs`

---

## Unit Tests

```csharp
public class ExceptionEvaluationServiceTests
{
    private readonly Mock<IExceptionEvaluationRepository> _repoMock = new();
    private readonly ExceptionEvaluationService _sut;

    [Fact]
    public async Task Low_activity_breach_creates_alert()
    {
        // Arrange
        // ... setup mocks for low activity breach creates alert

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Alert with status new
    }

    [Fact]
    public async Task Duplicate_alert_deduplicated()
    {
        // Arrange
        // ... setup mocks for duplicate alert deduplicated

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No new alert created
    }

    [Fact]
    public async Task Monitoring_disabled_skips_employee()
    {
        // Arrange
        // ... setup mocks for monitoring disabled skips employee

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No evaluation performed
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Low activity breach creates alert | Unit | Alert with status new |
| Duplicate alert deduplicated | Unit | No new alert created |
| Monitoring disabled skips employee | Unit | No evaluation performed |

## Related

- [[frontend/architecture/overview|Alert Generation Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
