# Time Off Types - Testing

**Module:** Time Off  
**Feature:** Time Off Types  
**Location:** `tests/ONEVO.Tests.Unit/Modules/TimeOff/TimeOffTypeServiceTests.cs`

---

## Unit Tests

```csharp
public class TimeOffTypeServiceTests
{
    private readonly Mock<ITimeOffTypeRepository> _repoMock = new();
    private readonly Mock<ITenantContext> _tenantMock = new();
    private readonly TimeOffTypeService _sut;

    public TimeOffTypeServiceTests()
    {
        _tenantMock.Setup(t => t.TenantId).Returns(Guid.NewGuid());
        _sut = new TimeOffTypeService(_repoMock.Object, _tenantMock.Object);
    }

    [Fact]
    public async Task CreateAsync_WithValidData_ReturnsSuccess()
    {
        var command = new CreateTimeOffTypeCommand
        {
            Name = "Annual",
            IsPaid = true,
            AllowFullDay = true,
            AllowHalfDay = true,
            AllowHourly = false
        };
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<Guid>(), "Annual", default)).ReturnsAsync(false);

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Name.Should().Be("Annual");
        _repoMock.Verify(r => r.AddAsync(It.IsAny<TimeOffType>(), default), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_WithDuplicateName_ReturnsFailure()
    {
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<Guid>(), "Annual", default)).ReturnsAsync(true);
        var command = new CreateTimeOffTypeCommand { Name = "Annual" };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("already exists");
    }

    [Fact]
    public async Task GetAllAsync_ReturnsOnlyActiveTypes()
    {
        _repoMock.Setup(r => r.GetActiveByTenantAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(new List<TimeOffType> { new() { Name = "Sick", IsActive = true } });

        var result = await _sut.GetAllAsync(default);

        result.IsSuccess.Should().BeTrue();
        result.Value.Should().HaveCount(1);
    }
}
```

## Integration Tests

```csharp
public class TimeOffTypeEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _client;

    public TimeOffTypeEndpointTests(ONEVOWebFactory factory)
    {
        _client = factory.CreateAuthenticatedClient(role: "HR_Admin");
    }

    [Fact]
    public async Task CreateTimeOffType_WithValidData_Returns201()
    {
        var command = new { Name = "Paternity", IsPaid = true, AllowFullDay = true, AllowHalfDay = false, AllowHourly = false };
        var response = await _client.PostAsJsonAsync("/api/v1/time-off/types", command);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task ListTimeOffTypes_ReturnsOnlyCurrentTenant()
    {
        var response = await _client.GetAsync("/api/v1/time-off/types");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task CreateTimeOffType_WithoutPermission_Returns403()
    {
        var employeeClient = _factory.CreateAuthenticatedClient(role: "Employee");
        var command = new { Name = "Custom", IsPaid = false };
        var response = await employeeClient.PostAsJsonAsync("/api/v1/time-off/types", command);

        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create time off type with valid data | Unit | Success, entity persisted |
| Create with duplicate name | Unit | Failure, "already exists" |
| Create with empty name | Unit | Validation failure |
| Create with unsupported policy-rule fields | Unit/API | Validation failure; approval, entitlement, carry-forward, notice, and request-limit rules belong to Time Off Policies |
| List active types only | Unit | Filters inactive |
| Tenant isolation on list | Integration | Only current tenant types |
| Permission check on create | Integration | 403 without `time_off:manage` |

## Related

- [[modules/time-off/time-off-types/overview|Time Off Types Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
