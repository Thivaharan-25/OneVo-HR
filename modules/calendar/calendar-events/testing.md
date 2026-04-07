# Calendar Events — Testing

**Module:** Calendar
**Feature:** Calendar Events
**Location:** `tests/ONEVO.Tests.Unit/Modules/Calendar/CalendarServiceTests.cs`

---

## Unit Tests

```csharp
public class CalendarServiceTests
{
    private readonly Mock<ICalendarRepository> _repoMock = new();
    private readonly CalendarService _sut;

    [Fact]
    public async Task GetEventsAsync_WithDateRange_ReturnsFilteredEvents()
    {
        SetupEventsInRange(3);
        var result = await _sut.GetEventsAsync(DateOnly.Parse("2026-04-01"), DateOnly.Parse("2026-04-30"), default);

        result.IsSuccess.Should().BeTrue();
        result.Value.Should().HaveCount(3);
    }

    [Fact]
    public async Task CreateAsync_ValidEvent_ReturnsCreated()
    {
        var command = new CreateEventCommand { Title = "Team Meeting", StartDate = DateTime.Today };
        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
    }

    [Fact]
    public async Task CreateAsync_EndBeforeStart_ReturnsValidationError()
    {
        var command = new CreateEventCommand { StartDate = DateTime.Today, EndDate = DateTime.Today.AddDays(-1) };
        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| GetEventsAsync WithDateRange ReturnsFilteredEvents | Unit | ReturnsFilteredEvents |
| CreateAsync ValidEvent ReturnsCreated | Unit | ReturnsCreated |
| CreateAsync EndBeforeStart ReturnsValidationError | Unit | ReturnsValidationError |

## Related

- [[calendar/calendar-events/overview|Calendar Events Overview]]
- [[testing/README|Testing Standards]]
