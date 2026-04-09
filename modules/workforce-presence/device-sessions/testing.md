# Device Sessions — Testing

**Module:** Workforce Presence
**Feature:** Device Sessions
**Location:** `tests/ONEVO.Tests.Unit/Modules/WorkforcePresence/DeviceSessionServiceTests.cs`

---

## Unit Tests

```csharp
public class DeviceSessionServiceTests
{
    private readonly Mock<IDeviceSessionRepository> _repoMock = new();
    private readonly DeviceSessionService _sut;

    [Fact]
    public async Task Process_creates_session_record()
    {
        // Arrange
        // ... setup mocks for process creates session record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Session inserted
    }

    [Fact]
    public async Task Idle_above_threshold_creates_break()
    {
        // Arrange
        // ... setup mocks for idle above threshold creates break

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Break auto-detected
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Process creates session record | Unit | Session inserted |
| Idle above threshold creates break | Unit | Break auto-detected |

## Related

- [[modules/workforce-presence/device-sessions/overview|Device Sessions Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
