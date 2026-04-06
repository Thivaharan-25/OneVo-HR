# Testing Strategy: ONEVO

## Test Pyramid

```
         ┌─────────┐
         │  E2E    │  Playwright (Phase 2, with frontend)
         ├─────────┤
        │ Contract │  Pact (module API contracts)
        ├──────────┤
       │ Integration│  xUnit + Testcontainers (real PostgreSQL + Redis)
       ├────────────┤
      │    Unit     │  xUnit + Moq + FluentAssertions (80%+ coverage)
      ├──────────────┤
     │  Architecture │  ArchUnitNET (boundary enforcement)
     └───────────────┘
```

## Test Types

### Unit Tests (Services, Validators, Handlers)

- **Framework:** xUnit
- **Mocking:** Moq
- **Assertions:** FluentAssertions
- **Coverage target:** 80%+ for all services
- **Location:** `tests/ONEVO.Tests.Unit/Modules/{ModuleName}/`

```csharp
public class EmployeeServiceTests
{
    private readonly Mock<IEmployeeRepository> _repoMock = new();
    private readonly Mock<ITenantContext> _tenantMock = new();
    private readonly EmployeeService _sut;

    public EmployeeServiceTests()
    {
        _tenantMock.Setup(t => t.TenantId).Returns(Guid.NewGuid());
        _sut = new EmployeeService(_repoMock.Object, _tenantMock.Object);
    }

    [Fact]
    public async Task GetByIdAsync_WhenEmployeeExists_ReturnsSuccess()
    {
        // Arrange
        var employeeId = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByIdAsync(employeeId, default))
            .ReturnsAsync(new Employee { Id = employeeId, FirstName = "John" });

        // Act
        var result = await _sut.GetByIdAsync(employeeId, default);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value!.FirstName.Should().Be("John");
    }

    [Fact]
    public async Task GetByIdAsync_WhenNotFound_ReturnsFailure()
    {
        _repoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), default))
            .ReturnsAsync((Employee?)null);

        var result = await _sut.GetByIdAsync(Guid.NewGuid(), default);

        result.IsSuccess.Should().BeFalse();
        result.Error!.Message.Should().Contain("not found");
    }
}
```

### Integration Tests (API + Database)

- **Framework:** xUnit + WebApplicationFactory
- **Database:** Testcontainers (real PostgreSQL in Docker)
- **Location:** `tests/ONEVO.Tests.Integration/`

```csharp
public class EmployeeEndpointTests : IClassFixture<ONEVOWebFactory>
{
    private readonly HttpClient _client;

    public EmployeeEndpointTests(ONEVOWebFactory factory)
    {
        _client = factory.CreateAuthenticatedClient(tenantId: TestTenants.Default, role: "HR_Admin");
    }

    [Fact]
    public async Task CreateEmployee_WithValidData_Returns201()
    {
        var command = new { FirstName = "John", LastName = "Doe", Email = "john@test.com" };
        var response = await _client.PostAsJsonAsync("/api/v1/employees", command);
        
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
    }

    [Fact]
    public async Task GetEmployees_AsDifferentTenant_ReturnsEmpty()
    {
        // Employees from another tenant should NOT be visible
        var otherTenantClient = _factory.CreateAuthenticatedClient(tenantId: TestTenants.Other);
        var response = await otherTenantClient.GetAsync("/api/v1/employees");
        
        var result = await response.Content.ReadFromJsonAsync<PagedResult<EmployeeDto>>();
        result!.Data.Should().BeEmpty(); // Tenant isolation verified
    }
}
```

### Architecture Tests (ArchUnitNET)

- **Location:** `tests/ONEVO.Tests.Architecture/`
- **Purpose:** Enforce module boundaries, naming conventions, dependency rules

```csharp
public class ModuleBoundaryTests
{
    private static readonly Architecture Architecture = new ArchLoader()
        .LoadAssemblies(typeof(Program).Assembly)
        .Build();

    [Fact]
    public void Modules_Should_Not_Have_Circular_Dependencies()
    {
        Slices().Matching("ONEVO.Modules.(*)")
            .Should().BeFreeOfCycles()
            .Check(Architecture);
    }

    [Fact]
    public void Internal_Types_Should_Not_Be_Accessed_From_Outside()
    {
        Types().That().ResideInNamespace("*.Internal.*", true)
            .Should().NotBePublic()
            .Check(Architecture);
    }

    [Fact]
    public void All_Entities_Should_Inherit_BaseEntity()
    {
        Classes().That().HaveNameEndingWith("Entity").Or().ResideInNamespace("*.Entities")
            .Should().BeAssignableTo(typeof(BaseEntity))
            .Check(Architecture);
    }
}
```

## Test Naming Convention

```
{MethodName}_{Scenario}_{ExpectedResult}

Examples:
GetByIdAsync_WhenEmployeeExists_ReturnsSuccess
ApproveLeaveRequest_WhenAlreadyApproved_ReturnsFailure
CreateEmployee_WithMissingFirstName_Returns422
```

## Running Tests

```bash
# All tests
dotnet test

# Unit tests only
dotnet test --filter "Category=Unit"

# Integration tests only (requires Docker)
dotnet test --filter "Category=Integration"

# Architecture tests
dotnet test --filter "Category=Architecture"

# With coverage report
dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
```

## CI Pipeline Test Gates

| Gate | Threshold | Blocks Deploy? |
|:-----|:----------|:--------------|
| Unit tests pass | 100% | Yes |
| Integration tests pass | 100% | Yes |
| Architecture tests pass | 100% | Yes |
| Code coverage | ≥ 80% | Yes (warning at 70%) |

## Related

- [[module-boundaries]] — ArchUnitNET boundary enforcement tests
- [[coding-standards]] — naming conventions for tests
- [[ci-cd-pipeline]] — test execution in CI pipeline
- [[multi-tenancy]] — tenant isolation integration tests
- [[shared-kernel]] — BaseEntity, Result<T> used in test assertions
