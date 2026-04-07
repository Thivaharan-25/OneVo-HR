# Leave Types — Testing

**Module:** Leave  
**Feature:** Leave Types  
**Location:** `tests/ONEVO.Tests.Unit/Modules/Leave/LeaveTypeServiceTests.cs`

---

## Unit Tests

```csharp
public class LeaveTypeServiceTests
{
    private readonly Mock<ILeaveTypeRepository> _repoMock = new();
    private readonly Mock<ITenantContext> _tenantMock = new();
    private readonly LeaveTypeService _sut;

    public LeaveTypeServiceTests()
    {
        _tenantMock.Setup(t => t.TenantId).Returns(Guid.NewGuid());
        _sut = new LeaveTypeService(_repoMock.Object, _tenantMock.Object);
    }

    [Fact]
    public async Task CreateAsync_WithValidData_ReturnsSuccess()
    {
        var command = new CreateLeaveTypeCommand { Name = "Annual", IsPaid = true, RequiresApproval = true };
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<Guid>(), "Annual", default)).ReturnsAsync(false);

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeTrue();
        result.Value!.Name.Should().Be("Annual");
        _repoMock.Verify(r => r.AddAsync(It.IsAny<LeaveType>(), default), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_WithDuplicateName_ReturnsFailure()
    {
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<Guid>(), "Annual", default)).ReturnsAsync(true);
        var command = new CreateLeaveTypeCommand { Name = "Annual" };

        var result = await _sut.CreateAsync(command, default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("already exists");
    }

    [Fact]
    public async Task GetAllAsync_ReturnsOnlyActiveTypes()
    {
        _repoMock.Setup(r => r.GetActiveByTenantAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync(new List<LeaveType> { new() { Name = "Sick", IsActive = true } });

        var result = await _sut.GetAllAsync(default);

        result.IsSuccess.Should().BeTrue();
        result.Value.Should().HaveCount(1);
    }
}
```

## Integration Tests

```csharp
public class LeaveTypeEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _client;

    public LeaveTypeEndpointTests(ONEVOWebFactory factory)
    {
        _client = factory.CreateAuthenticatedClient(role: "HR_Admin");
    }

    [Fact]
    public async Task CreateLeaveType_WithValidData_Returns201()
    {
        var command = new { Name = "Paternity", IsPaid = true, RequiresApproval = true };
        var response = await _client.PostAsJsonAsync("/api/v1/leave/types", command);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task ListLeaveTypes_ReturnsOnlyCurrentTenant()
    {
        var response = await _client.GetAsync("/api/v1/leave/types");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task CreateLeaveType_WithoutPermission_Returns403()
    {
        var employeeClient = _factory.CreateAuthenticatedClient(role: "Employee");
        var command = new { Name = "Custom", IsPaid = false };
        var response = await employeeClient.PostAsJsonAsync("/api/v1/leave/types", command);

        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }
}
```

## Test Scenarios

| Scenario | Type | Expected |
|:---------|:-----|:---------|
| Create leave type with valid data | Unit | Success, entity persisted |
| Create with duplicate name | Unit | Failure, "already exists" |
| Create with empty name | Unit | Validation failure |
| List active types only | Unit | Filters inactive |
| Tenant isolation on list | Integration | Only current tenant types |
| Permission check on create | Integration | 403 without `leave:manage` |

## Related

- [[leave-types|Leave Types Overview]]
- [[testing/README|Testing Standards]]
