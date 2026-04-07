# Conflict Detection — Testing

**Module:** Calendar
**Feature:** Conflict Detection
**Location:** `tests/ONEVO.Tests.Unit/Modules/Calendar/CalendarConflictServiceTests.cs`

---

## Unit Tests

```csharp
public class CalendarConflictServiceTests
{
    private readonly Mock<ICalendarConflictRepository> _repoMock = new();
    private readonly CalendarConflictService _sut;

    [Fact]
    public async Task GetConflictsForDateRangeAsync_WithOverlappingReview_ReturnsHighSeverity()
    {
        SetupReviewEvent(overlapping: true);
        var result = await _sut.GetConflictsForDateRangeAsync(_employeeId, _startDate, _endDate, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.HasConflicts.Should().BeTrue();
        result.Value.HighSeverityCount.Should().Be(1);
    }

    [Fact]
    public async Task GetConflictsForDateRangeAsync_NoOverlap_ReturnsNoConflicts()
    {
        SetupNoOverlappingEvents();
        var result = await _sut.GetConflictsForDateRangeAsync(_employeeId, _startDate, _endDate, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.HasConflicts.Should().BeFalse();
    }

    [Fact]
    public async Task GetConflictsForDateRangeAsync_ExcludesLeaveAndHoliday()
    {
        SetupLeaveAndHolidayEvents();
        var result = await _sut.GetConflictsForDateRangeAsync(_employeeId, _startDate, _endDate, default);

        result.Value!.HasConflicts.Should().BeFalse();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| GetConflictsForDateRangeAsync WithOverlappingReview ReturnsHighSeverity | Unit | ReturnsHighSeverity |
| GetConflictsForDateRangeAsync NoOverlap ReturnsNoConflicts | Unit | ReturnsNoConflicts |
| GetConflictsForDateRangeAsync ExcludesLeaveAndHoliday | Unit | ExcludesLeaveAndHoliday |

## Related

- [[calendar/conflict-detection/overview|Conflict Detection Overview]]
- [[testing/README|Testing Standards]]
