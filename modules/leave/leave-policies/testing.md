# Leave Policies — Testing

**Module:** Leave
**Feature:** Leave Policies
**Location:** `tests/ONEVO.Tests.Unit/Modules/Leave/LeavePolicyServiceTests.cs`

---

## Unit Tests

```csharp
public class LeavePolicyServiceTests
{
    private readonly Mock<ILeavePolicyRepository> _repoMock = new();
    private readonly LeavePolicyService _sut;

    [Fact]
    public async Task Create_policy_versions_existing_one()
    {
        // Arrange
        // ... setup mocks for create policy versions existing one

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Old policy superseded
    }

    [Fact]
    public async Task Active_policy_has_superseded_by_id_=_null()
    {
        // Arrange
        // ... setup mocks for active policy has superseded_by_id = null

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Query filter works
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create policy versions existing one | Unit | Old policy superseded |
| Active policy has superseded_by_id = null | Unit | Query filter works |

## Related

- [[modules/leave/leave-policies/overview|Leave Policies Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
