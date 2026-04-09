# Allowances — Testing

**Module:** Payroll
**Feature:** Allowances
**Location:** `tests/ONEVO.Tests.Unit/Modules/Payroll/AllowanceServiceTests.cs`

---

## Unit Tests

```csharp
public class AllowanceServiceTests
{
    private readonly Mock<IAllowanceRepository> _repoMock = new();
    private readonly AllowanceService _sut;

    [Fact]
    public async Task Create_allowance_type()
    {
        // Arrange
        // ... setup mocks for create allowance type

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Type created
    }

    [Fact]
    public async Task Assign_to_employee()
    {
        // Arrange
        // ... setup mocks for assign to employee

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Allowance assigned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create allowance type | Unit | Type created |
| Assign to employee | Unit | Allowance assigned |

## Related

- [[frontend/architecture/overview|Allowances Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
