# Chat & Messaging - Testing

**Phase:** Phase 2 - deferred
**Phase 1 Status:** Not active in current Phase 1 Work implementation; retained as future design reference.

**Module:** WorkSync
**Feature:** Chat & Messaging
**Location:** `tests/ONEVO.Tests.Unit/Features/WorkSync/Chat/`

---

## Unit Tests

```csharp
public class ChannelServiceTests
{
    [Fact]
    public async Task CreateDMChannel_AlreadyExists_ReturnsExisting()
    {
        SetupExistingDMChannel(_userId, _otherUserId, _existingChannelId);
        var result = await _sut.GetOrCreateDMAsync(_userId, _otherUserId, default);
        result.IsSuccess.Should().BeTrue();
        result.Value!.Id.Should().Be(_existingChannelId); // idempotent
        _channelRepoMock.Verify(r => r.InsertAsync(It.IsAny<Channel>(), default), Times.Never);
    }

    [Fact]
    public async Task SendMessage_ToChannelNotMemberOf_ReturnsFailure()
    {
        SetupUserNotMember(_channelId, _userId);
        var result = await _sut.SendAsync(_channelId, _userId, "Hello", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("NOT_CHANNEL_MEMBER");
    }

    [Fact]
    public async Task SendReply_ToThreadReply_ReturnsFailure()
    {
        var parentMsg = new Message { ParentMessageId = Guid.NewGuid() }; // already a reply
        _msgRepoMock.Setup(r => r.GetByIdAsync(_parentId, default)).ReturnsAsync(parentMsg);
        var result = await _sut.SendReplyAsync(_channelId, _parentId, "Nested", default);
        result.IsSuccess.Should().BeFalse();
        result.Error!.Code.Should().Be("CANNOT_NEST_THREADS");
    }

    [Fact]
    public async Task SoftDeleteMessage_RetainsContent()
    {
        var message = new Message { Content = "Important message", SenderId = _userId };
        await _sut.DeleteAsync(message.Id, _userId, default);
        message.IsDeleted.Should().BeTrue();
        message.Content.Should().Be("Important message"); // content retained
    }

    [Fact]
    public async Task UnreadCount_UsesLastReadAt()
    {
        SetupMessages(_channelId, count: 10, newestAt: DateTime.UtcNow);
        SetupLastReadAt(_channelId, _userId, DateTime.UtcNow.AddMinutes(-5));
        var count = await _sut.GetUnreadCountAsync(_channelId, _userId, default);
        count.Should().BeGreaterThan(0);
    }
}
```

## Integration Tests

```csharp
public class ChatEndpointTests : IClassFixture<ONEVOWebFactory>
{
    [Fact]
    public async Task SendMessage_SignalREventFired()
    {
        var hubMock = ResolveWorkSyncChatHubMock();
        await SendMessageAsync(_channelId, "Hello");
        hubMock.VerifyPublished("chat:message", _channelId, Times.Once);
    }

    [Fact]
    public async Task GetOrCreateDM_CalledTwice_ReturnsSameChannel()
    {
        var dm1 = await CreateDMAsync(_userId, _otherUserId);
        var dm2 = await CreateDMAsync(_userId, _otherUserId);
        dm1.Id.Should().Be(dm2.Id);
    }

    [Fact]
    public async Task SendMessage_LinkedTeamsChannel_QueuesTeamsSync()
    {
        SetupLinkedTeamsChannel(_channelId);
        await AssertTeamsSyncQueued(_channelId);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| DM channel already exists - returns existing | Unit + Integration | Idempotent, same channel |
| Send to channel without membership | Unit | NOT_CHANNEL_MEMBER |
| Reply to a thread reply (nested) | Unit | CANNOT_NEST_THREADS |
| Soft delete retains content | Unit | Content preserved, is_deleted = true |
| Unread count based on last_read_at | Unit | Count > 0 when messages after last read |
| SignalR fired on message | Integration | WorkSync chat hub publishes canonical `chat:message` payload |
| Assistant message created | Integration | Assistant message stored and `chat:message` plus `ai:*` events published |

## Related

- [[modules/work-management/chat/overview|Chat Overview]]
- [[modules/work-management/chat/end-to-end-logic|Chat Logic]]
