# Balance Audit - Testing

**Module:** Time Off
**Feature:** Balance Audit
**Location:** `tests/ONEVO.Tests.Unit/Modules/TimeOff/TimeOffBalanceAuditServiceTests.cs`

---

## Unit Tests

```csharp
public class TimeOffBalanceAuditServiceTests
{
    private readonly Mock<ITimeOffBalanceAuditRepository> _repoMock = new();
    private readonly TimeOffBalanceAuditService _sut;

    [Fact]
    public async Task Approval_creates_deduction_audit_entry()
    {
        // Arrange
        // ... setup mocks for approval creates deduction audit entry

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // change_type = deduction
    }

    [Fact]
    public async Task Cancellation_creates_adjustment_entry()
    {
        // Arrange
        // ... setup mocks for cancellation creates adjustment entry

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // change_type = adjustment
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Approval creates deduction audit entry | Unit | change_type = deduction |
| Cancellation creates adjustment entry | Unit | change_type = adjustment |

## Related

- [[modules/time-off/balance-audit/overview|Balance Audit Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
