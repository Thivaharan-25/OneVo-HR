# Adjustments — Testing

**Module:** Payroll
**Feature:** Adjustments
**Location:** `tests/ONEVO.Tests.Unit/Modules/Payroll/AdjustmentServiceTests.cs`

---

## Unit Tests

```csharp
public class AdjustmentServiceTests
{
    private readonly Mock<IAdjustmentRepository> _repoMock = new();
    private readonly AdjustmentService _sut;

    [Fact]
    public async Task Create_adjustment_recalculates_payslip()
    {
        // Arrange
        // ... setup mocks for create adjustment recalculates payslip

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Net pay updated
    }

    [Fact]
    public async Task Adjustment_on_completed_run_fails()
    {
        // Arrange
        // ... setup mocks for adjustment on completed run fails

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 400 returned
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create adjustment recalculates payslip | Unit | Net pay updated |
| Adjustment on completed run fails | Unit | 400 returned |

## Related

- [[payroll/adjustments/overview|Adjustments Overview]]
- [[testing/README|Testing Standards]]
