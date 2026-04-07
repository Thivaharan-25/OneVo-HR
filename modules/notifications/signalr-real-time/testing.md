# SignalR Real-Time — Testing

**Module:** Notifications
**Feature:** SignalR Real-Time
**Location:** `tests/ONEVO.Tests.Unit/Modules/Notifications/SignalRNotificationServiceTests.cs`

---

## Unit Tests

```csharp
public class SignalRNotificationServiceTests
{
    private readonly Mock<ISignalRNotificationRepository> _repoMock = new();
    private readonly SignalRNotificationService _sut;

    [Fact]
    public async Task Connected_user_receives_push()
    {
        // Arrange
        // ... setup mocks for connected user receives push

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Message sent via hub
    }

    [Fact]
    public async Task Disconnected_user_gets_in-app_notification()
    {
        // Arrange
        // ... setup mocks for disconnected user gets in-app notification

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Queued for next login
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Connected user receives push | Unit | Message sent via hub |
| Disconnected user gets in-app notification | Unit | Queued for next login |

## Related

- [[notifications/signalr-real-time/overview|SignalR Real-Time Overview]]
- [[testing/README|Testing Standards]]
