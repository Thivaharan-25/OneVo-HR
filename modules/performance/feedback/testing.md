# Feedback — Testing

**Module:** Performance
**Feature:** Feedback
**Location:** `tests/ONEVO.Tests.Unit/Modules/Performance/FeedbackServiceTests.cs`

---

## Unit Tests

```csharp
public class FeedbackServiceTests
{
    private readonly Mock<IFeedbackRepository> _repoMock = new();
    private readonly FeedbackService _sut;

    [Fact]
    public async Task Request_feedback_notifies_respondent()
    {
        // Arrange
        // ... setup mocks for request feedback notifies respondent

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Notification sent
    }

    [Fact]
    public async Task Submit_feedback_updates_status()
    {
        // Arrange
        // ... setup mocks for submit feedback updates status

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = completed
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Request feedback notifies respondent | Unit | Notification sent |
| Submit feedback updates status | Unit | Status = completed |

## Related

- [[feedback|Feedback Overview]]
- [[testing/README|Testing Standards]]
