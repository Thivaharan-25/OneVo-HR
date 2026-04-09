# Expense Claims — Testing

**Module:** Expense
**Feature:** Expense Claims
**Location:** `tests/ONEVO.Tests.Unit/Modules/Expense/ExpenseClaimServiceTests.cs`

---

## Unit Tests

```csharp
public class ExpenseClaimServiceTests
{
    private readonly Mock<IExpenseClaimRepository> _repoMock = new();
    private readonly ExpenseClaimService _sut;

    [Fact]
    public async Task Submit_claim_creates_pending_record()
    {
        // Arrange
        // ... setup mocks for submit claim creates pending record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = pending
    }

    [Fact]
    public async Task Approve_claim_triggers_reimbursement()
    {
        // Arrange
        // ... setup mocks for approve claim triggers reimbursement

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = approved
    }

    [Fact]
    public async Task Duplicate_receipt_number_rejected()
    {
        // Arrange
        // ... setup mocks for duplicate receipt number rejected

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 409 Conflict
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Submit claim creates pending record | Unit | Status = pending |
| Approve claim triggers reimbursement | Unit | Status = approved |
| Duplicate receipt number rejected | Unit | 409 Conflict |

## Related

- [[modules/expense/expense-claims/overview|Expense Claims]] — feature overview
- [[code-standards/testing-strategy|Testing Standards]] — project-wide testing conventions
