# Balance Audit — Testing

**Module:** Leave
**Feature:** Balance Audit
**Location:** `tests/ONEVO.Tests.Unit/Modules/Leave/LeaveBalanceAuditServiceTests.cs`

---

## Unit Tests

```csharp
public class LeaveBalanceAuditServiceTests
{
    private readonly Mock<ILeaveBalanceAuditRepository> _repoMock = new();
    private readonly LeaveBalanceAuditService _sut;

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

- [[modules/leave/balance-audit/overview|Balance Audit Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
