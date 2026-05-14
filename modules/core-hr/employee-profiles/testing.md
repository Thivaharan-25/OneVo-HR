# Employee Profiles - Testing Strategy

**Module:** Core HR
**Feature:** Employee Profiles

---

## Unit Tests

Unit tests must exercise handlers/services through repository and service interfaces. They must not mock `IApplicationDbContext`, `DbSet<T>`, or EF Core queryables.

```csharp
public class CreateEmployeeCommandHandlerTests
{
    private readonly Mock<IEmployeeRepository> _employeeRepositoryMock = new();
    private readonly Mock<IUnitOfWork> _unitOfWorkMock = new();
    private readonly Mock<ICurrentUser> _currentUserMock = new();
    private readonly CreateEmployeeCommandHandler _sut;

    public CreateEmployeeCommandHandlerTests()
    {
        _currentUserMock.Setup(x => x.TenantId).Returns(Guid.NewGuid());

        _sut = new CreateEmployeeCommandHandler(
            _employeeRepositoryMock.Object,
            _unitOfWorkMock.Object,
            _currentUserMock.Object);
    }

    [Fact]
    public async Task Handle_ValidEmployee_ReturnsCreatedEmployee()
    {
        var command = new CreateEmployeeCommand
        {
            FirstName = "John",
            LastName = "Doe",
            Email = "john.doe@company.com",
            DepartmentId = Guid.NewGuid(),
            JobTitleId = Guid.NewGuid(),
            HireDate = DateOnly.FromDateTime(DateTime.Today)
        };

        _employeeRepositoryMock
            .Setup(x => x.EmailExistsAsync(command.Email, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);

        var result = await _sut.Handle(command, CancellationToken.None);

        result.IsSuccess.Should().BeTrue();
        _employeeRepositoryMock.Verify(x => x.AddAsync(It.IsAny<Employee>(), It.IsAny<CancellationToken>()), Times.Once);
        _unitOfWorkMock.Verify(x => x.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task Handle_DuplicateEmail_ReturnsConflict()
    {
        var command = new CreateEmployeeCommand { Email = "john@company.com" };

        _employeeRepositoryMock
            .Setup(x => x.EmailExistsAsync(command.Email, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _sut.Handle(command, CancellationToken.None);

        result.IsFailure.Should().BeTrue();
        result.Error.Code.Should().Contain("DuplicateEmail");
    }
}

public class UpdateEmployeeCommandHandlerTests
{
    private readonly Mock<IEmployeeRepository> _employeeRepositoryMock = new();
    private readonly Mock<IUnitOfWork> _unitOfWorkMock = new();
    private readonly UpdateEmployeeCommandHandler _sut;

    public UpdateEmployeeCommandHandlerTests()
    {
        _sut = new UpdateEmployeeCommandHandler(
            _employeeRepositoryMock.Object,
            _unitOfWorkMock.Object);
    }

    [Fact]
    public async Task Handle_ManagerIdCreatesCircle_ReturnsValidationFailure()
    {
        var employeeId = Guid.NewGuid();
        var managerId = Guid.NewGuid();

        _employeeRepositoryMock
            .Setup(x => x.WouldCreateManagerCycleAsync(employeeId, managerId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _sut.Handle(
            new UpdateEmployeeCommand { EmployeeId = employeeId, ManagerId = managerId },
            CancellationToken.None);

        result.IsFailure.Should().BeTrue();
        result.Error.Code.Should().Contain("ManagerCycle");
    }
}
```

## Integration Tests

Integration tests may verify persistence through the API response and repository interfaces. Direct `ApplicationDbContext`, `IApplicationDbContext`, or `DbSet<T>` access is not part of the test contract.

```csharp
public class EmployeesApiTests : IClassFixture<CustomWebApplicationFactory>
{
    private readonly HttpClient _client;
    private readonly CustomWebApplicationFactory _factory;

    public EmployeesApiTests(CustomWebApplicationFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", factory.GetTestToken("employees:read", "employees:write", "employees:delete"));
    }

    [Fact]
    public async Task CreateEmployee_ValidPayload_Returns201AndPersists()
    {
        var department = await _factory.SeedDepartmentAsync();
        var payload = new
        {
            firstName = "Integration",
            lastName = "Test",
            email = $"integration-{Guid.NewGuid():N}@test.com",
            departmentId = department.Id,
            hireDate = "2026-01-15"
        };

        var response = await _client.PostAsJsonAsync("/api/v1/employees", payload);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var body = await response.Content.ReadFromJsonAsync<EmployeeResponse>();
        body!.FirstName.Should().Be("Integration");
        body.Email.Should().Be(payload.email);

        using var scope = _factory.Services.CreateScope();
        var employees = scope.ServiceProvider.GetRequiredService<IEmployeeRepository>();
        var persisted = await employees.GetByIdAsync(body.Id, CancellationToken.None);
        persisted.Should().NotBeNull();
    }

    [Fact]
    public async Task DeleteEmployee_ExistingEmployee_Returns204AndSoftDeletes()
    {
        var employee = await _factory.SeedEmployeeAsync();

        var response = await _client.DeleteAsync($"/api/v1/employees/{employee.Id}");

        response.StatusCode.Should().Be(HttpStatusCode.NoContent);

        using var scope = _factory.Services.CreateScope();
        var employees = scope.ServiceProvider.GetRequiredService<IEmployeeRepository>();
        var deleted = await employees.GetByIdIncludingDeletedAsync(employee.Id, CancellationToken.None);
        deleted!.IsDeleted.Should().BeTrue();
    }
}
```

## Test Scenarios

| Scenario | Input | Expected Output | Type |
|:---------|:------|:----------------|:-----|
| Create valid employee | Complete DTO with valid FKs | 201 + employee persisted | Integration |
| Create with duplicate email | Email already exists in tenant | Conflict result or 409 | Unit/API |
| Create with duplicate employee number | Number already taken | Conflict result or 409 | Unit/API |
| Update with circular manager | Manager relationship forms a cycle | Validation failure | Unit |
| Soft delete active employee | Valid employee ID | 204 + `is_deleted=true` | Integration |
| Soft delete already-deleted | Deleted employee ID | Not found result or 404 | Unit/API |
| Get own profile | Authenticated customer web session | 200 + own employee data | Integration |
| Get direct reports | Manager ID with active and deleted reports | Deleted reports excluded | Unit |
| List with pagination | page and pageSize | Correct page and total count | Integration |
| Create missing required fields | Empty required field | Validation errors | Unit/API |
| Cross-tenant access | Employee from another tenant | 404 or forbidden according to endpoint contract | Integration |

## Test Data

- `CustomWebApplicationFactory` extends `WebApplicationFactory<Program>`, uses Testcontainers for PostgreSQL, seeds a default tenant, and provides helper methods like `SeedEmployeeAsync()` and `SeedDepartmentAsync()`.
- Test tokens are generated via `GetTestToken(params string[] permissions)` with permission claims scoped to the test tenant.
- Each test seeds its own data to avoid cross-test interference.
- Tests that need deleted rows use repository methods that explicitly expose deleted-row reads for verification, not direct EF query filters.

## Related

- [[modules/core-hr/employee-profiles/overview|Employee Profiles Overview]]
- [[backend/repository-persistence-boundary|Repository Persistence Boundary]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]

