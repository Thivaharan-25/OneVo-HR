# My Space & Reminders — Testing

**Module:** WorkSync
**Feature:** My Space & Reminders
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/MySpace/`

---

## Unit Tests

```csharp
public class ReminderServiceTests
{
    [Fact]
    public async Task CreateReminder_DuplicateTaskLink_ReturnsFailure()
    {
        SetupExistingReminderForTask(_userId, _taskId);
        var result = await _sut.CreateAsync(_userId, new CreateReminderCommand { LinkedTaskId = _taskId }, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("DUPLICATE_REMINDER");
    }

    [Fact]
    public async Task CompleteReminder_WithLinkedTask_UpdatesTaskStatus()
    {
        var reminder = new Reminder { LinkedTaskId = _taskId };
        _reminderRepoMock.Setup(r => r.GetByIdAsync(reminder.Id, default)).ReturnsAsync(reminder);

        await _sut.CompleteAsync(reminder.Id, default);

        _taskCommandMock.Verify(c => c.UpdateStatusAsync(_taskId, "done", default), Times.Once);
    }

    [Fact]
    public async Task TaskCompletedEvent_MarksLinkedReminderDone()
    {
        var reminder = new Reminder { LinkedTaskId = _taskId, IsCompleted = false };
        SetupReminderForTask(_taskId, reminder);

        await _handler.Handle(new TaskCompletedEvent(_taskId), default);

        reminder.IsCompleted.Should().BeTrue();
        reminder.CompletedAt.Should().NotBeNull();
    }

    [Fact]
    public async Task CompleteAlreadyCompleted_ReturnsFailure()
    {
        var reminder = new Reminder { IsCompleted = true };
        var result = await _sut.CompleteAsync(reminder.Id, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("ALREADY_COMPLETED");
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Duplicate reminder for same task | Unit | DUPLICATE_REMINDER |
| Complete reminder → task updated | Unit | Task status = done |
| Task completed → reminder done | Unit | Reminder is_completed = true |
| Complete already-completed | Unit | ALREADY_COMPLETED |
| Personal board project_id = null | Unit | project_id null, user_id set |

## Related

- [[modules/work-management/my-space/overview|My Space Overview]]
- [[modules/work-management/my-space/end-to-end-logic|My Space Logic]]
