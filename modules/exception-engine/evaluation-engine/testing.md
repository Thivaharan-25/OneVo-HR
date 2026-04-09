# Evaluation Engine — Testing

**Module:** Exception Engine
**Feature:** Evaluation Engine
**Location:** `tests/ONEVO.Tests.Unit/Modules/ExceptionEngine/ExceptionEvaluationServiceTests.cs`

---

## Unit Tests

```csharp
public class ExceptionEvaluationServiceTests
{
    private readonly Mock<IExceptionEvaluationRepository> _repoMock = new();
    private readonly ExceptionEvaluationService _sut;

    [Fact]
    public async Task Low_activity_rule_evaluates_idle_percentage()
    {
        // Arrange
        // ... setup mocks for low activity rule evaluates idle percentage

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Breach detected above threshold
    }

    [Fact]
    public async Task Excess_meeting_rule_evaluates_meeting_percentage()
    {
        // Arrange
        // ... setup mocks for excess meeting rule evaluates meeting percentage

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Alert created when exceeded
    }

    [Fact]
    public async Task Outside_work_hours_skips_evaluation()
    {
        // Arrange
        // ... setup mocks for outside work hours skips evaluation

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No rules evaluated
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Low activity rule evaluates idle percentage | Unit | Breach detected above threshold |
| Excess meeting rule evaluates meeting percentage | Unit | Alert created when exceeded |
| Outside work hours skips evaluation | Unit | No rules evaluated |

## Related

- [[frontend/architecture/overview|Evaluation Engine Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
