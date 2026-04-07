# Employee Lifecycle — Testing

**Module:** Core HR
**Feature:** Employee Lifecycle
**Location:** `tests/ONEVO.Tests.Unit/Modules/CoreHR/EmployeeLifecycleServiceTests.cs`

---

## Unit Tests

```csharp
public class EmployeeLifecycleServiceTests
{
    private readonly Mock<IEmployeeLifecycleRepository> _repoMock = new();
    private readonly EmployeeLifecycleService _sut;

    [Fact]
    public async Task Promote_updates_department_and_creates_lifecycle_event()
    {
        // Arrange
        // ... setup mocks for promote updates department and creates lifecycle event

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // UpdateAsync called, lifecycle event inserted
    }

    [Fact]
    public async Task Transfer_changes_department()
    {
        // Arrange
        // ... setup mocks for transfer changes department

        // Act
        // var result = await _sut.MethodAsync(command, default);

        // Assert
        // Department updated, EmployeeTransferred published
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Promote updates department and creates lifecycle event | Unit | UpdateAsync called, lifecycle event inserted |
| Transfer changes department | Unit | Department updated, EmployeeTransferred published |

## Related

- [[employee-lifecycle|Employee Lifecycle Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
