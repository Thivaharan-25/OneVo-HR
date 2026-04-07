# Grievance Cases — Testing

**Module:** Grievance
**Feature:** Grievance Cases
**Location:** `tests/ONEVO.Tests.Unit/Modules/Grievance/GrievanceServiceTests.cs`

---

## Unit Tests

```csharp
public class GrievanceServiceTests
{
    private readonly Mock<IGrievanceRepository> _repoMock = new();
    private readonly GrievanceService _sut;

    [Fact]
    public async Task File_anonymous_grievance_hides_filer()
    {
        // Arrange
        // ... setup mocks for file anonymous grievance hides filer

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // filed_by_id = null
    }

    [Fact]
    public async Task Resolve_case_updates_status()
    {
        // Arrange
        // ... setup mocks for resolve case updates status

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Status = resolved
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| File anonymous grievance hides filer | Unit | filed_by_id = null |
| Resolve case updates status | Unit | Status = resolved |

## Related

- [[grievance-cases]] — feature overview
- [[testing/README|Testing Standards]] — project-wide testing conventions
