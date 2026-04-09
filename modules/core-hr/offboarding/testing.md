# Offboarding — Testing

**Module:** Core HR
**Feature:** Offboarding
**Location:** `tests/ONEVO.Tests.Unit/Modules/CoreHR/OffboardingServiceTests.cs`

---

## Unit Tests

```csharp
public class OffboardingServiceTests
{
    private readonly Mock<IOffboardingRepository> _repoMock = new();
    private readonly OffboardingService _sut;

    [Fact]
    public async Task Start_offboarding_creates_record_and_lifecycle_event()
    {
        // Arrange
        // ... setup mocks for start offboarding creates record and lifecycle event

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Record created, events published
    }

    [Fact]
    public async Task Complete_offboarding_deactivates_user()
    {
        // Arrange
        // ... setup mocks for complete offboarding deactivates user

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // User is_active = false
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Start offboarding creates record and lifecycle event | Unit | Record created, events published |
| Complete offboarding deactivates user | Unit | User is_active = false |

## Related

- [[modules/core-hr/offboarding/overview|Offboarding Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
