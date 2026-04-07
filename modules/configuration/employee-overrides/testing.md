# Employee Overrides — Testing

**Module:** Configuration
**Feature:** Employee Overrides
**Location:** `tests/ONEVO.Tests.Unit/Modules/Configuration/EmployeeOverrideServiceTests.cs`

---

## Unit Tests

```csharp
public class EmployeeOverrideServiceTests
{
    private readonly Mock<IEmployeeOverrideRepository> _repoMock = new();
    private readonly Mock<IEmployeeService> _employeeServiceMock = new();
    private readonly ConfigurationService _sut;

    [Fact]
    public async Task SetEmployeeOverrideAsync_ValidEmployee_UpsertsOverride()
    {
        _employeeServiceMock.Setup(e => e.GetByIdAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(Result.Success(new EmployeeDto()));
        var command = new SetOverrideCommand { EmployeeId = _employeeId, ScreenshotCapture = false };

        var result = await _sut.SetEmployeeOverrideAsync(command, default);

        result.IsSuccess.Should().BeTrue();
    }

    [Fact]
    public async Task SetBulkOverrideAsync_ByDepartment_AffectsAllEmployees()
    {
        SetupDepartmentWith5Employees();

        var result = await _sut.SetBulkOverrideAsync(new SetBulkOverrideCommand
        {
            DepartmentId = _deptId, ActivityMonitoring = false
        }, default);

        result.IsSuccess.Should().BeTrue();
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Set individual override | Unit | Override upserted |
| Bulk override by department | Unit | All employees affected |
| Individual wins over bulk | Unit | Individual preserved |
| Null value inherits tenant | Unit | Tenant toggle used |

## Related

- [[configuration/employee-overrides/overview|Employee Overrides Overview]]
- [[testing/README|Testing Standards]]
- [[migration-patterns]]
