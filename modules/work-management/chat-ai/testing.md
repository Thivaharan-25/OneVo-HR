# Chat AI - Testing

**Phase:** Phase 2. Not part of Phase 1 implementation scope.

**Module:** WorkSync
**Feature:** Chat AI / ONEVO Semantic Kernel Assistant
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/ChatAI/`

---

## Unit Tests

```csharp
public class SemanticKernelChatOrchestratorTests
{
    [Fact]
    public async Task ProcessMessage_WithoutPremiumAi_SkipsKernel()
    {
        SetupTenantWithoutPremiumAi();

        await _sut.ProcessMessageAsync(_messageId, default);

        _kernelMock.Verify(k => k.InvokeAsync(It.IsAny<KernelArguments>(), default), Times.Never);
    }

    [Fact]
    public async Task ProcessMessage_UserWithoutPermission_DoesNotRegisterRestrictedFunction()
    {
        SetupUserPermissions("chat:read");

        await _sut.ProcessMessageAsync(_messageId, default);

        _pluginRegistryMock.Verify(r =>
            r.RegisterFunction("WorkSync.CreateTask", It.IsAny<KernelFunction>()), Times.Never);
    }

    [Fact]
    public async Task ReadOnlyAnswer_CreatesAssistantMessage()
    {
        SetupKernelReadOnlyAnswer("3 overdue tasks need review.");

        await _sut.ProcessMessageAsync(_messageId, default);

        _messageRepoMock.Verify(r =>
            r.InsertAsync(It.Is<Message>(m =>
                m.SenderType == "assistant" &&
                m.ContentType == "ai_answer"), default), Times.Once);
    }

    [Fact]
    public async Task ToolAction_CreatesPendingActionJob()
    {
        SetupKernelToolCall("WorkSync.CreateTask");

        await _sut.ProcessMessageAsync(_messageId, default);

        _jobRepoMock.Verify(r =>
            r.InsertAsync(It.Is<AiActionJob>(j =>
                j.Status == "pending" &&
                j.SourceMessageId == _messageId), default), Times.Once);
    }

    [Fact]
    public async Task TeamsMessage_UnmappedSender_SkipsAssistantTools()
    {
        SetupImportedTeamsMessage(mappedUserId: null);

        await _sut.ProcessMessageAsync(_messageId, default);

        _kernelMock.Verify(k => k.InvokeAsync(It.IsAny<KernelArguments>(), default), Times.Never);
    }
}

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
}
```

## Integration Tests

```csharp
public class AiActionJobEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task AssistantRun_ReadOnlyQuestion_ReturnsAssistantMessage()
    {
        var response = await PostAssistantRunAsync(_channelId, "What tasks are overdue?");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        await AssertAssistantMessageCreatedAsync(_channelId);
        await AssertSignalRPublishedAsync("chat:message", _channelId);
    }

    [Fact]
    public async Task AssistantRun_ActionIntent_PublishesPendingAction()
    {
        var response = await PostAssistantRunAsync(_channelId, "Create a task for Sarah to review payroll.");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        await AssertPendingAiActionCreatedAsync(_channelId);
        await AssertSignalRPublishedAsync("ai:action_pending", _channelId);
    }

    [Fact]
    public async Task UndoFlow_WithinWindow_CancelsAction()
    {
        var jobId = await CreatePendingAssistantActionAsync();
        var response = await _client.DeleteAsync($"/api/v1/ai-actions/{jobId}/undo");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var job = await GetJobAsync(jobId);
        job.Status.Should().Be("undone");
    }

    [Fact]
    public async Task FinalizeJob_HangfireProcess_CreatesEntity()
    {
        var jobId = await CreatePendingJobAsync(undoWindow: TimeSpan.FromMilliseconds(100));
        await System.Threading.Tasks.Task.Delay(200);
        await TriggerFinalizeJobAsync();

        var job = await GetJobAsync(jobId);
        job.Status.Should().Be("finalized");
    }

    [Fact]
    public async Task ImportedTeamsMessage_MappedSender_CanInvokeAssistant()
    {
        await ImportTeamsMessageAsync(_channelId, _teamsMessageId, mappedUserId: _userId);

        await AssertAssistantRunCreatedAsync(_channelId);
        await AssertNoDuplicateMessageForExternalIdAsync(_teamsMessageId);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Tenant without Agentic Chat / `premium_ai` | Unit | Kernel is not invoked |
| User lacks tool permission | Unit | Restricted Kernel function is not registered |
| Read-only answer | Unit + Integration | Assistant message stored with `sender_type = assistant` |
| Action intent | Unit + Integration | `premium_ai_detections` and pending `ai_action_jobs` rows created |
| Undo within 10s window | Unit + Integration | status = undone, entity not created |
| Undo after window expired | Unit | `UNDO_WINDOW_EXPIRED` error |
| Undo with `tag_execution_id` | Unit | Both job and tag execution undone |
| Finalize already-finalized | Unit | Idempotent, no double creation |
| Hangfire finalize | Integration | Entity created, status = finalized |

## Related

- [[modules/work-management/chat-ai/overview|Chat AI Overview]]
- [[modules/work-management/chat-ai/end-to-end-logic|Chat AI Logic]]
- [[modules/shared-platform/chatbot-api-integration|Semantic Kernel Assistant Integration]]
- [[code-standards/testing-strategy|Testing Standards]]
