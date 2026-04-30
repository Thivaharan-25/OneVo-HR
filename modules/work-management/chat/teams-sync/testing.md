# Teams Chat Sync - Testing

**Module:** WorkSync
**Feature:** Teams Chat Sync
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
        SetupGraphSendMessage("teams-message-1");

        var result = await _sut.SendOneVoMessageToTeamsAsync(_messageId, default);

        result.IsSuccess.Should().BeTrue();
        await AssertSyncStateExists(_messageId, "teams-message-1");
    }

    [Fact]
    public async Task ImportTeamsMessage_DuplicateExternalId_IsNoOp()
    {
        SetupExistingSyncState("teams-message-1");
        var result = await _sut.ImportTeamsMessageAsync(BuildWebhook("teams-message-1"), default);
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
        var response = await PostOneVoMessageAsync(_channelId, "Hello Teams");
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var dto = await response.ReadAsAsync<MessageDto>();
        dto.SyncStatus.Should().BeOneOf("pending", "synced");
    }

    [Fact]
    public async Task TeamsWebhook_NewMessage_CreatesOneVoMessageAndPushesSignalR()
    {
        SetupGraphDeltaMessage("teams-message-1", "Hello OneVo");
        await PostTeamsWebhookAsync();
        await AssertOneVoMessageImported("teams-message-1");
        AssertSignalRMessageCreatedPublished();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Send ONEVO message to linked Teams channel | Unit + Integration | Graph send called; sync state stored |
| Send ONEVO message to unlinked channel | Unit | Local-only message |
| User lacks Teams connection | Unit | `sync_status = not_linked` |
| Graph send timeout | Unit | Retry queued, no duplicate local message |
| Inbound Teams message | Integration | ONEVO message created |
| Duplicate inbound Teams webhook | Integration | No duplicate message |
| Teams edit imported | Unit | ONEVO message updated and `is_edited = true` |
| Teams delete imported | Unit | ONEVO message soft-deleted |
| ONEVO delete outbound | Unit | Local soft delete always; Teams delete only if policy allows |
| Attachment inbound blocked by policy | Unit | Message imported; attachment marked failed |
| Unmatched Teams sender | Unit | External participant or skip according to tenant policy |

---

## Related

- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync Logic]]
- [[modules/work-management/chat/testing|Chat Testing]]
- [[modules/integrations/microsoft-teams/testing|Microsoft Teams Integration Testing]]
