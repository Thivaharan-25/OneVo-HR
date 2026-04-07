# Pensions — Testing

**Module:** Payroll
**Feature:** Pensions
**Location:** `tests/ONEVO.Tests.Unit/Modules/Payroll/PensionServiceTests.cs`

---

## Unit Tests

```csharp
public class PensionServiceTests
{
    private readonly Mock<IPensionRepository> _repoMock = new();
    private readonly PensionService _sut;

    [Fact]
    public async Task Create_plan_with_contributions()
    {
        // Arrange
        // ... setup mocks for create plan with contributions

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Plan created
    }

    [Fact]
    public async Task Enroll_employee_in_plan()
    {
        // Arrange
        // ... setup mocks for enroll employee in plan

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Enrollment created
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create plan with contributions | Unit | Plan created |
| Enroll employee in plan | Unit | Enrollment created |

## Related

- [[payroll/pensions/overview|Pensions Overview]]
- [[testing/README|Testing Standards]]
