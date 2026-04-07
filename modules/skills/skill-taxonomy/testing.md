# Skill Taxonomy — Testing

**Module:** Skills
**Feature:** Skill Taxonomy
**Location:** `tests/ONEVO.Tests.Unit/Modules/Skills/SkillTaxonomyServiceTests.cs`

---

## Unit Tests

```csharp
public class SkillTaxonomyServiceTests
{
    private readonly Mock<ISkillTaxonomyRepository> _repoMock = new();
    private readonly SkillTaxonomyService _sut;

    [Fact]
    public async Task Create_category_validates_unique_name()
    {
        // Arrange
        // ... setup mocks for create category validates unique name

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Category created
    }

    [Fact]
    public async Task Create_skill_validates_proficiency_levels()
    {
        // Arrange
        // ... setup mocks for create skill validates proficiency levels

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 5 levels required
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create category validates unique name | Unit | Category created |
| Create skill validates proficiency levels | Unit | 5 levels required |

## Related

- [[skill-taxonomy]] — feature overview
- [[testing/README|Testing Standards]] — project-wide testing conventions
