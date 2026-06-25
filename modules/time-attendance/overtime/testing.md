# Overtime - Testing

**Module:** Time & Attendance
**Feature:** Overtime
**Location:** `tests/ONEVO.Tests.Unit/Modules/TimeAttendance/OvertimeServiceTests.cs`

---

## Unit Tests

```csharp
public class OvertimeServiceTests
{
    private readonly Mock<IOvertimeRepository> _repoMock = new();
    private readonly OvertimeService _sut;

    [Fact]
    public async Task Submit_overtime_creates_inbox_approval()
    {
        // Arrange
        // ... setup mocks for submit overtime creates inbox approval

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Inbox approval item created for eligible owner
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
| Submit overtime creates inbox approval | Unit | Inbox approval item created for eligible owner |
| Approve adds to payroll hours | Unit | Overtime hours recorded |

## Related

- [[modules/time-attendance/overtime/overview|Overtime Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
