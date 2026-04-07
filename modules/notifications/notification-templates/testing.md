# Notification Templates — Testing

**Module:** Notifications
**Feature:** Notification Templates
**Location:** `tests/ONEVO.Tests.Unit/Modules/Notifications/NotificationTemplateServiceTests.cs`

---

## Unit Tests

```csharp
public class NotificationTemplateServiceTests
{
    private readonly Mock<INotificationTemplateRepository> _repoMock = new();
    private readonly NotificationTemplateService _sut;

    [Fact]
    public async Task Template_renders_with_variables()
    {
        // Arrange
        // ... setup mocks for template renders with variables

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Variables substituted
    }

    [Fact]
    public async Task Inactive_template_skipped()
    {
        // Arrange
        // ... setup mocks for inactive template skipped

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // No notification sent
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Template renders with variables | Unit | Variables substituted |
| Inactive template skipped | Unit | No notification sent |

## Related

- [[notifications/notification-templates/overview|Notification Templates Overview]]
- [[testing/README|Testing Standards]]
