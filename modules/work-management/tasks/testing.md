# Task Management - Testing

**Module:** WorkSync
**Feature:** Task Management
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Tasks/`

---

## Unit Tests

```csharp
public class TaskServiceTests
{
    [Fact]
    public async Task CreateTask_GeneratesShortId_WithProjectIdentifier()
    {
        var project = new Project { Identifier = "TASK", WorkspaceId = _wsId };
        var result = await _sut.CreateAsync(_validCommand, default);
        result.IsSuccess.Should().BeTrue();
        result.Value!.ShortId.Should().MatchRegex(@"^TASK-\d+$");
    }

    [Fact]
    public async Task UpdateStatus_InvalidTransition_ReturnsFailure()
    {
        var task = new Task { Status = "done" };
        var result = await _sut.UpdateStatusAsync(task.Id, "in_progress", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("Invalid status transition");
    }

    [Fact]
    public async Task UpdateStatus_ToDone_WithApprovalRequired_ReturnsFailure()
    {
        SetupProjectStatusApprovalRequired();
        SetupNoApprovedApproval(taskId: _taskId);
        var result = await _sut.UpdateStatusAsync(_taskId, "done", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("APPROVAL_REQUIRED");
    }

    [Fact]
    public async Task UpdateStatus_ToDone_WithApprovalApproved_Succeeds()
    {
        SetupProjectStatusApprovalRequired();
        SetupApprovedApproval(taskId: _taskId);
        var result = await _sut.UpdateStatusAsync(_taskId, "done", default);
        result.IsSuccess.Should().BeTrue();
    }

    [Fact]
    public async Task MoveCard_ExceedsWipLimit_ReturnsFailure()
    {
        SetupColumnWithWipLimit(limit: 2, currentCount: 2);
        var result = await _sut.MoveCardAsync(_taskId, _columnId, default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("WIP_LIMIT_EXCEEDED");
    }

    [Fact]
    public async Task MoveCard_UpdatesTaskStatus_ToColumnStatusKey()
    {
        var column = new BoardColumn { StatusKey = "in_review", WipLimit = null };
        _columnRepoMock.Setup(r => r.GetByIdAsync(_columnId, default)).ReturnsAsync(column);
        await _sut.MoveCardAsync(_taskId, _columnId, default);
        _taskRepoMock.Verify(r => r.UpdateStatusAsync(_taskId, "in_review", default), Times.Once);
    }
}
```

## Integration Tests

```csharp
public class TaskEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task FullFlow_CreateTask_MoveToInProgress_Complete()
    {
        var task = await CreateTaskAsync("Fix login bug");
        task.Status.Should().Be("todo");
        task.ShortId.Should().StartWith("TASK-");

        await UpdateStatusAsync(task.Id, "in_progress");
        await UpdateStatusAsync(task.Id, "in_review");
        var done = await UpdateStatusAsync(task.Id, "done");
        done.Status.Should().Be("done");
    }

    [Fact]
    public async Task TenantIsolation_CannotSeeOtherTenantTasks()
    {
        var foreignTask = await CreateTaskInOtherTenantAsync();
        var response = await _client.GetAsync($"/api/v1/tasks/{foreignTask.Id}");
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task WorkspaceIsolation_CannotSeeOtherWorkspaceTasks()
    {
        var otherWsTask = await CreateTaskInOtherWorkspaceAsync();
        var response = await _client.GetAsync($"/api/v1/tasks/{otherWsTask.Id}");
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create task with valid data | Unit | Success, short_id generated |
| Invalid status transition | Unit | Failure with message |
| Done blocked by approval requirement | Unit | APPROVAL_REQUIRED error |
| Move card exceeds WIP limit | Unit | WIP_LIMIT_EXCEEDED error |
| Move card updates task.status | Unit | status = column.status_key |
| Full create -> complete flow | Integration | Status progresses correctly |
| Tenant isolation | Integration | Cannot access other tenant tasks |
| Workspace isolation | Integration | Cannot access other workspace tasks |
| Custom field required but null | Unit | Validation failure |

## Related

- [[modules/work-management/tasks/overview|Tasks Overview]]
- [[modules/work-management/tasks/end-to-end-logic|Tasks Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
