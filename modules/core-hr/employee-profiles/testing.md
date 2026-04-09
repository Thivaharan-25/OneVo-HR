# Employee Profiles — Testing Strategy

**Module:** Core HR
**Feature:** Employee Profiles

---

## Unit Tests

```csharp
public class EmployeeServiceTests
{
    private readonly Mock<IApplicationDbContext> _dbContextMock;
    private readonly Mock<IMediator> _mediatorMock;
    private readonly Mock<ICurrentTenantService> _tenantServiceMock;
    private readonly EmployeeService _sut;

    public EmployeeServiceTests()
    {
        _dbContextMock = new Mock<IApplicationDbContext>();
        _mediatorMock = new Mock<IMediator>();
        _tenantServiceMock = new Mock<ICurrentTenantService>();
        _tenantServiceMock.Setup(x => x.TenantId).Returns(Guid.NewGuid());

        _sut = new EmployeeService(
            _dbContextMock.Object,
            _mediatorMock.Object,
            _tenantServiceMock.Object);
    }

    [Fact]
    public async Task CreateAsync_ValidEmployee_ReturnsCreatedEmployee()
    {
        // Arrange
        var dto = new CreateEmployeeDto
        {
            FirstName = "John",
            LastName = "Doe",
            Email = "john.doe@company.com",
            DepartmentId = Guid.NewGuid(),
            JobTitleId = Guid.NewGuid(),
            HireDate = DateOnly.FromDateTime(DateTime.Today)
        };

        var employees = new List<Employee>().AsQueryable().BuildMockDbSet();
        _dbContextMock.Setup(x => x.Employees).Returns(employees.Object);

        // Act
        var result = await _sut.CreateAsync(dto, Guid.NewGuid());

        // Assert
        result.Should().NotBeNull();
        result.FirstName.Should().Be("John");
        result.LastName.Should().Be("Doe");
        _dbContextMock.Verify(x => x.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Once);
        _mediatorMock.Verify(x => x.Publish(
            It.IsAny<EmployeeCreatedEvent>(),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_DuplicateEmail_ThrowsConflictException()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        var existing = new Employee { Email = "john@company.com", TenantId = tenantId, IsDeleted = false };
        var employees = new List<Employee> { existing }.AsQueryable().BuildMockDbSet();
        _dbContextMock.Setup(x => x.Employees).Returns(employees.Object);

        var dto = new CreateEmployeeDto { Email = "john@company.com" };

        // Act
        var act = () => _sut.CreateAsync(dto, Guid.NewGuid());

        // Assert
        await act.Should().ThrowAsync<ConflictException>()
            .WithMessage("*email*already exists*");
    }

    [Fact]
    public async Task SoftDeleteAsync_ExistingEmployee_SetsIsDeletedTrue()
    {
        // Arrange
        var employeeId = Guid.NewGuid();
        var employee = new Employee
        {
            Id = employeeId,
            IsDeleted = false,
            TenantId = _tenantServiceMock.Object.TenantId
        };
        var employees = new List<Employee> { employee }.AsQueryable().BuildMockDbSet();
        _dbContextMock.Setup(x => x.Employees).Returns(employees.Object);

        // Act
        await _sut.SoftDeleteAsync(employeeId, Guid.NewGuid());

        // Assert
        employee.IsDeleted.Should().BeTrue();
        employee.TerminationDate.Should().NotBeNull();
        _mediatorMock.Verify(x => x.Publish(
            It.IsAny<EmployeeTerminatedEvent>(),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task SoftDeleteAsync_AlreadyDeleted_ThrowsNotFoundException()
    {
        // Arrange
        var employees = new List<Employee>().AsQueryable().BuildMockDbSet();
        _dbContextMock.Setup(x => x.Employees).Returns(employees.Object);

        // Act
        var act = () => _sut.SoftDeleteAsync(Guid.NewGuid(), Guid.NewGuid());

        // Assert
        await act.Should().ThrowAsync<NotFoundException>();
    }

    [Fact]
    public async Task UpdateAsync_ManagerIdCreatesCircle_ThrowsValidationException()
    {
        // Arrange
        var empA = new Employee { Id = Guid.NewGuid(), ManagerId = null, TenantId = _tenantServiceMock.Object.TenantId, IsDeleted = false };
        var empB = new Employee { Id = Guid.NewGuid(), ManagerId = empA.Id, TenantId = _tenantServiceMock.Object.TenantId, IsDeleted = false };
        var employees = new List<Employee> { empA, empB }.AsQueryable().BuildMockDbSet();
        _dbContextMock.Setup(x => x.Employees).Returns(employees.Object);

        var dto = new UpdateEmployeeDto { ManagerId = empB.Id }; // A -> B -> A = cycle

        // Act
        var act = () => _sut.UpdateAsync(empA.Id, dto, Guid.NewGuid());

        // Assert
        await act.Should().ThrowAsync<ValidationException>()
            .WithMessage("*circular*");
    }

    [Fact]
    public async Task GetDirectReportsAsync_ReturnsOnlyActiveDirectReports()
    {
        // Arrange
        var managerId = Guid.NewGuid();
        var tenantId = _tenantServiceMock.Object.TenantId;
        var reports = new List<Employee>
        {
            new() { Id = Guid.NewGuid(), ManagerId = managerId, TenantId = tenantId, IsDeleted = false },
            new() { Id = Guid.NewGuid(), ManagerId = managerId, TenantId = tenantId, IsDeleted = false },
            new() { Id = Guid.NewGuid(), ManagerId = managerId, TenantId = tenantId, IsDeleted = true } // soft-deleted
        };
        var employees = reports.AsQueryable().BuildMockDbSet();
        _dbContextMock.Setup(x => x.Employees).Returns(employees.Object);

        // Act
        var result = await _sut.GetDirectReportsAsync(managerId);

        // Assert
        result.Should().HaveCount(2);
    }
}

public class CreateEmployeeValidatorTests
{
    private readonly CreateEmployeeValidator _sut = new();

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void Validate_EmptyFirstName_Fails(string firstName)
    {
        var dto = new CreateEmployeeDto { FirstName = firstName, LastName = "Doe", Email = "a@b.com" };
        var result = _sut.Validate(dto);
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == nameof(dto.FirstName));
    }

    [Fact]
    public void Validate_InvalidEmailFormat_Fails()
    {
        var dto = new CreateEmployeeDto { FirstName = "John", LastName = "Doe", Email = "not-an-email" };
        var result = _sut.Validate(dto);
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == nameof(dto.Email));
    }

    [Fact]
    public void Validate_ValidEmployee_Passes()
    {
        var dto = new CreateEmployeeDto
        {
            FirstName = "John",
            LastName = "Doe",
            Email = "john@company.com",
            DepartmentId = Guid.NewGuid(),
            HireDate = DateOnly.FromDateTime(DateTime.Today)
        };
        var result = _sut.Validate(dto);
        result.IsValid.Should().BeTrue();
    }
}
```

