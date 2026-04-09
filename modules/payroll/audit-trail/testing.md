# Audit Trail — Testing

**Module:** Payroll
**Feature:** Audit Trail
**Location:** `tests/ONEVO.Tests.Unit/Modules/Payroll/PayrollAuditServiceTests.cs`

---

## Unit Tests

```csharp
public class PayrollAuditServiceTests
{
    private readonly Mock<IPayrollAuditRepository> _repoMock = new();
    private readonly PayrollAuditService _sut;

    [Fact]
    public async Task Run_actions_logged_automatically()
    {
        // Arrange
        // ... setup mocks for run actions logged automatically

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Audit entry created
    }

    [Fact]
    public async Task Query_returns_chronological_entries()
    {
        // Arrange
        // ... setup mocks for query returns chronological entries

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Ordered by created_at
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Run actions logged automatically | Unit | Audit entry created |
| Query returns chronological entries | Unit | Ordered by created_at |

## Related

- [[frontend/architecture/overview|Audit Trail Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
