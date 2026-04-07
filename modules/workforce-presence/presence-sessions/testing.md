# Presence Sessions — Testing

**Module:** Workforce Presence
**Feature:** Presence Sessions
**Location:** `tests/ONEVO.Tests.Unit/Modules/WorkforcePresence/PresenceReconciliationServiceTests.cs`

---

## Unit Tests

```csharp
public class PresenceReconciliationServiceTests
{
    private readonly Mock<IPresenceReconciliationRepository> _repoMock = new();
    private readonly PresenceReconciliationService _sut;

    [Fact]
    public async Task Reconcile_merges_biometric_and_agent_data()
    {
        // Arrange
        // ... setup mocks for reconcile merges biometric and agent data

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Unified session created
    }

    [Fact]
    public async Task First_seen_uses_earliest_source()
    {
        // Arrange
        // ... setup mocks for first seen uses earliest source

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // MIN of all sources
    }

    [Fact]
    public async Task On_leave_status_from_leave_module()
    {
        // Arrange
        // ... setup mocks for on leave status from leave module

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = on_leave
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Reconcile merges biometric and agent data | Unit | Unified session created |
| First seen uses earliest source | Unit | MIN of all sources |
| On leave status from leave module | Unit | Status = on_leave |

## Related

- [[presence-sessions|Presence Sessions Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
