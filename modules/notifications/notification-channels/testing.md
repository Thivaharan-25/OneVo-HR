# Notification Channels — Testing

**Module:** Notifications
**Feature:** Notification Channels
**Location:** `tests/ONEVO.Tests.Unit/Modules/Notifications/NotificationChannelServiceTests.cs`

---

## Unit Tests

```csharp
public class NotificationChannelServiceTests
{
    private readonly Mock<INotificationChannelRepository> _repoMock = new();
    private readonly NotificationChannelService _sut;

    [Fact]
    public async Task Send_via_email_calls_Resend_API()
    {
        // Arrange
        // ... setup mocks for send via email calls resend api

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Email dispatched
    }

    [Fact]
    public async Task Inactive_channel_skipped()
    {
        // Arrange
        // ... setup mocks for inactive channel skipped

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No dispatch
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Send via email calls Resend API | Unit | Email dispatched |
| Inactive channel skipped | Unit | No dispatch |

## Related

- [[notifications/notification-channels/overview|Notification Channels Overview]]
- [[testing/README|Testing Standards]]
