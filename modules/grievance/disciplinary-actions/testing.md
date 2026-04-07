# Disciplinary Actions — Testing

**Module:** Grievance
**Feature:** Disciplinary Actions
**Location:** `tests/ONEVO.Tests.Unit/Modules/Grievance/DisciplinaryServiceTests.cs`

---

## Unit Tests

```csharp
public class DisciplinaryServiceTests
{
    private readonly Mock<IDisciplinaryRepository> _repoMock = new();
    private readonly DisciplinaryService _sut;

    [Fact]
    public async Task Issue_warning_creates_record()
    {
        // Arrange
        // ... setup mocks for issue warning creates record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Action recorded
    }

    [Fact]
    public async Task Termination_triggers_offboarding()
    {
        // Arrange
        // ... setup mocks for termination triggers offboarding

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
| Issue warning creates record | Unit | Action recorded |
| Termination triggers offboarding | Unit | Offboarding started |

## Related

- [[disciplinary-actions]] — feature overview
- [[testing/README|Testing Standards]] — project-wide testing conventions
