# Review Cycles — Testing

**Module:** Performance
**Feature:** Review Cycles
**Location:** `tests/ONEVO.Tests.Unit/Modules/Performance/ReviewCycleServiceTests.cs`

---

## Unit Tests

```csharp
public class ReviewCycleServiceTests
{
    private readonly Mock<IReviewCycleRepository> _repoMock = new();
    private readonly ReviewCycleService _sut;

    [Fact]
    public async Task Create_cycle_in_draft_status()
    {
        // Arrange
        // ... setup mocks for create cycle in draft status

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = draft
    }

    [Fact]
    public async Task Activate_cycle_creates_reviews_for_all_employees()
    {
        // Arrange
        // ... setup mocks for activate cycle creates reviews for all employees

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Review records created
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create cycle in draft status | Unit | Status = draft |
| Activate cycle creates reviews for all employees | Unit | Review records created |

## Related

- [[modules/performance/review-cycles/overview|Review Cycles Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
