# Job Hierarchy — Testing

**Module:** Org Structure
**Feature:** Job Hierarchy
**Location:** `tests/ONEVO.Tests.Unit/Modules/OrgStructure/JobHierarchyServiceTests.cs`

---

## Unit Tests

```csharp
public class JobHierarchyServiceTests
{
    private readonly Mock<IJobHierarchyRepository> _repoMock = new();
    private readonly JobHierarchyService _sut;

    [Fact]
    public async Task Create_job_family_with_levels()
    {
        // Arrange
        // ... setup mocks for create job family with levels

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Hierarchy created
    }

    [Fact]
    public async Task Delete_used_job_title_fails()
    {
        // Arrange
        // ... setup mocks for delete used job title fails

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // 409 Conflict
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create job family with levels | Unit | Hierarchy created |
| Delete used job title fails | Unit | 409 Conflict |

## Related

- [[job-hierarchy|Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
