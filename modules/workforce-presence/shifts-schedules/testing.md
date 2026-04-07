# Shifts & Schedules — Testing

**Module:** Workforce Presence
**Feature:** Shifts & Schedules
**Location:** `tests/ONEVO.Tests.Unit/Modules/WorkforcePresence/ShiftServiceTests.cs`

---

## Unit Tests

```csharp
public class ShiftServiceTests
{
    private readonly Mock<IShiftRepository> _repoMock = new();
    private readonly ShiftService _sut;

    [Fact]
    public async Task Create_shift_validates_times()
    {
        // Arrange
        // ... setup mocks for create shift validates times

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Shift created
    }

    [Fact]
    public async Task Assign_employee_to_schedule()
    {
        // Arrange
        // ... setup mocks for assign employee to schedule

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Assignment created
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create shift validates times | Unit | Shift created |
| Assign employee to schedule | Unit | Assignment created |

## Related

- [[shifts-schedules|Shifts & Schedules Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
