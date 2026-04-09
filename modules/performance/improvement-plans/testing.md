# Improvement Plans (PIP) — Testing

**Module:** Performance
**Feature:** Improvement Plans (PIP)
**Location:** `tests/ONEVO.Tests.Unit/Modules/Performance/PipServiceTests.cs`

---

## Unit Tests

```csharp
public class PipServiceTests
{
    private readonly Mock<IPipRepository> _repoMock = new();
    private readonly PipService _sut;

    [Fact]
    public async Task Create_PIP_for_employee()
    {
        // Arrange
        // ... setup mocks for create pip for employee

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // PIP with objectives
    }

    [Fact]
    public async Task Complete_with_termination_triggers_offboarding()
    {
        // Arrange
        // ... setup mocks for complete with termination triggers offboarding

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Offboarding started
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create PIP for employee | Unit | PIP with objectives |
| Complete with termination triggers offboarding | Unit | Offboarding started |

## Related

- [[modules/performance/improvement-plans/overview|Improvement Plans Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
