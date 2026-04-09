# Escalation Chains — Testing

**Module:** Exception Engine
**Feature:** Escalation Chains
**Location:** `tests/ONEVO.Tests.Unit/Modules/ExceptionEngine/EscalationServiceTests.cs`

---

## Unit Tests

```csharp
public class EscalationServiceTests
{
    private readonly Mock<IEscalationRepository> _repoMock = new();
    private readonly EscalationService _sut;

    [Fact]
    public async Task Unacknowledged_alert_escalated_after_delay()
    {
        // Arrange
        // ... setup mocks for unacknowledged alert escalated after delay

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Alert status escalated
    }

    [Fact]
    public async Task Chain_configured_per_severity()
    {
        // Arrange
        // ... setup mocks for chain configured per severity

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Correct steps created
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Unacknowledged alert escalated after delay | Unit | Alert status escalated |
| Chain configured per severity | Unit | Correct steps created |

## Related

- [[frontend/architecture/overview|Escalation Chains Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
