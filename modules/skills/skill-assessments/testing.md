# Skill Assessments — Testing

**Module:** Skills
**Feature:** Skill Assessments
**Location:** `tests/ONEVO.Tests.Unit/Modules/Skills/SkillAssessmentServiceTests.cs`

---

## Unit Tests

```csharp
public class SkillAssessmentServiceTests
{
    private readonly Mock<ISkillAssessmentRepository> _repoMock = new();
    private readonly SkillAssessmentService _sut;

    [Fact]
    public async Task MCQ_auto-scored_correctly()
    {
        // Arrange
        // ... setup mocks for mcq auto-scored correctly

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Score calculated
    }

    [Fact]
    public async Task Validation_request_notifies_validator()
    {
        // Arrange
        // ... setup mocks for validation request notifies validator

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Notification sent
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| MCQ auto-scored correctly | Unit | Score calculated |
| Validation request notifies validator | Unit | Notification sent |

## Related

- [[modules/skills/skill-assessments/overview|Skill Assessments]] — feature overview
- [[code-standards/testing-strategy|Testing Standards]] — project-wide testing conventions
