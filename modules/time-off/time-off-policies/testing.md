# Time Off Policies - Testing

**Module:** Time Off
**Feature:** Time Off Policies
**Location:** `tests/ONEVO.Tests.Unit/Modules/TimeOff/TimeOffPolicyServiceTests.cs`

---

## Unit Tests

```csharp
public class TimeOffPolicyServiceTests
{
    private readonly Mock<ITimeOffPolicyRepository> _repoMock = new();
    private readonly TimeOffPolicyService _sut;

    [Fact]
    public async Task Create_policy_requires_permission_in_selected_company()
    {
        // Arrange
        // ... setup selected Company context and deny time_off:manage for that Company

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Permission failure
    }

    [Fact]
    public async Task Replace_policy_closes_old_policy_with_effective_to()
    {
        // Arrange
        // ... setup existing active policy in the selected Company

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Old policy effective_to is set before the new policy effective_from
        // New policy is active in the selected Company
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create policy without permission in selected Company | Unit | Failure |
| Create policy with permission in selected Company | Unit | Policy `legal_entity_id` comes from topbar Company context |
| Replace active policy | Unit | Old policy gets `effective_to`; new policy starts at `effective_from` |
| List policies | Unit/API | Returns policies for selected Company only |

## Related

- [[modules/time-off/time-off-policies/overview|Time Off Policies Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
