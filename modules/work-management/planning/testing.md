# Planning — Testing

**Module:** WorkSync
**Feature:** Planning
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Planning/`

---

## Unit Tests

```csharp
public class SprintServiceTests
{
    [Fact]
    public async Task ActivateSprint_WithExistingActiveSprint_ReturnsFailure()
    {
        SetupActiveSprintInProject(_projectId);
        var result = await _sut.ActivateAsync(_sprintId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("ACTIVE_SPRINT_EXISTS");
    }

    [Fact]
    public async Task ActivateSprint_MissingDates_ReturnsFailure()
    {
        var sprint = new Sprint { StartDate = null, EndDate = null };
        var result = await _sut.ActivateAsync(sprint.Id, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("start_date and end_date required");
    }

    [Fact]
    public async Task CompleteSprint_MovesIncompleteTasks_ToBacklog()
    {
        var sprint = SetupActiveSprintWithIncompleteTasks(3);
        await _sut.CompleteAsync(sprint.Id, default);
        _backlogRepoMock.Verify(r => r.RemoveFromSprintAsync(
            It.IsAny<Guid>(), It.IsAny<DateTime>(), default), Times.Exactly(3));
    }

    [Fact]
    public async Task AddTaskToSprint_AlreadyInSprint_ReturnsFailure()
    {
        SetupTaskAlreadyInSprint(_taskId, _sprintId);
        var result = await _sut.AddToSprintAsync(_sprintId, _taskId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("ALREADY_IN_SPRINT");
    }

    [Fact]
    public async Task DailySnapshot_WritesOneRowPerSprint()
    {
        SetupActiveSprints(5);
        await _sut.WriteSnapshotsAsync(DateOnly.FromDateTime(DateTime.Today), default);
        _snapshotRepoMock.Verify(r => r.UpsertAsync(
            It.IsAny<SprintDailySnapshot>(), default), Times.Exactly(5));
    }
}

public class BoardServiceTests
{
    [Fact]
    public async Task MoveCard_UpdatesTaskStatus_ToColumnStatusKey()
    {
        var column = new BoardColumn { StatusKey = "in_review", WipLimit = null };
        await _sut.MoveCardAsync(_taskId, column.Id, null, default);
        _taskRepoMock.Verify(r => r.UpdateStatusAsync(_taskId, "in_review", default), Times.Once);
    }

    [Fact]
    public async Task MoveCard_WipLimitReached_ReturnsFailure()
    {
        SetupColumnWipLimitReached(_columnId, limit: 3);
        var result = await _sut.MoveCardAsync(_taskId, _columnId, null, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("WIP_LIMIT_EXCEEDED");
    }
}
```

## Integration Tests

```csharp
public class SprintEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task FullSprintCycle_Create_Activate_Complete()
    {
        var sprint = await CreateSprintAsync("Sprint 1", startDate, endDate);
        await ActivateSprintAsync(sprint.Id);
        var task = await CreateAndAddTaskToSprintAsync(sprint.Id, storyPoints: 5);
        await CompleteTaskAsync(task.Id);
        var report = await CompleteSprintAsync(sprint.Id);
        report.CompletedPoints.Should().Be(5);
        report.CompletionRate.Should().Be(100);
    }

    [Fact]
    public async Task BurndownChart_HasSnapshotPerDay()
    {
        var sprint = await CreateActivatedSprintAsync();
        await TriggerDailySnapshotJobAsync();
        var burndown = await GetBurndownAsync(sprint.Id);
        burndown.Snapshots.Should().NotBeEmpty();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Activate with existing active sprint | Unit | ACTIVE_SPRINT_EXISTS |
| Activate with missing dates | Unit | Validation failure |
| Complete sprint moves incomplete tasks | Unit | removed_at set for incomplete items |
| Add duplicate task to sprint | Unit | ALREADY_IN_SPRINT |
| Daily snapshot writes one row per active sprint | Unit | N rows upserted |
| Move card updates task.status | Unit | status = column.status_key |
| WIP limit exceeded on card move | Unit | WIP_LIMIT_EXCEEDED |
| Full sprint lifecycle | Integration | Report generated correctly |
| Burndown snapshot present | Integration | At least one snapshot row |

## Related

- [[modules/work-management/planning/overview|Planning Overview]]
- [[modules/work-management/planning/end-to-end-logic|Planning Logic]]
