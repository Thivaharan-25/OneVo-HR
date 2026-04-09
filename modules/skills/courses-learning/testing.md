# Courses & Learning — Testing

**Module:** Skills
**Feature:** Courses & Learning
**Location:** `tests/ONEVO.Tests.Unit/Modules/Skills/CourseServiceTests.cs`

---

## Unit Tests

```csharp
public class CourseServiceTests
{
    private readonly Mock<ICourseRepository> _repoMock = new();
    private readonly CourseService _sut;

    [Fact]
    public async Task Enroll_creates_enrollment_record()
    {
        // Arrange
        // ... setup mocks for enroll creates enrollment record

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = assigned
    }

    [Fact]
    public async Task 100%_progress_marks_completed()
    {
        // Arrange
        // ... setup mocks for 100% progress marks completed

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
| Enroll creates enrollment record | Unit | Status = assigned |
| 100% progress marks completed | Unit | Status = completed |

## Related

- [[modules/skills/courses-learning/overview|Courses Learning]] — feature overview
- [[code-standards/testing-strategy|Testing Standards]] — project-wide testing conventions
