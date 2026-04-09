# Onboarding — Testing

**Module:** Core HR
**Feature:** Onboarding
**Location:** `tests/ONEVO.Tests.Unit/Modules/CoreHR/OnboardingServiceTests.cs`

---

## Unit Tests

```csharp
public class OnboardingServiceTests
{
    private readonly Mock<IOnboardingRepository> _repoMock = new();
    private readonly OnboardingService _sut;

    [Fact]
    public async Task Start_onboarding_creates_tasks_from_template()
    {
        // Arrange
        // ... setup mocks for start onboarding creates tasks from template

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Tasks created from template
    }

    [Fact]
    public async Task No_template_returns_error()
    {
        // Arrange
        // ... setup mocks for no template returns error

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 400 returned
    }

    [Fact]
    public async Task Complete_task_updates_status()
    {
        // Arrange
        // ... setup mocks for complete task updates status

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status set to completed
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Start onboarding creates tasks from template | Unit | Tasks created from template |
| No template returns error | Unit | 400 returned |
| Complete task updates status | Unit | Status set to completed |

## Related

- [[modules/core-hr/onboarding/overview|Onboarding Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
