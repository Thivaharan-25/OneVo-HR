# Overtime — Testing

**Module:** Workforce Presence
**Feature:** Overtime
**Location:** `tests/ONEVO.Tests.Unit/Modules/WorkforcePresence/OvertimeServiceTests.cs`

---

## Unit Tests

```csharp
public class OvertimeServiceTests
{
    private readonly Mock<IOvertimeRepository> _repoMock = new();
    private readonly OvertimeService _sut;

    [Fact]
    public async Task Submit_overtime_creates_workflow()
    {
        // Arrange
        // ... setup mocks for submit overtime creates workflow

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Approval workflow started
    }

    [Fact]
    public async Task Approve_adds_to_payroll_hours()
    {
        // Arrange
        // ... setup mocks for approve adds to payroll hours

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Overtime hours recorded
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Submit overtime creates workflow | Unit | Approval workflow started |
| Approve adds to payroll hours | Unit | Overtime hours recorded |

## Related

- [[modules/workforce-presence/overtime/overview|Overtime Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
