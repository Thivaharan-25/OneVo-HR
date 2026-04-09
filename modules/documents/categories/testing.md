# Categories — Testing

**Module:** Documents
**Feature:** Categories
**Location:** `tests/ONEVO.Tests.Unit/Modules/Documents/CategoryServiceTests.cs`

---

## Unit Tests

```csharp
public class CategoryServiceTests
{
    private readonly Mock<ICategoryRepository> _repoMock = new();
    private readonly CategoryService _sut;

    [Fact]
    public async Task Create_category_with_parent_builds_hierarchy()
    {
        // Arrange
        // ... setup mocks for create category with parent builds hierarchy

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Parent linked correctly
    }

    [Fact]
    public async Task Max_depth_3_enforced()
    {
        // Arrange
        // ... setup mocks for max depth 3 enforced

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Validation failure at depth 4
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create category with parent builds hierarchy | Unit | Parent linked correctly |
| Max depth 3 enforced | Unit | Validation failure at depth 4 |

## Related

- [[frontend/architecture/overview|Categories Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
