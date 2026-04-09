# Employee Skills — Testing

**Module:** Skills
**Feature:** Employee Skills
**Location:** `tests/ONEVO.Tests.Unit/Modules/Skills/SkillsServiceTests.cs`

---

## Unit Tests

```csharp
public class SkillsServiceTests
{
    private readonly Mock<ISkillsRepository> _repoMock = new();
    private readonly SkillsService _sut;

    [Fact]
    public async Task Get_skills_returns_with_proficiency()
    {
        // Arrange
        // ... setup mocks for get skills returns with proficiency

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Skills with levels
    }

    [Fact]
    public async Task Gap_analysis_compares_against_requirements()
    {
        // Arrange
        // ... setup mocks for gap analysis compares against requirements

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Gaps identified
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Get skills returns with proficiency | Unit | Skills with levels |
| Gap analysis compares against requirements | Unit | Gaps identified |

## Related

- [[modules/skills/employee-skills/overview|Employee Skills]] — feature overview
- [[code-standards/testing-strategy|Testing Standards]] — project-wide testing conventions
