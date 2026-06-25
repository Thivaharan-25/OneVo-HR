
**Module:** WorkSync
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Chat/TeamsSync/`

---

## Unit Tests

```csharp
public class TeamsChatSyncTests
{
    [Fact]
    public async Task SendMessage_ChannelLinked_SendsToTeamsAndStoresExternalId()
    {
        SetupChannelTeamsLink(_channelId, _teamsChannelId);
        SetupUserTeamsConnection(_userId, _teamsUserId);

        var result = await _sut.SendOneVoMessageToTeamsAsync(_messageId, default);

        result.IsSuccess.Should().BeTrue();
    }

    [Fact]
    public async Task ImportTeamsMessage_DuplicateExternalId_IsNoOp()
    {
        result.IsSuccess.Should().BeTrue();
        _messageRepo.Verify(r => r.InsertAsync(It.IsAny<Message>(), default), Times.Never);
    }

    [Fact]
    public async Task OutboundSync_UserNotLinked_MarksMessageNotLinked()
    {
        SetupChannelTeamsLink(_channelId, _teamsChannelId);
        SetupNoUserTeamsConnection(_userId);
        var result = await _sut.SendOneVoMessageToTeamsAsync(_messageId, default);
        result.IsSuccess.Should().BeFalse();
        await AssertMessageSyncStatus(_messageId, "not_linked");
    }
}
```

## Integration Tests

```csharp
public class TeamsChatSyncEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task PostMessage_LinkedChannel_ReturnsMessageWithSyncPending()
    {
        SetupLinkedTeamsChannel();
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var dto = await response.ReadAsAsync<MessageDto>();
        dto.SyncStatus.Should().BeOneOf("pending", "synced");
    }

    [Fact]
    public async Task TeamsWebhook_NewMessage_CreatesOneVoMessageAndPushesSignalR()
    {
        await PostTeamsWebhookAsync();
        AssertSignalRMessageCreatedPublished();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Send ONEVO message to unlinked channel | Unit | Local-only message |
| Graph send timeout | Unit | Retry queued, no duplicate local message |
| Attachment inbound blocked by policy | Unit | Message imported; attachment marked failed |

---

## Related

- [[modules/work-management/chat/testing|Chat Testing]]
- [[modules/integrations/microsoft-teams/testing|Microsoft Teams Integration Testing]]
