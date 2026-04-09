# Break Tracking — Testing

**Module:** Workforce Presence
**Feature:** Break Tracking
**Location:** `tests/ONEVO.Tests.Unit/Modules/WorkforcePresence/BreakServiceTests.cs`

---

## Unit Tests

```csharp
public class BreakServiceTests
{
    private readonly Mock<IBreakRepository> _repoMock = new();
    private readonly BreakService _sut;

    [Fact]
    public async Task Start_break_creates_record()
    {
        // Arrange
        // ... setup mocks for start break creates record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Break started
    }

    [Fact]
    public async Task End_break_calculates_duration()
    {
        // Arrange
        // ... setup mocks for end break calculates duration

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Duration computed
    }

    [Fact]
    public async Task Exceeded_break_publishes_event()
    {
        // Arrange
        // ... setup mocks for exceeded break publishes event

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // BreakExceeded event
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Start break creates record | Unit | Break started |
| End break calculates duration | Unit | Duration computed |
| Exceeded break publishes event | Unit | BreakExceeded event |

## Related

- [[Userflow/Workforce-Presence/break-tracking|Break Tracking Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