---

## Integration Tests

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
        // Arrange
        var department = await _factory.SeedDepartmentAsync();
        var payload = new
        {
            firstName = "Integration",
            lastName = "Test",
            email = $"integration-{Guid.NewGuid():N}@test.com",
            departmentId = department.Id,
            hireDate = "2026-01-15"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/employees", payload);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var body = await response.Content.ReadFromJsonAsync<EmployeeResponse>();
        body!.FirstName.Should().Be("Integration");
        body.Email.Should().Be(payload.email);

        // Verify persisted
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<IApplicationDbContext>();
        var persisted = await db.Employees.FindAsync(body.Id);
        persisted.Should().NotBeNull();
    }

    [Fact]
    public async Task DeleteEmployee_ExistingEmployee_Returns204AndSoftDeletes()
    {
        // Arrange
        var employee = await _factory.SeedEmployeeAsync();

        // Act
        var response = await _client.DeleteAsync($"/api/v1/employees/{employee.Id}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NoContent);

        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<IApplicationDbContext>();
        var deleted = await db.Employees.IgnoreQueryFilters()
            .FirstOrDefaultAsync(e => e.Id == employee.Id);
        deleted!.IsDeleted.Should().BeTrue();
    }

    [Fact]
    public async Task GetEmployee_WithoutPermission_Returns403()
    {
        // Arrange
        var noPermClient = _factory.CreateClient();
        noPermClient.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", _factory.GetTestToken()); // no permissions

        // Act
        var response = await noPermClient.GetAsync($"/api/v1/employees/{Guid.NewGuid()}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }

    [Fact]
    public async Task ListEmployees_Paginated_ReturnsCorrectPage()
    {
        // Arrange
        for (int i = 0; i < 15; i++)
            await _factory.SeedEmployeeAsync();

        // Act
        var response = await _client.GetAsync("/api/v1/employees?page=1&pageSize=10");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var body = await response.Content.ReadFromJsonAsync<PagedResponse<EmployeeResponse>>();
        body!.Items.Should().HaveCount(10);
        body.TotalCount.Should().BeGreaterOrEqualTo(15);
    }
}
```

---

## Test Scenarios

| Scenario | Input | Expected Output | Type |
|:---------|:------|:----------------|:-----|
| Create valid employee | Complete DTO with valid FKs | 201 + employee persisted + EmployeeCreated event | Integration |
| Create with duplicate email | Email already exists in tenant | 409 Conflict | Unit |
| Create with duplicate employee_number | Number already taken | 409 Conflict | Unit |
| Update with circular manager | manager_id forms a cycle | 422 Validation error | Unit |
| Soft delete active employee | Valid employee ID | 204 + is_deleted=true + EmployeeTerminated event | Integration |
| Soft delete already-deleted | Deleted employee ID | 404 Not Found | Unit |
| Get own profile | Authenticated user JWT | 200 + own employee data | Integration |
| Get direct reports | Manager ID with 3 active + 1 deleted report | 200 + 3 results (excludes soft-deleted) | Unit |
| List with pagination | page=2, pageSize=5 | 200 + correct slice of data | Integration |
| Create missing required fields | Empty first_name | 400 + validation errors | Unit |
| Cross-tenant access | Employee from tenant B | 404 (tenant filter) | Integration |

---

## Test Data

- **CustomWebApplicationFactory**: Extends `WebApplicationFactory<Program>`, uses Testcontainers for PostgreSQL, seeds a default tenant, and provides helper methods like `SeedEmployeeAsync()` and `SeedDepartmentAsync()`.
- **Test tokens**: Generated via `GetTestToken(params string[] permissions)` that creates JWT with specified permission claims scoped to the test tenant.
- **Fixtures**: Each test seeds its own data to avoid cross-test interference. Tests run in parallel with separate database schemas per test class.

## Related

- [[modules/core-hr/employee-profiles/overview|Employee Profiles Overview]]
- [[code-standards/testing-strategy|Testing Standards]]
- [[database/migration-patterns|Migration Patterns]]
