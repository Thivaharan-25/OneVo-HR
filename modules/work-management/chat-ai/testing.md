# Chat AI — Testing

**Module:** WorkSync
**Feature:** Chat AI
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/ChatAI/`

---

## Unit Tests

```csharp
public class AiActionJobServiceTests
{
    [Fact]
    public async Task UndoAction_WithinWindow_SetsStatusUndone()
    {
        var job = new AiActionJob
        {
            Status = "pending",
            UndoExpiresAt = DateTime.UtcNow.AddSeconds(5),
            TagExecutionId = null
        };
        _jobRepoMock.Setup(r => r.GetByIdAsync(job.Id, default)).ReturnsAsync(job);

        var result = await _sut.UndoAsync(job.Id, default);

        result.IsSuccess.Should().BeTrue();
        job.Status.Should().Be("undone");
        job.UndoneAt.Should().NotBeNull();
    }

    [Fact]
    public async Task UndoAction_AfterWindowExpired_ReturnsFailure()
    {
        var job = new AiActionJob
        {
            Status = "pending",
            UndoExpiresAt = DateTime.UtcNow.AddSeconds(-1)
        };
        _jobRepoMock.Setup(r => r.GetByIdAsync(job.Id, default)).ReturnsAsync(job);

        var result = await _sut.UndoAsync(job.Id, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("UNDO_WINDOW_EXPIRED");
    }

    [Fact]
    public async Task UndoAction_WithTagExecutionId_AlsoUndoesTagExecution()
    {
        var job = new AiActionJob
        {
            Status = "pending",
            UndoExpiresAt = DateTime.UtcNow.AddSeconds(10),
            TagExecutionId = _tagExecutionId
        };
        _jobRepoMock.Setup(r => r.GetByIdAsync(job.Id, default)).ReturnsAsync(job);

        await _sut.UndoAsync(job.Id, default);

        _tagExecRepoMock.Verify(r =>
            r.UpdateStatusAsync(_tagExecutionId, "undone", default), Times.Once);
    }

    [Fact]
    public async Task FinalizeJob_AlreadyFinalized_IsIdempotent()
    {
        var job = new AiActionJob { Status = "finalized" };
        var result = await _sut.FinalizeAsync(job.Id, default);
        result.IsSuccess.Should().BeTrue();
        _entityCreatorMock.Verify(c => c.CreateAsync(It.IsAny<AiActionJob>(), default), Times.Never);
    }

    [Fact]
    public async Task ChatAIDetection_WithoutPremiumFlag_SkipsDetection()
    {
        SetupTenantWithoutPremiumAi();
        await _sut.ProcessMessageAsync(_messageId, default);
        _aiServiceMock.Verify(a => a.DetectIntentAsync(It.IsAny<string>(), default), Times.Never);
    }
}
```

## Integration Tests

```csharp
public class AiActionJobEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task UndoFlow_WithinWindow_CancelsAction()
    {
        var jobId = await SimulateAiDetectionAsync();
        var response = await _client.DeleteAsync($"/api/v1/ai-actions/{jobId}/undo");
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var job = await GetJobAsync(jobId);
        job.Status.Should().Be("undone");
    }

    [Fact]
    public async Task FinalizeJob_HangfireProcess_CreatesEntity()
    {
        var jobId = await CreatePendingJobAsync(undoWindow: TimeSpan.FromMilliseconds(100));
        await System.Threading.Tasks.Task.Delay(200); // let window expire
        await TriggerFinalizeJobAsync();

        var job = await GetJobAsync(jobId);
        job.Status.Should().Be("finalized");
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Undo within 10s window | Unit | status = undone |
| Undo after window expired | Unit | UNDO_WINDOW_EXPIRED error |
| Undo with tag_execution_id | Unit | Both job and tag execution undone |
| Finalize already-finalized | Unit | Idempotent — no double creation |
| Detection without premium_ai | Unit | AI service not called |
| Full undo flow | Integration | Status = undone, entity not created |
| Hangfire finalize | Integration | Entity created, status = finalized |

## Related

- [[modules/work-management/chat-ai/overview|Chat AI Overview]]
- [[modules/work-management/chat-ai/end-to-end-logic|Chat AI Logic]]
- [[code-standards/testing-strategy|Testing Standards]]
