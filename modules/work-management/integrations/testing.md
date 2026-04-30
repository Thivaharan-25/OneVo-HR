# Integration & API — Testing

**Module:** WorkSync
**Feature:** Integration & API
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Integrations/`

---

## Unit Tests

```csharp
public class WebhookServiceTests
{
    [Fact]
    public async Task ProcessWebhook_InvalidHmac_ReturnsUnauthorized()
    {
        var result = await _sut.ProcessWebhookAsync(_repoId,
            rawBody: "payload", hmacHeader: "sha256=invalid", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("INVALID_SIGNATURE");
    }

    [Fact]
    public async Task ProcessCommit_ParsesTaskIdsFromMessage()
    {
        var commitMsg = "Fix login [TASK-123] and also #456";
        var taskIds = _sut.ParseTaskIds(commitMsg);
        taskIds.Should().HaveCount(2);
    }

    [Fact]
    public async Task ProcessCommit_NoTaskIds_InsertsEmptyArray()
    {
        var commitMsg = "Update README";
        var taskIds = _sut.ParseTaskIds(commitMsg);
        taskIds.Should().BeEmpty();
    }
}

public class AutomationRuleServiceTests
{
    [Fact]
    public async Task EvaluateRules_BranchPatternMatch_ExecutesAction()
    {
        var rule = new TaskAutomationRule
        {
            TriggerType = "pr_merged",
            IsActive = true,
            ConditionJson = """{ "branch_pattern": "main" }""",
            ActionType = "update_task_status",
            ActionParamsJson = """{ "new_status": "done" }"""
        };
        var @event = new CodeActivityEvent { EventType = "pr_merged", PayloadJson = """{ "branch": "main" }""" };
        var result = await _sut.EvaluateAsync(rule, @event, default);
        result.Executed.Should().BeTrue();
    }

    [Fact]
    public async Task EvaluateRules_BranchPatternMismatch_SkipsAction()
    {
        var rule = BuildRule(branchPattern: "release/*");
        var @event = BuildEvent(branch: "feature/login");
        var result = await _sut.EvaluateAsync(rule, @event, default);
        result.Executed.Should().BeFalse();
    }

    [Fact]
    public async Task EvaluateRules_DuplicateEvent_IsIdempotent()
    {
        SetupAlreadyProcessed(_ruleId, _eventId);
        await _sut.EvaluateAsync(_rule, _event, default);
        _actionExecutorMock.Verify(e => e.ExecuteAsync(It.IsAny<TaskAutomationRule>(), default), Times.Never);
    }
}
```

## Integration Tests

```csharp
public class WebhookEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task ReceiveValidWebhook_CreatesCodeActivityEvent()
    {
        var payload = BuildGithubPushPayload();
        var hmac = ComputeHmac(_repo.WebhookSecret, payload);
        var response = await _client.PostAsync(
            $"/api/v1/webhooks/github/{_repo.Id}",
            new StringContent(payload),
            hmacHeader: $"sha256={hmac}");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var events = await GetCodeActivityEventsAsync(_repo.Id);
        events.Should().HaveCount(1);
    }

    [Fact]
    public async Task ReceiveWebhook_InvalidSignature_Returns401()
    {
        var response = await _client.PostAsync(
            $"/api/v1/webhooks/github/{_repo.Id}",
            new StringContent("payload"),
            hmacHeader: "sha256=badsignature");
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Invalid HMAC | Unit + Integration | 401 Unauthorized |
| Parse [TASK-123] from commit | Unit | task_ids populated |
| Parse #456 from commit | Unit | task_ids populated |
| No task ID in commit | Unit | Empty array |
| Branch pattern match → execute action | Unit | Action executed |
| Branch pattern mismatch → skip | Unit | Action not executed |
| Duplicate event (idempotency) | Unit | Action not re-executed |
| Valid webhook creates event | Integration | code_activity_events row created |
| Invalid HMAC returns 401 | Integration | 401 returned |

## Related

- [[modules/work-management/integrations/overview|Integrations Overview]]
- [[modules/work-management/integrations/end-to-end-logic|Integrations Logic]]
