# Reviews — Testing

**Module:** Performance
**Feature:** Reviews
**Location:** `tests/ONEVO.Tests.Unit/Modules/Performance/ReviewServiceTests.cs`

---

## Unit Tests

```csharp
public class ReviewServiceTests
{
    private readonly Mock<IReviewRepository> _repoMock = new();
    private readonly ReviewService _sut;

    [Fact]
    public async Task Submit_review_updates_status()
    {
        // Arrange
        // ... setup mocks for submit review updates status

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = submitted
    }

    [Fact]
    public async Task Rating_out_of_range_rejected()
    {
        // Arrange
        // ... setup mocks for rating out of range rejected

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 1.0-5.0 enforced
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Submit review updates status | Unit | Status = submitted |
| Rating out of range rejected | Unit | 1.0-5.0 enforced |

## Related

- [[modules/performance/reviews/overview|Reviews Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
