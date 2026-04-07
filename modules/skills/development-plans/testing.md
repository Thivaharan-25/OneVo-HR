# Development Plans — Testing

**Module:** Skills
**Feature:** Development Plans
**Location:** `tests/ONEVO.Tests.Unit/Modules/Skills/DevelopmentPlanServiceTests.cs`

---

## Unit Tests

```csharp
public class DevelopmentPlanServiceTests
{
    private readonly Mock<IDevelopmentPlanRepository> _repoMock = new();
    private readonly DevelopmentPlanService _sut;

    [Fact]
    public async Task Create_plan_with_milestones()
    {
        // Arrange
        // ... setup mocks for create plan with milestones

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Items created
    }

    [Fact]
    public async Task All_items_completed_completes_plan()
    {
        // Arrange
        // ... setup mocks for all items completed completes plan

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Plan status = completed
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create plan with milestones | Unit | Items created |
| All items completed completes plan | Unit | Plan status = completed |

## Related

- [[development-plans]] — feature overview
- [[testing/README|Testing Standards]] — project-wide testing conventions
