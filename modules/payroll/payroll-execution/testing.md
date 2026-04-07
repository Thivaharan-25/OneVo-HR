# Payroll Execution — Testing

**Module:** Payroll
**Feature:** Payroll Execution
**Location:** `tests/ONEVO.Tests.Unit/Modules/Payroll/PayrollServiceTests.cs`

---

## Unit Tests

```csharp
public class PayrollServiceTests
{
    private readonly Mock<IPayrollRepository> _repoMock = new();
    private readonly PayrollService _sut;

    [Fact]
    public async Task Execute_run_calculates_net_pay_correctly()
    {
        // Arrange
        // ... setup mocks for execute run calculates net pay correctly

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // net = gross + allowances - tax - pension
    }

    [Fact]
    public async Task Concurrent_run_blocked_by_lock()
    {
        // Arrange
        // ... setup mocks for concurrent run blocked by lock

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 409 Conflict
    }

    [Fact]
    public async Task Missing_salary_data_skips_employee()
    {
        // Arrange
        // ... setup mocks for missing salary data skips employee

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Warning logged
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Execute run calculates net pay correctly | Unit | net = gross + allowances - tax - pension |
| Concurrent run blocked by lock | Unit | 409 Conflict |
| Missing salary data skips employee | Unit | Warning logged |

## Related

- [[payroll/payroll-execution/overview|Payroll Execution Overview]]
- [[testing/README|Testing Standards]]
