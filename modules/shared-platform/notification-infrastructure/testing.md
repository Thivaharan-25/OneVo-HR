# Notification Infrastructure — Testing

**Module:** Shared Platform
**Feature:** Notification Infrastructure
**Location:** `tests/ONEVO.Tests.Unit/Modules/SharedPlatform/NotificationPipelineServiceTests.cs`

---

## Unit Tests

```csharp
public class NotificationPipelineServiceTests
{
    private readonly Mock<INotificationPipelineRepository> _repoMock = new();
    private readonly NotificationPipelineService _sut;

    [Fact]
    public async Task Pipeline_renders_template_and_dispatches()
    {
        // Arrange
        // ... setup mocks for pipeline renders template and dispatches

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Email sent via Resend
    }

    [Fact]
    public async Task Escalation_rule_triggers_after_SLA()
    {
        // Arrange
        // ... setup mocks for escalation rule triggers after sla

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Reminder sent
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Pipeline renders template and dispatches | Unit | Email sent via Resend |
| Escalation rule triggers after SLA | Unit | Reminder sent |

## Related

- [[modules/shared-platform/notification-infrastructure/overview|Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
