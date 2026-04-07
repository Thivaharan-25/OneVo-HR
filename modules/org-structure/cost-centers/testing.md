# Cost Centers — Testing

**Module:** Org Structure
**Feature:** Cost Centers
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/CostCenterServiceTests.cs`

---

## Unit Tests

```csharp
public class CostCenterServiceTests
{
    private readonly Mock<ICostCenterRepository> _repoMock = new();
    private readonly CostCenterService _sut;

    [Fact]
    public async Task Create_cost_center_validates_unique_code()
    {
        // Arrange
        // ... setup mocks for create cost center validates unique code

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Cost center created
    }

    [Fact]
    public async Task Assign_department_to_cost_center()
    {
        // Arrange
        // ... setup mocks for assign department to cost center

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Department updated
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create cost center validates unique code | Unit | Cost center created |
| Assign department to cost center | Unit | Department updated |

## Related

- [[cost-centers|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
