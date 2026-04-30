# Time Management — Testing

**Module:** WorkSync
**Feature:** Time Management
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Time/`

---

## Unit Tests

```csharp
public class TimeServiceTests
{
    [Fact]
    public async Task StartTimer_WithActiveTimer_ReturnsFailure()
    {
        SetupActiveTimer(_userId);
        var result = await _sut.StartTimerAsync(_userId, _taskId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("ACTIVE_TIMER_EXISTS");
    }

    [Fact]
    public async Task StopTimer_CalculatesDurationCorrectly()
    {
        var startedAt = DateTime.UtcNow.AddHours(-2).AddMinutes(-15);
        var timer = new TimeLog { StartedAt = startedAt, EndedAt = null };
        SetupActiveTimer(_userId, timer);

        var result = await _sut.StopTimerAsync(_userId, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.DurationMinutes.Should().BeCloseTo(135, delta: 1); // 2h15m
    }

    [Fact]
    public async Task StopTimer_NoActiveTimer_ReturnsFailure()
    {
        SetupNoActiveTimer(_userId);
        var result = await _sut.StopTimerAsync(_userId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("NO_ACTIVE_TIMER");
    }

    [Fact]
    public async Task LogTime_FutureDate_ReturnsFailure()
    {
        var result = await _sut.LogManualAsync(_taskId, _userId,
            loggedDate: DateOnly.FromDateTime(DateTime.Today.AddDays(1)), 60, "", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("future date");
    }

    [Fact]
    public async Task SubmitTimesheet_AfterSubmission_LocksEntries()
    {
        var timesheet = new Timesheet { Status = "draft" };
        await _sut.SubmitAsync(timesheet.Id, default);
        timesheet.Status.Should().Be("submitted");

        var modifyResult = await _sut.UpdateEntryAsync(timesheet.Id, _entryId, 90, default);
        modifyResult.IsSuccess.Should().BeFalse();
        modifyResult.Error!.Message.Should().Contain("locked");
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Start timer with active timer | Unit | ACTIVE_TIMER_EXISTS |
| Stop timer calculates duration | Unit | Correct minutes |
| Stop with no active timer | Unit | NO_ACTIVE_TIMER |
| Log for future date | Unit | Failure |
| Submitted timesheet locked | Unit | Cannot modify entries |
| IDE tag @time:log source = "ide_tag" | Unit | source field set correctly |

## Related

- [[modules/work-management/time/overview|Time Overview]]
- [[modules/work-management/time/end-to-end-logic|Time Logic]]
