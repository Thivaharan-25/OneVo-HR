# Goals / OKR — Testing

**Module:** Performance
**Feature:** Goals / OKR
**Location:** `tests/ONEVO.Tests.Unit/Modules/Performance/GoalServiceTests.cs`

---

## Unit Tests

```csharp
public class GoalServiceTests
{
    private readonly Mock<IGoalRepository> _repoMock = new();
    private readonly GoalService _sut;

    [Fact]
    public async Task Create_goal_with_parent_validates_hierarchy()
    {
        // Arrange
        // ... setup mocks for create goal with parent validates hierarchy

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Cascading OKR linked
    }

    [Fact]
    public async Task Update_progress_auto-completes_at_target()
    {
        // Arrange
        // ... setup mocks for update progress auto-completes at target

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = completed
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create goal with parent validates hierarchy | Unit | Cascading OKR linked |
| Update progress auto-completes at target | Unit | Status = completed |

## Related

- [[modules/performance/goals-okr/overview|Goals & OKR Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
